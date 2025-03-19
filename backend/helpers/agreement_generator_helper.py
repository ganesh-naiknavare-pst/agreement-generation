import fitz
import os
from collections import Counter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

def extract_text_from_pdf(pdf_path, chunk_size=1000):
    """Extracts text from a PDF file and returns it in manageable chunks."""
    doc = fitz.open(pdf_path)
    full_text = "\n".join([page.get_text("text") for page in doc])

    chunks = [full_text[i : i + chunk_size] for i in range(0, len(full_text), chunk_size)]

    return chunks

def find_font_file(font_name, fonts_dir="fonts"):
    """Searches for a font file in the project-specific fonts directory."""
    font_extensions = (".ttf", ".otf")
    
    for root, _, files in os.walk(fonts_dir):
        for file in files:
            if file.lower().startswith(font_name.lower()) and file.lower().endswith(font_extensions):
                return os.path.join(root, file)
    
    return None

def extract_fonts(pdf_path):
    doc = fitz.open(pdf_path)
    font_counter = Counter()

    for page in doc:
        text_instances = page.get_text("dict")["blocks"]
        for block in text_instances:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_name = span["font"]
                        font_counter[font_name] += 1

    if not font_counter:
        return "Helvetica", None
    
    font_file = find_font_file(font_name)
    font_name, _ = font_counter.most_common(1)[0]
    return font_name, font_file

def create_pdf_file(content, output_pdf_path="output.pdf", font_name="Times-Roman", font_file="/backend/fonts/times-roman/Times-Roman.ttf"):
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
