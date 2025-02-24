import pypandoc
import base64
import requests
import asyncio
import websockets
import json
from typing import Annotated
from typing_extensions import TypedDict
from pypdf import PdfReader
from langchain.chat_models import ChatOpenAI
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from pypandoc.pandoc_download import download_pandoc
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, Tool, AgentType
from datetime import datetime
import uuid
from config import (
    SMTP2GO_API_KEY,
    SENDER_EMAIL,
    WEBSOCKET_URL,
    BASE_APPROVAL_URL,
)


class ApprovalTimeoutError(Exception):
    pass


def generate_email_template(role: str, user_id: str) -> str:
    approve_url = f"{BASE_APPROVAL_URL}/{user_id}/approve"
    reject_url = f"{BASE_APPROVAL_URL}/{user_id}/reject"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Rental Agreement for {role}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                padding: 20px;
                background-color: #f4f4f4;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            .button {{
                display: inline-block;
                padding: 10px 20px;
                margin: 10px 5px;
                border-radius: 5px;
                text-decoration: none;
                color: white;
            }}
            .approve {{
                background-color: #28a745;
            }}
            .reject {{
                background-color: #dc3545;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <p>Hello,</p>
            <p>Please review and sign the attached rental agreement document.</p>
            <p>Click on one of the following links to approve or reject the agreement:</p>
            <p>
                <a href="{approve_url}" class="button approve">Approve Agreement</a>
                <a href="{reject_url}" class="button reject">Reject Agreement</a>
            </p>
            <p>Best regards,<br>Docu Sign Team</p>
        </div>
    </body>
    </html>
    """


download_pandoc()

# Memory and LLM setup
memory = ConversationBufferMemory(memory_key="chat_history")
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key="",
    base_url="http://0.0.0.0:1337/v1",
)


class State(TypedDict):
    messages: Annotated[list, add_messages]


class AgreementState:
    def __init__(self):
        self.tenant_id = str(uuid.uuid4())
        self.owner_id = str(uuid.uuid4())
        self.tenant_approved = False
        self.owner_approved = False
        self.agreement_text = ""
        self.tenant_signature = ""
        self.owner_signature = ""

    def is_fully_approved(self):
        return self.tenant_approved and self.owner_approved


agreement_state = AgreementState()


def read_pdf_pypdf(file_path):
    reader = PdfReader(file_path)
    text = "\n".join(
        [page.extract_text() for page in reader.pages if page.extract_text()]
    )
    return text


def send_email_with_attachment(recipient_email: str, pdf_path: str, role: str):
    url = "https://api.smtp2go.com/v3/email/send"

    with open(pdf_path, "rb") as attachment_file:
        file_content = attachment_file.read()
        encoded_file = base64.b64encode(file_content).decode("utf-8")

    user_id = (
        agreement_state.tenant_id if role == "tenant" else agreement_state.owner_id
    )
    email_body = generate_email_template(role, user_id)

    payload = {
        "sender": SENDER_EMAIL,
        "to": [recipient_email],
        "subject": f"Rental Agreement for {role.capitalize()}",
        "html_body": email_body,
        "attachments": [
            {
                "fileblob": encoded_file,
                "filename": "rental-agreement.pdf",
                "content_type": "application/pdf",
            }
        ],
    }

    headers = {
        "X-Smtp2go-Api-Key": SMTP2GO_API_KEY,
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.status_code == 200, response.text


async def listen_for_approval(timeout_seconds: int = 300) -> bool:
    """
    Listen for approval messages with a timeout.

    Args:
        timeout_seconds: Maximum time to wait for approvals (default 5 minutes)

    Returns:
        bool: True if both parties approved, False if rejected or timeout

    Raises:
        ApprovalTimeoutError: If no response received within timeout period
    """
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            while True:
                try:
                    # Set timeout for receiving messages
                    response = await asyncio.wait_for(
                        websocket.recv(), timeout=timeout_seconds
                    )

                    data = json.loads(response)
                    print(f"Received approval response: {data}")

                    if data.get("user_id") == agreement_state.tenant_id:
                        agreement_state.tenant_approved = data.get("approved", False)
                        if agreement_state.tenant_approved:
                            agreement_state.tenant_signature = (
                                f"APPROVED BY TENANT - {datetime.now()}"
                            )
                            print("Tenant has approved!")
                        else:
                            print("Tenant has rejected!")
                            return False

                    elif data.get("user_id") == agreement_state.owner_id:
                        agreement_state.owner_approved = data.get("approved", False)
                        if agreement_state.owner_approved:
                            agreement_state.owner_signature = (
                                f"APPROVED BY OWNER - {datetime.now()}"
                            )
                            print("Owner has approved!")
                        else:
                            print("Owner has rejected!")
                            return False

                    # Check if both parties have responded
                    if agreement_state.is_fully_approved():
                        print("Both parties have approved!")
                        return True

                except asyncio.TimeoutError:
                    raise ApprovalTimeoutError(
                        "Approval process timed out after " f"{timeout_seconds} seconds"
                    )
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON received: {e}")
                    continue

    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed unexpectedly")
        return False
    except websockets.exceptions.WebSocketException as e:
        print(f"WebSocket error: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False


def generate_agreement(state: State):
    system_msg = {
        "role": "system",
        "content": """You are a rental agreement generator. Your task is to fill in the rental agreement template with the provided details.
        IMPORTANT RULES:
        1. Output ONLY the agreement text itself
        2. Do NOT add any introductory text
        3. Do NOT add any concluding text
        4. Do NOT add any notes or comments
        5. Start directly with the agreement content
        6. Include placeholder text [TENANT SIGNATURE] and [OWNER SIGNATURE] where signatures should go
        7. Make sure to add all the details for all points mentioned
        8. Dont include any symbols in the text such as currency symobls like ₹, etc.
        """,
    }
    messages = [system_msg] + state["messages"]
    response = llm.invoke(messages)
    agreement_state.agreement_text = response.content
    return {"messages": response}


def create_pdf(state: State):
    content = state["messages"][-1].content

    if agreement_state.is_fully_approved():
        content = content.replace(
            "[TENANT SIGNATURE]", agreement_state.tenant_signature
        )
        content = content.replace("[OWNER SIGNATURE]", agreement_state.owner_signature)

    pypandoc.convert_text(
        content, "pdf", "md", encoding="utf-8", outputfile="rental-agreement.pdf"
    )
    return {"messages": content}


# Build graph
graph_builder = StateGraph(State)
graph_builder.add_node("generate", generate_agreement)
graph_builder.add_node("create_pdf", create_pdf)
graph_builder.add_edge(START, "generate")
graph_builder.add_edge("generate", "create_pdf")
graph_builder.add_edge("create_pdf", END)

graph = graph_builder.compile()


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
    agent_kwargs={
        "prefix": """You are just a legal agreement generator. Your task is to use the generate_agreement tool to create agreements.
        IMPORTANT: The tool will output only the agreement text without any symbols in it such as currency symbols etc. Do not add any additional text, comments, or formatting.
        Use this exact format:
        Action: generate_agreement
        Action Input: <user input>"""
    },
)


async def main():
    print("\nWelcome to the Rental Agreement Generator")
    print("Please provide the following information:")
    tenant_email = input("Enter tenant's email: ").strip()
    owner_email = input("Enter owner's email: ").strip()
    agreement_details = input("Enter agreement details: ").strip()

    try:
        print("\nGenerating agreement...")
        # Generate initial agreement
        response = agent.run(agreement_details)

        print("\nSending emails to tenant and owner...")
        # Send initial emails
        tenant_success, _ = send_email_with_attachment(
            tenant_email, "rental-agreement.pdf", "tenant"
        )
        owner_success, _ = send_email_with_attachment(
            owner_email, "rental-agreement.pdf", "owner"
        )

        if tenant_success and owner_success:
            print("Initial agreements sent successfully!")
            print("\nWaiting for approvals (timeout: 5 minutes)...")

            try:
                # Wait for approvals with timeout
                approved = await listen_for_approval(timeout_seconds=300)

                if approved:
                    print("\nBoth parties approved! Generating final agreement...")
                    # Generate final PDF with signatures
                    _ = agent.run(agreement_details)

                    # Send final signed version
                    send_email_with_attachment(
                        tenant_email, "rental-agreement.pdf", "tenant"
                    )
                    send_email_with_attachment(
                        owner_email, "rental-agreement.pdf", "owner"
                    )
                    print("Final signed agreement sent to both parties!")
                else:
                    print("\nAgreement was rejected or approval process failed.")

            except ApprovalTimeoutError:
                print("\nApproval process timed out. Please try again later.")

        else:
            print("Error sending initial emails.")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
