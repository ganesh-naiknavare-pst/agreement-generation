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
        self.owner_id = str(uuid.uuid4())
        self.tenants = {}  # Dict to store multiple tenants {tenant_id: approval_status}
        self.owner_approved = False
        self.agreement_text = ""
        self.owner_signature = ""
        self.tenant_signatures = {}  # Dict to store tenant signatures {tenant_id: signature}

    def add_tenant(self, tenant_email):
        tenant_id = str(uuid.uuid4())
        self.tenants[tenant_id] = False
        self.tenant_signatures[tenant_id] = ""
        return tenant_id

    def is_fully_approved(self):
        return self.owner_approved and all(self.tenants.values())


agreement_state = AgreementState()


def read_pdf_pypdf(file_path):
    reader = PdfReader(file_path)
    text = "\n".join(
        [page.extract_text() for page in reader.pages if page.extract_text()]
    )
    return text


def send_email_with_attachment(recipient_email: str, pdf_path: str, role: str, user_id=None):
    url = "https://api.smtp2go.com/v3/email/send"

    with open(pdf_path, "rb") as attachment_file:
        file_content = attachment_file.read()
        encoded_file = base64.b64encode(file_content).decode("utf-8")

    # Use the provided user_id for tenants, or owner_id for owner
    if role == "owner":
        user_id = agreement_state.owner_id
    elif user_id is None:
        user_id = agreement_state.owner_id  # fallback, though this shouldn't happen

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
    if response.status_code == 200:
        print(f"Successfully sent email to {recipient_email}")
    else:
        print(f"Failed to send email to {recipient_email}: {response.text}")
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

                    user_id = data.get("user_id")
                    
                    if user_id in agreement_state.tenants:
                        agreement_state.tenants[user_id] = data.get("approved", False)
                        if agreement_state.tenants[user_id]:
                            agreement_state.tenant_signatures[user_id] = (
                                f"APPROVED BY TENANT - {datetime.now()}"
                            )
                            print(f"Tenant {user_id} has approved!")
                        else:
                            print(f"Tenant {user_id} has rejected!")
                            return False

                    elif user_id == agreement_state.owner_id:
                        agreement_state.owner_approved = data.get("approved", False)
                        if agreement_state.owner_approved:
                            agreement_state.owner_signature = (
                                f"APPROVED BY OWNER - {datetime.now()}"
                            )
                            print("Owner has approved!")
                        else:
                            print("Owner has rejected!")
                            return False

                    if agreement_state.is_fully_approved():
                        print("Owner and all tenants have approved!")
                        return True

                except asyncio.TimeoutError:
                    raise ApprovalTimeoutError(
                        f"Approval process timed out after {timeout_seconds} seconds"
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
        6. Include placeholder text [TENANT 1 SIGNATURE], [TENANT 2 SIGNATURE] etc. for each tenant and [OWNER SIGNATURE] for owner
        7. Make sure to add all the details for all points mentioned
        8. Use 'Rs.' instead of any currency symbols
        9. Number each tenant as TENANT 1, TENANT 2, etc. in the agreement
        10. NEVER use the ₹ symbol - always use 'Rs.' instead
        """,
    }
    messages = [system_msg] + state["messages"]
    response = llm.invoke(messages)
    agreement_state.agreement_text = response.content
    return {"messages": response}


def create_pdf(state: State):
    content = state["messages"][-1].content

    if agreement_state.is_fully_approved():
        # Replace owner signature
        content = content.replace("[OWNER SIGNATURE]", agreement_state.owner_signature)
        
        # Replace tenant signatures with numbered placeholders
        for i, (tenant_id, signature) in enumerate(agreement_state.tenant_signatures.items(), 1):
            placeholder = f"[TENANT {i} SIGNATURE]"
            content = content.replace(placeholder, signature)

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
    
    # Get owner information
    owner_name = input("Enter owner's name: ").strip()
    owner_email = input("Enter owner's email: ").strip()
    
    # First ask for number of tenants
    while True:
        try:
            num_tenants = int(input("Enter the number of tenants for this agreement: ").strip())
            if num_tenants <= 0:
                print("Please enter a valid number greater than 0")
                continue
            break
        except ValueError:
            print("Please enter a valid number")
    
    # Get multiple tenant information
    tenants = []
    tenant_details = []
    print(f"\nPlease enter details for {num_tenants} tenants:")
    for i in range(num_tenants):
        print(f"\nTenant {i+1} Details:")
        while True:
            tenant_name = input(f"Enter name for Tenant {i+1}: ").strip()
            tenant_email = input(f"Enter email for Tenant {i+1}: ").strip()
            if tenant_email and tenant_name:
                tenant_id = agreement_state.add_tenant(tenant_email)
                tenants.append((tenant_id, tenant_email))
                tenant_details.append({"name": tenant_name, "email": tenant_email})
                break
            print("Name and email cannot be empty. Please try again.")

    # Get other agreement details
    property_address = input("\nEnter property address: ").strip()
    city = input("Enter city: ").strip()
    rent_amount = input("Enter monthly rent amount: ").strip()
    start_date = input("Enter agreement start date (YYYY-MM-DD): ").strip()
    
    # Format the agreement details in a structured way
    agreement_details = f"""
Create a rental agreement with the following details:

Owner: {owner_name}

Tenants:
{chr(10).join(f'{i+1}. {t["name"]}' for i, t in enumerate(tenant_details))}

Property Details:
- Address: {property_address}
- City: {city}
- Rent Amount in Rs :{rent_amount} 
- Agreement Start Date: {start_date}
- Duration: 11 months

Additional Terms:
- Rent will be split equally among all tenants
- Each tenant is jointly and severally liable for the full rent amount
- All tenants must agree to any changes in the agreement
- Security deposit will be Rs. {rent_amount} (collected equally from each tenant)
"""

    try:
        print("\nGenerating agreement...")
        response = agent.run(agreement_details)

        print("\nSending emails to owner and tenants...")
        
        # Send to owner
        owner_success, _ = send_email_with_attachment(
            owner_email, "rental-agreement.pdf", "owner"
        )

        # Send to all tenants
        tenant_successes = []
        for tenant_id, tenant_email in tenants:
            success, _ = send_email_with_attachment(
                tenant_email, 
                "rental-agreement.pdf", 
                "tenant",
                tenant_id
            )
            tenant_successes.append(success)
            print(f"Sent agreement to tenant: {tenant_email}")

        if owner_success and all(tenant_successes):
            print("Initial agreements sent successfully!")
            print("\nWaiting for approvals (timeout: 5 minutes)...")

            try:
                approved = await listen_for_approval(timeout_seconds=300)

                if approved:
                    print("\nAll parties approved! Generating final agreement...")
                    _ = agent.run(agreement_details)

                    print("\nSending final signed agreement to all parties...")
                    # Send to owner
                    owner_success, _ = send_email_with_attachment(
                        owner_email, "rental-agreement.pdf", "owner"
                    )
                    
                    # Send to all tenants with their respective IDs
                    for tenant_id, tenant_email in tenants:
                        send_email_with_attachment(
                            tenant_email, 
                            "rental-agreement.pdf", 
                            "tenant",
                            tenant_id
                        )
                        print(f"Sent final agreement to tenant: {tenant_email}")
                    
                    if owner_success:
                        print("Final signed agreement sent to all parties!")
                    else:
                        print("Error sending final agreement to some parties.")

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
