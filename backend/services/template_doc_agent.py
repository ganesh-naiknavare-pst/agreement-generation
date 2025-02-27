from helpers.email_helper import send_email_with_attachment
from helpers.websocket_helper import listen_for_approval, ApprovalTimeoutError
from langchain.agents import initialize_agent, Tool, AgentType
from helpers.template_based_agreement_generator import llm, memory, template_graph
from prompts import  AGENT_PREFIX
from helpers.state_manager import template_agreement_state
from fastapi import HTTPException
import os
from pydantic import BaseModel

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
        description="Generate a rental agreement PDF from the provided details. Output only the agreement text.",
    )
]

def delete_temp_file():
    """Deletes the temporary agreement file if it exists."""
    try:
        if template_agreement_state.pdf_file_path and os.path.exists(template_agreement_state.pdf_file_path):
            os.remove(template_agreement_state.pdf_file_path)
            print(f"Temporary file deleted: {template_agreement_state.pdf_file_path}")
        else:
            print(f"Temp file not found: {template_agreement_state.pdf_file_path}")
    except Exception as e:
        print(f"Error deleting temp file: {str(e)}")

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

async def template_based_agreement(req: TemplateAgreementRequest):
    try:
        
        try:
            response = agent.run(req.user_prompt)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating agreement: {str(e)}")

        authority_success, _ = send_email_with_attachment(req.authority_email, template_agreement_state.pdf_file_path, "Authority", True)
        participent_success, _ = send_email_with_attachment(req.participent_email, template_agreement_state.pdf_file_path, "Participent", True)
        template_agreement_state.is_pdf_generated = True

        if authority_success and participent_success:
            delete_temp_file()
            try:
                # Wait for approvals
                approved = await listen_for_approval(timeout_seconds=300, is_template=True)
                if approved:
                    final_response = agent.run(req.user_prompt)
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
