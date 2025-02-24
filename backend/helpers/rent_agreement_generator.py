from constants import Model, CHAT_OPENAI_BASE_URL
import pypandoc
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from helpers.state_manager import State, agreement_state
import os

os.environ["OPENAI_API_KEY"] = "XXX"

memory = ConversationBufferMemory(memory_key="chat_history")
llm = ChatOpenAI(
    model= Model.GPT_4.value,
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key="",
    base_url=CHAT_OPENAI_BASE_URL,
)

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
