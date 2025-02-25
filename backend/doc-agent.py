import asyncio
from helpers.email_helper import send_email_with_attachment
from helpers.websocket_helper import listen_for_approval, ApprovalTimeoutError
from langchain.agents import initialize_agent, Tool, AgentType
from helpers.rent_agreement_generator import llm, memory, graph
from prompts import  AGENT_PREFIX
from templates import  format_agreement_details
from helpers.state_manager import  agreement_state

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
    agent_kwargs=AGENT_PREFIX,
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