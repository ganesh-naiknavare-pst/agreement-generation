import fitz
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def extract_text_from_pdf(pdf_path, chunk_size=1000):
    """Extracts text from a PDF file and returns it in manageable chunks."""
    doc = fitz.open(pdf_path)
    full_text = "\n".join([page.get_text("text") for page in doc])

    chunks = [full_text[i : i + chunk_size] for i in range(0, len(full_text), chunk_size)]
    
    return chunks

def find_font_file(font_name):
    """Search for a font file based on the extracted font name."""
    common_paths = [
        "/usr/share/fonts", "/usr/local/share/fonts", "~/.fonts",
        "C:/Windows/Fonts"
    ]
    font_extensions = [".ttf", ".otf"]

    for path in common_paths:
        full_path = os.path.expanduser(path)
        if os.path.exists(full_path):
            for root, _, files in os.walk(full_path):
                for file in files:
                    if file.lower().startswith(font_name.lower()) and file.lower().endswith(tuple(font_extensions)):
                        return os.path.join(root, file)

    return None

def extract_fonts(pdf_path):
    """Extracts fonts from the PDF and returns the first found font and its file path."""
    doc = fitz.open(pdf_path)
    font_set = set()

    for page in doc:
        text_info = page.get_text("dict")
        for block in text_info.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    font_set.add(span.get("font", "Unknown"))

    doc.close()
    
    if font_set:
        font_name = list(font_set)[0]
        font_file = find_font_file(font_name)
        return font_name, font_file
    else:
        return "helv", None
    
def create_pdf_file(content, font_name="Helvetica", font_file=None, output_pdf_path="output.pdf"):

    c = canvas.Canvas(output_pdf_path, pagesize=A4)
    
    if font_file and os.path.exists(font_file):
        pdfmetrics.registerFont(TTFont(font_name, font_file))
        c.setFont(font_name, 12)
    else:
        c.setFont("Helvetica", 12)

    # Set margins and text wrapping
    x, y = 50, 800
    max_width = 500
    lines = content.split("\n")

    for line in lines:
        if y < 50:
            c.showPage()
            c.setFont(font_name, 12) if font_file else c.setFont("Helvetica", 12)
            y = 800

        wrapped_lines = []
        while len(line) > 0:
            split_index = min(len(line), max_width // 6)
            wrapped_lines.append(line[:split_index])
            line = line[split_index:]

        for wrapped_line in wrapped_lines:
            c.drawString(x, y, wrapped_line)
            y -= 20

    c.save()
    return output_pdf_path