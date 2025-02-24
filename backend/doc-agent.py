import asyncio
from helpers.email_helper import send_email_with_attachment
from helpers.websocket_helper import listen_for_approval, ApprovalTimeoutError
from langchain.agents import initialize_agent, Tool, AgentType
from helpers.rent_agreement_generator import llm, memory, graph

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
