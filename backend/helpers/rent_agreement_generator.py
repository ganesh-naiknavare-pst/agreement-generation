import pypandoc
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from helpers.state_manager import State, agreement_state
import os

os.environ["OPENAI_API_KEY"] = "XXX"

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
from prompts import AGREEMENT_SYSTEM_PROMPT

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
