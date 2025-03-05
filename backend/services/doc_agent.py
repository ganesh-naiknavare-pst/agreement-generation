import logging
import shutil
import os
from helpers.email_helper import send_email_with_attachment
from helpers.websocket_helper import listen_for_approval, ApprovalTimeoutError
from langchain.agents import initialize_agent, Tool, AgentType
from helpers.rent_agreement_generator import create_pdf, agreement_state
from helpers.rent_agreement_generator import llm, memory, graph
from templates import format_agreement_details
from helpers.state_manager import agreement_state
from fastapi import HTTPException
from pydantic import BaseModel
import os
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from constants import MAX_RETRIES, RETRY_DELAY
from datetime import datetime
import base64
from prisma import Base64
from langchain_core.prompts.prompt import PromptTemplate
from prompts import template

logging.basicConfig(level=logging.INFO)


class AgreementRequest(BaseModel):
    owner_name: str
    owner_email: str
    owner_signature: str
    owner_photo: str
    tenant_details: list[dict]
    property_address: str
    city: str
    rent_amount: str
    start_date: datetime


def run_agreement_tool(user_input: str) -> str:
    output = None
    for event in graph.stream({"messages": ("user", user_input)}):
        if "create_pdf" in event:
            output = event["create_pdf"]["messages"]
            return output
    return "Failed to generate agreement"


# Define Tool
tools = [
    Tool(
        name="generate_agreement",
        func=run_agreement_tool,
        description="Generate a rental agreement PDF from the provided details. Output only the agreement text.",
    )
]


def delete_temp_file():
    """Deletes the temporary agreement file if it exists."""
    try:
        if agreement_state.pdf_file_path and os.path.exists(
            agreement_state.pdf_file_path
        ):
            os.remove(agreement_state.pdf_file_path)
            logging.info(f"Temporary file deleted: {agreement_state.pdf_file_path}")
        else:
            logging.info(f"Temp file not found: {agreement_state.pdf_file_path}")
    except Exception as e:
        logging.info(f"Error deleting temp file: {str(e)}")


def save_base64_image(photo_data: str, user_id: str, is_signature: bool = False) -> str:
    if photo_data.startswith("data:image/jpeg;base64,"):
        photo_data = photo_data.replace("data:image/jpeg;base64,", "")
        photo_bytes = base64.b64decode(photo_data)
        save_dir = "./utils"
        os.makedirs(save_dir, exist_ok=True)

        if is_signature:
            photo_path = f"{save_dir}/{user_id}_signature.jpg"
        else:
            photo_path = f"{save_dir}/{user_id}_photo.jpg"

        with open(photo_path, "wb") as photo_file:
            photo_file.write(photo_bytes)
        return photo_path
    return ""


# Initialize agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
    handle_parsing_errors=True,
    max_iterations=1,
    early_stopping_method="generate",
    prompt=PromptTemplate.from_template(template),
)


def log_before_retry(retry_state):
    attempt = retry_state.attempt_number
    logging.info(f"Retry attempt {attempt}: Retrying agreement generation...")
    delete_temp_file()


def log_after_failure(retry_state):
    exception = retry_state.outcome.exception()
    logging.info(
        f"Agreement generation failed after {retry_state.attempt_number} attempts : {str(exception)}"
    )


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_fixed(RETRY_DELAY),
    retry=retry_if_exception_type(Exception),
    before_sleep=log_before_retry,
    after=log_after_failure,
)
def generate_agreement_with_retry(agreement_details):
    return agent.invoke(agreement_details)


async def create_agreement_details(
    request: AgreementRequest, agreement_id: int, db: object
):
    try:
        # Reset agreement state for fresh request
        agreement_state.reset()
        # Store owner information
        agreement_state.owner_photo = save_base64_image(
            request.owner_photo, request.owner_name
        )
        agreement_state.set_owner(request.owner_name, request.owner_email)

        agreement_state.owner_signature = save_base64_image(
            request.owner_signature, request.owner_name, is_signature=True
        )
        # Store tenant details
        tenants = []
        for tenant in request.tenant_details:
            tenant_photo_path = save_base64_image(
                tenant.get("photo", ""), tenant["name"]
            )
            tenant_signature_path = save_base64_image(
                tenant.get("signature", ""), tenant["name"], is_signature=True
            )
            tenant_id = agreement_state.add_tenant(
                tenant["email"],
                tenant["name"],
                tenant_signature_path,
                tenant_photo_path,
            )
            tenants.append((tenant_id, tenant["email"]))

        # Format agreement details
        agreement_details = format_agreement_details(
            owner_name=request.owner_name,
            tenant_details=request.tenant_details,
            property_address=request.property_address,
            city=request.city,
            rent_amount=request.rent_amount,
            start_date=request.start_date,
        )

        try:
            response = generate_agreement_with_retry(agreement_details)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating agreement after {MAX_RETRIES} attempts: {str(e)}",
            )

        owner_success, _ = send_email_with_attachment(
            request.owner_email, agreement_state.pdf_file_path, "owner", False
        )
        tenant_successes = []
        for tenant_id, tenant_email in tenants:
            success, _ = send_email_with_attachment(
                tenant_email, agreement_state.pdf_file_path, "tenant", False, tenant_id
            )
            tenant_successes.append(success)
        agreement_state.is_pdf_generated = True

        if owner_success and all(tenant_successes):
            delete_temp_file()
            try:
                # Wait for approvals
                approved = await listen_for_approval(
                    timeout_seconds=300, is_template=False
                )
                if approved:
                    # Mark as approved and generate final PDF with signatures
                    agreement_state.owner_approved = True
                    for tenant_id in agreement_state.tenants:
                        agreement_state.tenants[tenant_id] = True
                    # Generate final PDF with signatures and get the path
                    create_pdf(agreement_state)
                    final_pdf_path = agreement_state.pdf_file_path

                    # Send final agreement with replaced signatures/photos
                    owner_success, _ = send_email_with_attachment(
                        request.owner_email, final_pdf_path, "owner", False
                    )
                    for tenant_id, tenant_email in tenants:
                        send_email_with_attachment(
                            tenant_email, final_pdf_path, "tenant", False, tenant_id
                        )
                    with open(agreement_state.pdf_file_path, "rb") as pdf_file:
                        pdf_base64 = Base64.encode(pdf_file.read())
                    await db.agreement.update(
                        where={"id": agreement_id},
                        data={"pdf": pdf_base64, "status": "APPROVED"},
                    )
                    delete_temp_file()
                    if os.path.exists("./utils"):
                        shutil.rmtree("./utils")
                    return {
                        "message": "Final signed agreement with signatures sent to all parties!"
                    }
                else:
                    await db.agreement.update(
                        where={"id": agreement_id},
                        data={"status": "REJECTED"},
                    )
                    return {
                        "message": "Agreement was rejected or approval process failed."
                    }
            except ApprovalTimeoutError:
                return {
                    "message": "Approval process timed out. Please try again later."
                }
        else:
            return {"message": "Error sending initial agreement emails."}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )
