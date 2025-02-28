import logging
from helpers.email_helper import send_email_with_attachment
from helpers.websocket_helper import listen_for_approval, ApprovalTimeoutError
from langchain.agents import initialize_agent, Tool, AgentType
from helpers.rent_agreement_generator import llm, memory, graph
from prompts import  AGENT_PREFIX
from templates import  format_agreement_details
from helpers.state_manager import  agreement_state
from fastapi import HTTPException
from pydantic import BaseModel
import os
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from constants import MAX_RETRIES, RETRY_DELAY

logging.basicConfig(level=logging.INFO)

class AgreementRequest(BaseModel):
    owner_name: str
    owner_email: str
    tenant_details: list[dict]
    property_address: str
    city: str
    rent_amount: str
    start_date: str

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
        if agreement_state.pdf_file_path and os.path.exists(agreement_state.pdf_file_path):
            os.remove(agreement_state.pdf_file_path)
            logging.info(f"Temporary file deleted: {agreement_state.pdf_file_path}")
        else:
             logging.info(f"Temp file not found: {agreement_state.pdf_file_path}")
    except Exception as e:
         logging.info(f"Error deleting temp file: {str(e)}")

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
    agent_kwargs=AGENT_PREFIX,
)

def log_before_retry(retry_state):
    attempt = retry_state.attempt_number
    logging.info(f"Retry attempt {attempt}: Retrying agreement generation...")
    delete_temp_file()

def log_after_failure(retry_state):
    exception = retry_state.outcome.exception()
    logging.info(f"Agreement generation failed after {retry_state.attempt_number} attempts : {str(exception)}")
    
@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_fixed(RETRY_DELAY),
    retry=retry_if_exception_type(Exception),
    before_sleep=log_before_retry,
    after=log_after_failure
)
def generate_agreement_with_retry(agreement_details):
    return agent.run(agreement_details)

async def create_agreement_details(request: AgreementRequest):
    try:
        # Store owner information
        agreement_state.set_owner(request.owner_name)

        # Store tenant details
        tenants = []
        for tenant in request.tenant_details:
            tenant_id = agreement_state.add_tenant(tenant["email"], tenant["name"], tenant.get("signature"))
            tenants.append((tenant_id, tenant["email"]))

        # Format agreement details
        agreement_details = format_agreement_details(
            owner_name=request.owner_name,
            tenant_details=request.tenant_details,
            property_address=request.property_address,
            city=request.city,
            rent_amount=request.rent_amount,
            start_date=request.start_date
        )

        # Generate initial agreement
        try:
            response = generate_agreement_with_retry(agreement_details)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating agreement after {MAX_RETRIES} attempts: {str(e)}")

        # Send initial agreement emails
        owner_success, _ = send_email_with_attachment(request.owner_email, agreement_state.pdf_file_path, "owner")
        tenant_successes = []
        for tenant_id, tenant_email in tenants:
            success, _ = send_email_with_attachment(tenant_email, agreement_state.pdf_file_path, "tenant", tenant_id)
            tenant_successes.append(success)
        agreement_state.is_pdf_generated = True

        if owner_success and all(tenant_successes):
            delete_temp_file()
            try:
                # Wait for approvals
                approved = await listen_for_approval(timeout_seconds=300)
                if approved:
                    try:
                        final_response = generate_agreement_with_retry(agreement_details)
                    except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error generating final agreement after {MAX_RETRIES} attempts: {str(e)}")
                    # Send final agreement emails
                    owner_success, _ = send_email_with_attachment(request.owner_email, agreement_state.pdf_file_path, "owner")
                    for tenant_id, tenant_email in tenants:
                        send_email_with_attachment(tenant_email, agreement_state.pdf_file_path, "tenant", tenant_id)
                    delete_temp_file()
                    return {"message": "Final signed agreement sent to all parties!"}
                else:
                    return {"message": "Agreement was rejected or approval process failed."}
            except ApprovalTimeoutError:
                return {"message": "Approval process timed out. Please try again later."}
        else:
            return {"message": "Error sending initial agreement emails."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
