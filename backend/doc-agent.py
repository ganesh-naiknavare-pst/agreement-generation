import os
import pypandoc
import base64
import requests
import asyncio
import websockets
import json
from typing import Annotated
from typing_extensions import TypedDict
from langchain.chat_models import ChatOpenAI
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from pypandoc.pandoc_download import download_pandoc
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, Tool, AgentType
from datetime import datetime
import uuid
import os
from config import (
    SMTP2GO_API_KEY,
    SENDER_EMAIL,
    WEBSOCKET_URL,
    BASE_APPROVAL_URL,
)
from prompts import AGREEMENT_SYSTEM_PROMPT, AGENT_PREFIX
from templates import generate_email_template, format_agreement_details


os.environ["OPENAI_API_KEY"] = "XXX"


class ApprovalTimeoutError(Exception):
    pass


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
        self.owner_name = ""
        self.tenants = {}
        self.tenant_names = {}
        self.owner_approved = False
        self.agreement_text = ""
        self.owner_signature = ""
        self.tenant_signatures = {}

    def add_tenant(self, tenant_email, tenant_name):
        tenant_id = str(uuid.uuid4())
        self.tenants[tenant_id] = False
        self.tenant_signatures[tenant_id] = ""
        self.tenant_names[tenant_id] = tenant_name
        return tenant_id

    def set_owner(self, owner_name):
        self.owner_name = owner_name

    def is_fully_approved(self):
        return self.owner_approved and all(self.tenants.values())


agreement_state = AgreementState()


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

    email_body = generate_email_template(role, user_id, BASE_APPROVAL_URL)

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
                            tenant_name = agreement_state.tenant_names[user_id]
                            agreement_state.tenant_signatures[user_id] = (
                                f"APPROVED BY {tenant_name} - {datetime.now()}"
                            )
                            print(f"Tenant {tenant_name} has approved!")
                        else:
                            print(f"Tenant {user_id} has rejected!")
                            return False

                    elif user_id == agreement_state.owner_id:
                        agreement_state.owner_approved = data.get("approved", False)
                        if agreement_state.owner_approved:
                            agreement_state.owner_signature = (
                                f"APPROVED BY {agreement_state.owner_name} - {datetime.now()}"
                            )
                            print(f"Owner {agreement_state.owner_name} has approved!")
                        else:
                            print("Owner has rejected!")
                            return False
                    # Check if both parties have responded
                    if agreement_state.is_fully_approved():
                        print("Both parties have approved!")
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
        "content": AGREEMENT_SYSTEM_PROMPT,
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

    # Ensure no Rupee symbols make it through to the PDF
    content = content.replace("₹", "Rs.")
    
    # Remove any potential Unicode characters that might cause LaTeX issues
    content = content.encode('ascii', 'ignore').decode()

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
        "prefix": AGENT_PREFIX
    },
)


async def main():
    print("\nWelcome to the Rental Agreement Generator")
    print("Please provide the following information:")
    
    # Get owner information
    owner_name = input("Enter owner's name: ").strip()
    owner_email = input("Enter owner's email: ").strip()
    agreement_state.set_owner(owner_name)  # Store owner name
    
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
                tenant_id = agreement_state.add_tenant(tenant_email, tenant_name)  # Pass tenant name
                tenants.append((tenant_id, tenant_email))
                tenant_details.append({"name": tenant_name, "email": tenant_email})
                break
            print("Name and email cannot be empty. Please try again.")

    # Get other agreement details
    property_address = input("\nEnter property address: ").strip()
    city = input("Enter city: ").strip()
    rent_amount = input("Enter monthly rent amount: ").strip()
    start_date = input("Enter agreement start date (YYYY-MM-DD): ").strip()
    
    # Replace the agreement_details string with the template function
    agreement_details = format_agreement_details(
        owner_name=owner_name,
        tenant_details=tenant_details,
        property_address=property_address,
        city=city,
        rent_amount=rent_amount,
        start_date=start_date
    )

    try:
        print("\nGenerating agreement...")
        # Generate initial agreement
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
                # Wait for approvals with timeout
                approved = await listen_for_approval(timeout_seconds=300)

                if approved:
                    print("\nBoth parties approved! Generating final agreement...")
                    # Generate final PDF with signatures
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
