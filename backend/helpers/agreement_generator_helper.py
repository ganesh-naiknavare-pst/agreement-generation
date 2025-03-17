import platform
import fitz
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

def extract_text_from_pdf(pdf_path, chunk_size=1000):
    """Extracts text from a PDF file and returns it in manageable chunks."""
    doc = fitz.open(pdf_path)
    full_text = "\n".join([page.get_text("text") for page in doc])

    chunks = [full_text[i : i + chunk_size] for i in range(0, len(full_text), chunk_size)]

    return chunks

def find_font_file(font_name):
    font_extensions = (".ttf", ".otf")  # Common font file extensions

    # Define common font directories per OS
    common_paths = {
        "Linux": ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts")],
        "Darwin": ["/System/Library/Fonts", os.path.expanduser("~/Library/Fonts")],
        "Windows": [r"C:\Windows\Fonts"]
    }

    system_platform = platform.system()
    search_paths = common_paths.get(system_platform, [])

    # Search for the font in each directory
    for path in search_paths:
        if os.path.exists(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if file.lower().startswith(font_name.lower()) and file.lower().endswith(font_extensions):
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

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os

def create_pdf_file(content, font_name="Helvetica", font_file=None, output_pdf_path="output.pdf"):
    doc = SimpleDocTemplate(output_pdf_path, pagesize=A4)

    styles = getSampleStyleSheet()
    custom_style = ParagraphStyle(
        "Custom",
        parent=styles["Normal"],
        fontName=font_name if font_file else "Helvetica",
        fontSize=10,
        leading=12,
        spaceAfter=10
    )

    if font_file and os.path.exists(font_file):
        pdfmetrics.registerFont(TTFont(font_name, font_file))

    story = []
    paragraphs = content.split("\n\n")

    for para in paragraphs:
        para = para.replace("\n", "<br/>")
        story.append(Paragraph(para, custom_style))
        story.append(Spacer(1, 12))

    doc.build(story)
    return output_pdf_path
