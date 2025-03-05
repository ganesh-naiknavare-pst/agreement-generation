import fitz

def extract_text_from_pdf(pdf_path, chunk_size=1000):
    """Extracts text from a PDF file and returns it in manageable chunks."""
    doc = fitz.open(pdf_path)
    full_text = "\n".join([page.get_text("text") for page in doc])

    chunks = [full_text[i : i + chunk_size] for i in range(0, len(full_text), chunk_size)]
    
    return chunks
