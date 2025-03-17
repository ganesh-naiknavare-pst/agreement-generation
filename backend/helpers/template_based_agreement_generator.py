import tempfile
from helpers.rent_agreement_generator import resize_image
from constants import Model, CHAT_OPENAI_BASE_URL
import pypandoc
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from helpers.state_manager import State, template_agreement_state
from helpers.agreement_generator_helper import extract_text_from_pdf, extract_fonts, create_pdf_file
from prompts import SYSTEM_PROMPT_FOR_SIGNATURE_PLACEHOLDER, USER_PROMPT_FOR_SIGNATURE_PLACEHOLDER, SYSTEM_PROMPT_FOR_AGGREMENT_GENERATION
import os

os.environ["OPENAI_API_KEY"] = "XXX"

memory = ConversationBufferMemory(memory_key="chat_history")
llm = ChatOpenAI(
    model= Model.GPT_MODEL.value,
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

    template_chunks = extract_text_from_pdf(template_agreement_state.template_file_path)
    font_name, font_file = extract_fonts(template_agreement_state.template_file_path)
    template_agreement_state.pdf_font_name = font_name
    template_agreement_state.pdf_font_file = font_file

    generated_text = ""
    for chunk in template_chunks:
        system_msg = {
            "role": "system",
            "content": SYSTEM_PROMPT_FOR_AGGREMENT_GENERATION.format(template_text=chunk),
        }
        messages = [system_msg] + state["messages"]
        response = llm.invoke(messages)
        generated_text += response.content + "\n"

    response_sign = add_signature(generated_text)
    template_agreement_state.agreement_text = response_sign.content

    return {"messages": response_sign}

def create_pdf(state: State):
    if template_agreement_state.is_pdf_generated:
        content= template_agreement_state.agreement_text
    else:
        content = state["messages"][-1].content
    content = content.replace("₹", "Rs.")

    content = content.encode('ascii', 'ignore').decode()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir=base_dir)
    temp_pdf_path = temp_pdf.name
    create_pdf_file(content, template_agreement_state.pdf_font_name, template_agreement_state.pdf_font_file, temp_pdf_path)

    template_agreement_state.pdf_file_path = temp_pdf_path
    return {"messages": content}

def update_pdf_with_signatures():
    """Updates the existing agreement PDF by replacing placeholders with actual signatures."""
    content = template_agreement_state.agreement_text
    if template_agreement_state.is_fully_approved():

        # Replace authority signature with image
        if os.path.isfile(template_agreement_state.authority_signature):
            authority_signature_data, _ = resize_image(
                template_agreement_state.authority_signature, 60, 30
            )
            content = content.replace(
                "[AUTHORITY_SIGNATURE]", f" ![AUTHORITY_SIGNATURE]({authority_signature_data})"
            )
        else:
            content = content.replace(
                "[AUTHORITY_SIGNATURE]", template_agreement_state.authority_signature
            )

        # Replace participant signature with image
        if os.path.isfile(template_agreement_state.participant_signature):
            participant_signature_data, _ = resize_image(
                template_agreement_state.participant_signature, 60, 30
            )
            content = content.replace(
                "[PARTICIPANT_SIGNATURE]", f" ![PARTICIPANT_SIGNATURE]({participant_signature_data})"
            )
        else:
            content = content.replace(
                "[PARTICIPANT_SIGNATURE]", template_agreement_state.participant_signature
            )

    # Convert updated content to PDF
    temp_pdf_path = template_agreement_state.pdf_file_path
    create_pdf_file(content, template_agreement_state.pdf_font_name, template_agreement_state.pdf_font_file, temp_pdf_path)

# Build graph
graph_builder = StateGraph(State)
graph_builder.add_node("generate", generate_agreement)
graph_builder.add_node("create_pdf", create_pdf)
graph_builder.add_edge(START, "generate")
graph_builder.add_edge("generate", "create_pdf")
graph_builder.add_edge("create_pdf", END)
template_graph = graph_builder.compile()
