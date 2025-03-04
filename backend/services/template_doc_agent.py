import logging
from helpers.email_helper import send_email_with_attachment
from helpers.websocket_helper import listen_for_approval, ApprovalTimeoutError
from langchain.agents import initialize_agent, Tool, AgentType
from helpers.template_based_agreement_generator import llm, memory, template_graph, update_pdf_with_signatures
from prompts import  AGENT_PREFIX
from helpers.state_manager import template_agreement_state
from fastapi import HTTPException
import os
from pydantic import BaseModel
import shutil
import os
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from constants import MAX_RETRIES, RETRY_DELAY

logging.basicConfig(level=logging.INFO)

class TemplateAgreementRequest(BaseModel):
    user_prompt: str
    authority_email: str
    participent_email: str


def run_agreement_tool(user_input: str) -> str:
    output = None
    for event in template_graph.stream({"messages": ("user", user_input)}):
        if "create_pdf" in event:
            output = event["create_pdf"]["messages"]
            return output
    return "Failed to generate agreement"

# Define Tool
tools = [
    Tool(
        name="generate_agreement",
        func=run_agreement_tool,
        description="Generate a agreement PDF from the provided details. Output only the agreement text.",
    )
]

def delete_temp_file():
    """Deletes the temporary agreement file if it exists."""
    try:
        if template_agreement_state.pdf_file_path and os.path.exists(
            template_agreement_state.pdf_file_path
        ):
            os.remove(template_agreement_state.pdf_file_path)
            logging.info(f"Temporary file deleted: {template_agreement_state.pdf_file_path}")
        else:
            logging.info(f"Temp file not found: {template_agreement_state.pdf_file_path}")
    except Exception as e:
        logging.info(f"Error deleting temp file: {str(e)}")
        
def delete_template_file():
    """Deletes the template agreement file if it exists."""
    try:
        if template_agreement_state.template_file_path and os.path.exists(
            template_agreement_state.template_file_path
        ):
            os.remove(template_agreement_state.template_file_path)
            logging.info(f"Template file deleted: {template_agreement_state.template_file_path}")
        else:
            logging.info(f"Template file not found: {template_agreement_state.template_file_path}")
    except Exception as e:
        logging.info(f"Error deleting template file: {str(e)}")

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

async def template_based_agreement(req: TemplateAgreementRequest, file):
    try:

        secure_filename = os.path.basename(file.filename)
        base_dir = os.path.join(os.path.dirname(__file__), "temp")
        os.makedirs(base_dir, exist_ok=True)
        temp_file_path = os.path.join(base_dir, secure_filename)
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        template_agreement_state.template_file_path = temp_file_path
        print(f"Template file path: {template_agreement_state.template_file_path}")
        try:
            response = generate_agreement_with_retry(req.user_prompt)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating agreement: {str(e)}")

        authority_success, _ = send_email_with_attachment(req.authority_email, template_agreement_state.pdf_file_path, "Authority", True)
        participent_success, _ = send_email_with_attachment(req.participent_email, template_agreement_state.pdf_file_path, "Participent", True)
        template_agreement_state.is_pdf_generated = True

        if authority_success and participent_success:
            # delete_temp_file()
            delete_template_file()
            try:
                # Wait for approvals
                approved = await listen_for_approval(timeout_seconds=300, is_template=True)
                if approved:
                    update_pdf_with_signatures()
                    # Send final agreement emails
                    authority_success, _ = send_email_with_attachment(req.authority_email, template_agreement_state.pdf_file_path, "Authority", True)
                    participent_success, _ = send_email_with_attachment(req.participent_email, template_agreement_state.pdf_file_path, "Participent", True)
                    delete_temp_file()
                    return {"message": "Final signed agreement sent to all parties!"}
                else:
                    return {"message": "Agreement was rejected or approval process failed."}
            except ApprovalTimeoutError:
                return {"message": "Approval process timed out. Please try again later."}
        else:
            return {"message": "Error sending initial agreement emails."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
