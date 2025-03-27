import logging
import shutil
import os
from helpers.db_operations import create_user_agreement_status, update_agreement_status, store_final_pdf
from helpers.email_helper import send_email_with_attachment
from helpers.websocket_helper import (
    listen_for_approval,
    ConnectionClosedError,
    ApprovalResult,
)
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
from prisma.enums import AgreementStatus
from typing import List, Dict
from prompts import PREFIX, FORMAT_INSTRUCTIONS, SUFFIX
logging.basicConfig(level=logging.INFO)

class AgreementRequest(BaseModel):
    owner_name: str
    owner_email: str
    tenant_details: list[dict]
    property_address: str
    city: str
    rent_amount: int
    agreement_period: list[datetime]
    owner_address: str
    furnishing_type: str
    security_deposit: int
    bhk_type: str
    area: int
    registration_date: str
    furniture_and_appliances: List[Dict[str, str]]
    amenities: List[str]


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
        file_ext = "jpg"
        photo_data = photo_data.replace("data:image/jpeg;base64,", "")
    elif photo_data.startswith("data:image/png;base64,"):
        file_ext = "png"
        photo_data = photo_data.replace("data:image/png;base64,", "")
    else:
        return ""

    photo_bytes = base64.b64decode(photo_data)
    save_dir = "./utils"
    os.makedirs(save_dir, exist_ok=True)

    if is_signature:
        photo_path = f"{save_dir}/{user_id}_signature.{file_ext}"
    else:
        photo_path = f"{save_dir}/{user_id}_photo.{file_ext}"

    with open(photo_path, "wb") as photo_file:
        photo_file.write(photo_bytes)

    return photo_path

from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            " You are a helpful assistant to Generate a rental agreement from the provided details. Output only the agreement text",
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# Initialize agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    memory=None,
    max_iterations=3,
    early_stopping_method="generate",
    agent_kwargs={
        "prefix": PREFIX,
        "format_instructions": FORMAT_INSTRUCTIONS,
        "suffix": SUFFIX,
        "prompt": prompt,
    },
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
        agreement_state.set_owner(request.owner_name, request.owner_email)

        agreement_state.agreement_id = agreement_id

        # Store tenant details
        tenants = []
        for tenant in request.tenant_details:
            tenant_id = agreement_state.add_tenant(
                tenant["email"],
                tenant["name"],
            )
            tenants.append((tenant_id, tenant["email"]))

        # Format agreement details
        agreement_details = format_agreement_details(
            owner_name=request.owner_name,
            tenant_details=request.tenant_details,
            property_address=request.property_address,
            city=request.city,
            rent_amount=request.rent_amount,
            agreement_period=[date.isoformat() for date in request.agreement_period],
            owner_address=request.owner_address,
            furnishing_type=request.furnishing_type,
            security_deposit=request.security_deposit,
            bhk_type=request.bhk_type,
            area=request.area,
            registration_date=request.registration_date,
            furniture_and_appliances=request.furniture_and_appliances,
            amenities=request.amenities,
        )

        try:
            response = generate_agreement_with_retry(agreement_details)
        except Exception as e:
            await update_agreement_status(db, agreement_id, AgreementStatus.FAILED)
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
                approval_result = await listen_for_approval(
                    timeout_seconds=300, is_template=False
                )

                if approval_result == ApprovalResult.APPROVED:
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
                    # Stores final agreement pdf in db
                    await store_final_pdf(db, agreement_id, agreement_state.pdf_file_path)
                    delete_temp_file()
                    if os.path.exists("./utils"):
                        shutil.rmtree("./utils")
                    agreement_state.reset()
                    return {
                        "message": "Final signed agreement with signatures sent to all parties!"
                    }
                elif approval_result == ApprovalResult.REJECTED:
                    # If explicitly rejected
                    await update_agreement_status(db, agreement_id, AgreementStatus.REJECTED)
                    await create_user_agreement_status(db, agreement_state.owner_id, agreement_id, AgreementStatus.REJECTED)
                    for tenant_id, _ in tenants:
                        await create_user_agreement_status(db, tenant_id, agreement_id, AgreementStatus.REJECTED)

                    delete_temp_file()
                    if os.path.exists("./utils"):
                        shutil.rmtree("./utils")
                    agreement_state.reset()
                    return {"message": "Agreement was rejected by one or more parties."}

                elif approval_result == ApprovalResult.EXPIRED:
                    # ApprovalResult.EXPIRED
                    await update_agreement_status(db, agreement_id, AgreementStatus.EXPIRED)
                    await create_user_agreement_status(db, agreement_state.owner_id, agreement_id, AgreementStatus.EXPIRED)
                    for tenant_id, _ in tenants:
                        await create_user_agreement_status(db, tenant_id, agreement_id, AgreementStatus.EXPIRED)

                    delete_temp_file()
                    if os.path.exists("./utils"):
                        shutil.rmtree("./utils")
                    agreement_state.reset()
                    return {
                        "message": "Agreement was expired due to no action taken by one or more parties within 5 minutes."
                    }

                else:
                    # ApprovalResult.CONNECTION_CLOSED
                    await update_agreement_status(db, agreement_id, AgreementStatus.FAILED)
                    await create_user_agreement_status(db, agreement_state.owner_id, agreement_id, AgreementStatus.FAILED)
                    for tenant_id, _ in tenants:
                        await create_user_agreement_status(db, tenant_id, agreement_id, AgreementStatus.FAILED)

                    delete_temp_file()
                    if os.path.exists("./utils"):
                        shutil.rmtree("./utils")
                    agreement_state.reset()
                    return {
                        "message": "Agreement process failed due to connection issues."
                    }

            except ConnectionClosedError as e:
                # Update status to FAILED on connection closed
                await update_agreement_status(db, agreement_id, AgreementStatus.FAILED)
                await create_user_agreement_status(db, agreement_state.owner_id, agreement_id, AgreementStatus.FAILED)
                for tenant_id, _ in tenants:
                    await create_user_agreement_status(db, tenant_id, agreement_id, AgreementStatus.FAILED)

                delete_temp_file()
                if os.path.exists("./utils"):
                    shutil.rmtree("./utils")
                agreement_state.reset()
                return {
                    "message": "Agreement process failed: Connection closed unexpectedly"
                }
        else:
            await update_agreement_status(db, agreement_id, AgreementStatus.FAILED)
            return {"message": "Error sending initial agreement emails."}

    except Exception as e:
        await update_agreement_status(db, agreement_id, AgreementStatus.FAILED)
        await create_user_agreement_status(db, agreement_state.owner_id, agreement_id, AgreementStatus.FAILED)
        for tenant_id, _ in tenants:
            await create_user_agreement_status(db, tenant_id, agreement_id, AgreementStatus.FAILED)
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )
