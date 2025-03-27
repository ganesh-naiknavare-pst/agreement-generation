import tempfile
from constants import Model, CHAT_OPENAI_BASE_URL
import pypandoc
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from helpers.state_manager import State, state_manager
import os
from PIL import Image
import io

os.environ["OPENAI_API_KEY"] = "XXX"

memory = ConversationBufferMemory(memory_key="chat_history")
llm = ChatOpenAI(
    model=Model.GPT_MODEL.value,
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key="",
    base_url=CHAT_OPENAI_BASE_URL,
)
from prompts import AGREEMENT_SYSTEM_PROMPT


def generate_agreement(state: State):
    agreement_id = state["agreement_id"]
    current_state = state_manager.get_agreement_state(agreement_id)
    if not current_state:
        raise ValueError("No active agreement state found")

    # Reset memory for fresh conversation
    memory.clear()
    if current_state.is_pdf_generated:
        return {"messages": current_state.agreement_text, "agreement_id": agreement_id}
    system_msg = {
        "role": "system",
        "content": AGREEMENT_SYSTEM_PROMPT,
    }
    messages = [system_msg] + state["messages"]
    response = llm.invoke(messages)
    current_state.agreement_text = response.content
    return {"messages": response, "agreement_id": agreement_id}


def resize_image(image_path, max_width, max_height):
    try:
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        with Image.open(image_path) as img:
            if image_path.lower().endswith(".jfif"):
                img = img.convert("RGB")

            img.thumbnail((max_width, max_height), Image.LANCZOS)

            original_format = "jpeg" if img.format == "JPEG" else "png"
            file_extension = ".jpg" if original_format == "jpeg" else ".png"

            temp_image = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
            temp_image_path = temp_image.name
            img.save(temp_image_path, format=img.format)
            temp_image.close()

            return temp_image_path, original_format
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None, None


def create_pdf(state: State):
    if isinstance(state, dict):
        content = state["messages"][-1].content
        agreement_id = state["agreement_id"]
        state = state_manager.get_agreement_state(agreement_id)
        state.agreement_text = content
    else:
        content = state.agreement_text

    if not state:
        raise ValueError("No active agreement state found")

    if state.is_fully_approved():
        # Replace owner signature with image
        if os.path.isfile(state.owner_signature):
            owner_signature_data, _ = resize_image(
                state.owner_signature, 60, 30
            )
            content = content.replace(
                "[OWNER SIGNATURE]", f" ![Owner Signature]({owner_signature_data})"
            )
        else:
            content = content.replace(
                "[OWNER SIGNATURE]", state.owner_signature
            )

        # Replace owner photos with image
        if os.path.isfile(state.owner_photo):
            owner_photo_data, _ = resize_image(state.owner_photo, 60, 60)
            content = content.replace(
                "[OWNER PHOTO]", f" ![Owner PHOTO]({owner_photo_data})"
            )
        else:
            content = content.replace("[OWNER PHOTO]", state.owner_photo)

        # Replace tenant signatures with numbered placeholders and images
        for i, (tenant_id, signature) in enumerate(
            state.tenant_signatures.items(), 1
        ):
            placeholder = f"[TENANT {i} SIGNATURE]"
            tenant_name = state.tenant_names.get(tenant_id, f"Tenant {i}")

            if os.path.isfile(signature):
                tenant_signature_data, _ = resize_image(signature, 60, 30)
                content = content.replace(
                    placeholder, f" ![Tenant {i} Signature]({tenant_signature_data})"
                )
            else:
                content = content.replace(placeholder, signature)

        # Replace tenant photos with numbered placeholders and images
        for i, (tenant_id, photo) in enumerate(
            state.tenant_photos.items(), 1
        ):
            placeholder = f"[TENANT {i} PHOTO]"
            tenant_name = state.tenant_names.get(tenant_id, f"Tenant {i}")
            if os.path.isfile(photo):
                tenant_photos_data, _ = resize_image(photo, 60, 60)
                content = content.replace(
                    placeholder, f" ![Tenant PHOTO]({tenant_photos_data})"
                )
            else:
                content = content.replace(placeholder, photo)

    # Ensure no Rupee symbols make it through to the PDF
    content = content.replace("₹", "Rs.")

    # Remove any potential Unicode characters that might cause LaTeX issues
    content = content.encode("ascii", "ignore").decode()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Create a temporary file
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir=base_dir)
    temp_pdf_path = temp_pdf.name

    pypandoc.convert_text(
        content, "pdf", "md", encoding="utf-8", outputfile=temp_pdf_path
    )
    state.pdf_file_path = temp_pdf_path
    return {"messages": content}


# Build graph
graph_builder = StateGraph(State)
graph_builder.add_node("generate", generate_agreement)
graph_builder.add_node("create_pdf", create_pdf)
graph_builder.add_edge(START, "generate")
graph_builder.add_edge("generate", "create_pdf")
graph_builder.add_edge("create_pdf", END)
graph = graph_builder.compile()
