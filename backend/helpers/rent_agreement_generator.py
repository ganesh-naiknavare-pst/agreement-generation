import tempfile
from constants import Model, CHAT_OPENAI_BASE_URL
import pypandoc
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from helpers.state_manager import State, agreement_state
import os
from PIL import Image
import io

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
from prompts import AGREEMENT_SYSTEM_PROMPT

def generate_agreement(state: State):
    if agreement_state.is_pdf_generated:
        return {"messages": agreement_state.agreement_text}
    system_msg = {
        "role": "system",
        "content": AGREEMENT_SYSTEM_PROMPT,
    }
    messages = [system_msg] + state["messages"]
    response = llm.invoke(messages)
    agreement_state.agreement_text = response.content
    return {"messages": response}

def resize_image(image_path, max_width, max_height):
    try:
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        with Image.open(image_path) as img:
            if image_path.lower().endswith('.jfif'):
                img = img.convert("RGB")  

            img.thumbnail((max_width, max_height), Image.LANCZOS)

            temp_image = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_image_path = temp_image.name
            img.save(temp_image_path, format='JPEG')
            temp_image.close()

            return temp_image_path, 'jpeg'
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None, None



def create_pdf(state: State):
    if agreement_state.is_pdf_generated:
        content = agreement_state.agreement_text
    else:
        content = state["messages"][-1].content

    if agreement_state.is_fully_approved():
        # Replace owner signature with image
        owner_signature_path = os.path.abspath(agreement_state.owner_signature)
        owner_signature_exists = os.path.isfile(owner_signature_path)

        if owner_signature_exists:
            owner_signature_data, owner_signature_format = resize_image(owner_signature_path, 60, 30)
            if owner_signature_data:
                content = content.replace(
                    "[OWNER SIGNATURE]", f"![Owner Signature]({owner_signature_data})"
                )
        else:
            content = content.replace("[OWNER SIGNATURE]", "Owner Name")

        # Replace tenant signatures with numbered placeholders and images
        for i, (tenant_id, signature) in enumerate(agreement_state.tenant_signatures.items(), 1):
            placeholder = f"[TENANT {i} SIGNATURE]"
            tenant_signature_path = os.path.abspath(signature)
            tenant_signature_exists = os.path.isfile(tenant_signature_path)

            if tenant_signature_exists:
                tenant_signature_data, _ = resize_image(tenant_signature_path, 60, 30)
                if tenant_signature_data:
                    content = content.replace(
                        placeholder, f"![Tenant {i} Signature]({tenant_signature_data})"
                    )

            else:
                content = content.replace(placeholder, f"Tenant {i} Name")

    # Ensure no Rupee symbols make it through to the PDF
    content = content.replace("₹", "Rs.")

    # Remove any potential Unicode characters that might cause LaTeX issues
    content = content.encode('ascii', 'ignore').decode()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Create a temporary file
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir=base_dir)
    temp_pdf_path = temp_pdf.name

    pypandoc.convert_text(
        content, "pdf", "md", encoding="utf-8", outputfile=temp_pdf_path
    )
    agreement_state.pdf_file_path = temp_pdf_path
    return {"messages": content}
# Build graph
graph_builder = StateGraph(State)
graph_builder.add_node("generate", generate_agreement)
graph_builder.add_node("create_pdf", create_pdf)
graph_builder.add_edge(START, "generate")
graph_builder.add_edge("generate", "create_pdf")
graph_builder.add_edge("create_pdf", END)
graph = graph_builder.compile()
