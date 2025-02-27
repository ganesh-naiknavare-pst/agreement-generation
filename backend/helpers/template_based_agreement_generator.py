import tempfile
from constants import Model, CHAT_OPENAI_BASE_URL
import pypandoc
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from helpers.state_manager import State, template_agreement_state
from helpers.agreement_generator_helper import extract_text_from_pdf
from prompts import SYSTEM_PROMPT_FOR_SIGNATURE_PLACEHOLDER, USER_PROMPT_FOR_SIGNATURE_PLACEHOLDER, SYSTEM_PROMPT_FOR_AGGREMENT_GENERATION
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

def add_signature(agreement_text: str):
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT_FOR_SIGNATURE_PLACEHOLDER.format(agreement_text=agreement_text),
        },
        {
            "role": "user",
            "content": USER_PROMPT_FOR_SIGNATURE_PLACEHOLDER,
        },
    ]
    
    return llm.invoke(messages)

def generate_agreement(state: State):
    if template_agreement_state.is_pdf_generated:
        return {"messages": template_agreement_state.agreement_text}
    template_text = extract_text_from_pdf("/home/pst-thinkpad/Agreement-Agent/backend/sample_rental_agr.pdf")
    # template_text = extract_text_from_pdf("/home/pst-thinkpad/Agreement-Agent/backend/offer_letter.pdf")
    print(f"Template Text------------------>{template_text}")
    system_msg = {
        "role": "system",
        "content": SYSTEM_PROMPT_FOR_AGGREMENT_GENERATION.format(template_text=template_text),
    }  
          
    messages = [system_msg] + state["messages"]
    response = llm.invoke(messages)
    response_sign = add_signature(response.content)
    template_agreement_state.agreement_text = response_sign.content
    
    return {"messages": response_sign}

def create_pdf(state: State):
    if template_agreement_state.is_pdf_generated:
        content= template_agreement_state.agreement_text
    else:
        content = state["messages"][-1].content

    if template_agreement_state.is_fully_approved():
        content = content.replace("[AUTHORITY_SIGNATURE]", template_agreement_state.authority_signature)
        content = content.replace("[PARTICIPANT_SIGNATURE]", template_agreement_state.participent_signature)
    content = content.replace("₹", "Rs.")

    content = content.encode('ascii', 'ignore').decode()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir=base_dir)
    temp_pdf_path = temp_pdf.name

    pypandoc.convert_text(
        content, "pdf", "md", encoding="utf-8", outputfile=temp_pdf_path
    )
    template_agreement_state.pdf_file_path = temp_pdf_path
    return {"messages": content}
# Build graph
graph_builder = StateGraph(State)
graph_builder.add_node("generate", generate_agreement)
graph_builder.add_node("create_pdf", create_pdf)
graph_builder.add_edge(START, "generate")
graph_builder.add_edge("generate", "create_pdf")
graph_builder.add_edge("create_pdf", END)
template_graph = graph_builder.compile()
