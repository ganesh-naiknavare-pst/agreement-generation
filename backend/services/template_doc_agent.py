# template_doc_agent.py
import logging
from helpers.email_helper import send_email_with_attachment
from helpers.websocket_helper import (
    listen_for_approval,
    ApprovalTimeoutError,
    ConnectionClosedError,
    ApprovalResult,
)
from langchain.agents import initialize_agent, Tool, AgentType
from helpers.template_based_agreement_generator import (
    llm,
    memory,
    template_graph,
    update_pdf_with_signatures,
)
from prompts import template
from helpers.state_manager import template_agreement_state
from fastapi import HTTPException
import os
from pydantic import BaseModel
import shutil
import os
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from constants import MAX_RETRIES, RETRY_DELAY
from langchain_core.prompts.prompt import PromptTemplate
from prisma import Base64
from prisma.enums import AgreementStatus


logging.basicConfig(level=logging.INFO)


class TemplateAgreementRequest(BaseModel):
    user_prompt: str
    authority_email: str
    participant_email: str


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
            logging.info(
                f"Temporary file deleted: {template_agreement_state.pdf_file_path}"
            )
        else:
            logging.info(
                f"Temp file not found: {template_agreement_state.pdf_file_path}"
            )
    except Exception as e:
        logging.info(f"Error deleting temp file: {str(e)}")


def delete_template_file():
    """Deletes the template agreement file if it exists."""
    try:
        if template_agreement_state.template_file_path and os.path.exists(
            template_agreement_state.template_file_path
        ):
            os.remove(template_agreement_state.template_file_path)
            logging.info(
                f"Template file deleted: {template_agreement_state.template_file_path}"
            )
        else:
            logging.info(
                f"Template file not found: {template_agreement_state.template_file_path}"
            )
    except Exception as e:
        logging.info(f"Error deleting template file: {str(e)}")


# Initialize agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
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


async def template_based_agreement(
    req: TemplateAgreementRequest, file, agreement_id: int, db: object
):
    try:
        template_agreement_state.agreement_id = agreement_id
        template_agreement_state.set_authority(req.authority_email)
        template_agreement_state.set_participant(req.participant_email)
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
            await db.templateagreement.update(
                where={"id": agreement_id},
                data={"status": AgreementStatus.FAILED},
            )
            raise HTTPException(
                status_code=500, detail=f"Error generating agreement: {str(e)}"
            )


        authority_success, _ = send_email_with_attachment(
            req.authority_email,
            template_agreement_state.pdf_file_path,
            "Authority",
            True,
        )
        participant_success, _ = send_email_with_attachment(
            req.participant_email,
            template_agreement_state.pdf_file_path,
            "Participant",
            True,
        )
        template_agreement_state.is_pdf_generated = True

        if authority_success and participant_success:
            delete_temp_file()
            delete_template_file()
            try:
                # Wait for approvals
                approval_result = await listen_for_approval(
                    timeout_seconds=300, is_template=True
                )
                
                if approval_result == ApprovalResult.APPROVED:
                    update_pdf_with_signatures()
                    # Send final agreement emails
                    authority_success, _ = send_email_with_attachment(
                        req.authority_email,
                        template_agreement_state.pdf_file_path,
                        "Authority",
                        True,
                    )
                    participant_success, _ = send_email_with_attachment(
                        req.participant_email,
                        template_agreement_state.pdf_file_path,
                        "Participant",
                        True,
                    )
                    with open(template_agreement_state.pdf_file_path, "rb") as pdf_file:
                        pdf_base64 = Base64.encode(pdf_file.read())
                    await db.templateagreement.update(
                        where={"id": agreement_id},
                        data={"pdf": pdf_base64, "status": AgreementStatus.APPROVED},
                    )
                    delete_temp_file()
                    template_agreement_state.reset()
                    return {"message": "Final signed agreement sent to all parties!"}
                elif approval_result == ApprovalResult.REJECTED:
                    # If explicitly rejected
                    await db.templateagreement.update(
                        where={"id": agreement_id},
                        data={"status": AgreementStatus.REJECTED},
                    )
                    return {
                        "message": "Agreement was rejected by one or more parties."
                    }
                else:  # ApprovalResult.CONNECTION_CLOSED
                    await db.templateagreement.update(
                        where={"id": agreement_id},
                        data={"status": AgreementStatus.FAILED},
                    )
                    return {
                        "message": "Agreement process failed due to connection issues."
                    }
            except ApprovalTimeoutError:
                # If timeout occurs (no response within time limit)
                await db.templateagreement.update(
                    where={"id": agreement_id},
                    data={"status": AgreementStatus.FAILED},
                )
                return {
                    "message": "Agreement approval process timed out. No response received within the time limit."
                }
            except ConnectionClosedError as e:
                # If connection was closed unexpectedly
                await db.templateagreement.update(
                    where={"id": agreement_id},
                    data={"status": AgreementStatus.FAILED},
                )
                return {
                    "message": f"Agreement process failed: {str(e)}"
                }
        else:
            await db.templateagreement.update(
                where={"id": agreement_id},
                data={"status": AgreementStatus.FAILED},
            )
            return {"message": "Error sending initial agreement emails."}
    except Exception as e:
        await db.templateagreement.update(
            where={"id": agreement_id},
            data={"status": AgreementStatus.FAILED},
        )
        raise HTTPException(status_code=500, detail=str(e))
