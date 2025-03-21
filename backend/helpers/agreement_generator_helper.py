import fitz
import os
import re
from collections import Counter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, KeepTogether, Table, TableStyle, Image, HRFlowable
from reportlab.lib import colors
from PIL import Image as PILImage
import pypandoc
import shutil

PAGE_WIDTH, PAGE_HEIGHT = A4

def extract_text_from_pdf(pdf_path, chunk_size=1000):
    """Extracts text from a PDF file and returns it in manageable chunks."""
    doc = fitz.open(pdf_path)
    full_text = "\n".join([page.get_text("text") for page in doc])
    chunks = [full_text[i: i + chunk_size] for i in range(0, len(full_text), chunk_size)]
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
    """Extracts the most common font from a PDF."""
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
    font_name, _ = font_counter.most_common(1)[0]
    font_file = find_font_file(font_name)
    return font_name, font_file

def resize_image(image_path, max_width=80, max_height=50):
    """Resizes an image to fit within max dimensions while maintaining aspect ratio."""
    try:
        img = PILImage.open(image_path)
        img.thumbnail((max_width, max_height))
        resized_img_path = f"temp_resized_{os.path.basename(image_path)}"
        img.save(resized_img_path)
        return resized_img_path
    except Exception as e:
        return None

def preprocess_table_data(data):
    """Preprocess table data to merge grouped rows while keeping the header intact."""
    if not data:
        return []
    header = data[0]
    merged_data = [header]
    row_count = len(data)
    col_count = len(header)

    i = 1
    while i < row_count:
        if i + 2 < row_count:
            merged_row = data[i][:]
            for col in range(col_count):
                if data[i + 1][col] == data[i + 2][col]:
                    merged_row[col] = data[i][col] 
                else:
                    merged_row[col] = f"{data[i][col]}\n{data[i + 1][col]}\n{data[i + 2][col]}"  # Merge contents
            merged_data.append(merged_row)
            i += 3
        else:
            merged_data.append(data[i])
            i += 1
    return merged_data

def clean_html_for_reportlab(html):
    html = re.sub(r'<b>\s*</b>', '', html)
    html = re.sub(r'<para>\s*</para>', '', html)
    html = re.sub(r'(<br\s*/?>\s*)+', '<br/>', html)
    html = re.sub(r'<para fontSize="(\d+)"><b>(.*?)</b></para>', r'<p style="font-size:\1px; font-weight:bold;">\2</p>', html)
    html = re.sub(r'<para fontSize="(\d+)">(.*?)</para>', r'<p style="font-size:\1px;">\2</p>', html)
    html = re.sub(r'<para>', '<p>', html)
    html = re.sub(r'</para>', '</p>', html)
    html = html.replace('<hr width="100%"/>', '<hr/>')
    return html.strip()

def markdown_to_html(text):
    """Converts Markdown to HTML for ReportLab compatibility."""
    
    text = re.sub(r'### (.*?)\s*\n?', r'<para fontSize="14"><b>\1</b></para><br/><br/>', text)
    text = re.sub(r'## (.*?)\s*\n?', r'<para fontSize="12"><b>\1</b></para><br/><br/>', text)
    text = re.sub(r'# (.*?)\s*\n?', r'<para fontSize="16"><b>\1</b></para><br/><br/>', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = re.sub(r'(?m)^\s*[-•] (.*?)$', r'• \1', text)
    text = text.replace("\n", "<br/>")  
    return text

def parse_markdown_table(md_table):
    """Parses a Markdown table and ensures images are correctly inserted."""
    lines = md_table.strip().split("\n")
    rows = [line.split("|")[1:-1] for line in lines if "|" in line]
    data = [[cell.strip() for cell in row] for row in rows]
    data = [row for row in data if not all(re.match(r"^[-:]+$", cell) for cell in row)]

    if len(data) > 0 and "Photo" in data[0] and "Signature" in data[0]:
        data = preprocess_table_data(data)

    image_pattern = re.compile(r"!\[(.*?)\]\((.*?)\)")
    styles = getSampleStyleSheet()
    body_style = styles["BodyText"]
    for row_idx in range(1, len(data)):
        for col_idx in range(len(data[row_idx])):
            cell_content = data[row_idx][col_idx]
            match = image_pattern.search(cell_content)
            if match:
                _, img_path = match.groups()
                img_path = img_path.strip()
                if os.path.exists(img_path):
                    resized_img = resize_image(img_path)
                    if resized_img:
                        data[row_idx][col_idx] = Image(resized_img, width=80, height=50)
            else:
                html_content = pypandoc.convert_text(cell_content, "html", format="md")
                html_content = re.sub(r"</strong>\s*<strong>", r"</strong><br/><strong>", html_content)
                html_content = re.sub(r"(?<!<br/>)\s*<strong>", r"<br/><strong>", html_content)
                html_content = re.sub(r"<p>(.*?)</p>", r"\1<br/>", html_content)
                data[row_idx][col_idx] = Paragraph(html_content, body_style)

    col_widths = [PAGE_WIDTH * 0.25] * len(data[0])
    table = Table(data, colWidths=col_widths)
    style = [
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("ALIGN", (0, 1), (0, -1), "LEFT"),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]
    table.setStyle(TableStyle(style))
    return table

def create_pdf_file(content, output_pdf_path="output.pdf", font_name="Times-Roman", font_file="fonts/times.ttf"):
    """Creates a PDF file with formatted text, images, and properly styled tables, ensuring temp files are cleaned up."""
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
    temp_files = []  # Store temp file paths for cleanup

    paragraphs = content.split("\n\n")
    table_pattern = re.compile(r"(\|.+?\|(?:\n\|[-:]+[-|:]+\|)+\n(?:\|.+?\|\n?)+)")
    image_pattern = re.compile(r"!\[(.*?)\]\((.*?)\)")

    for para in paragraphs:
        if table_pattern.match(para):
            table = parse_markdown_table(para)
            story.append(KeepTogether([table]))
        else:
            html_content = markdown_to_html(para)
            clean_content = clean_html_for_reportlab(html_content)
            elements = []
            temp_text = clean_content
            image_replacements = {}

            for match in image_pattern.finditer(para):
                label, img_path = match.groups()
                placeholder = f"[[IMAGE_{len(image_replacements)}]]"
                image_replacements[placeholder] = img_path
                temp_text = temp_text.replace(match.group(0), placeholder)

            parts = re.split(r"(\[\[IMAGE_\d+\]\])", temp_text)

            for part in parts:
                if part in image_replacements:
                    img_path = image_replacements[part]
                    if os.path.exists(img_path):
                        resized_img_path = resize_image(img_path)
                        if resized_img_path:
                            elements.append(Image(resized_img_path, width=80, height=50))
                            temp_files.append(resized_img_path)  # Track temp file
                elif part.strip() == "---":
                    elements.append(HRFlowable(width="100%", thickness=1, color="black", spaceBefore=10, spaceAfter=10))
                else:
                    elements.append(Paragraph(part, custom_style))

            story.append(KeepTogether(elements))
        story.append(Spacer(1, 12))

    doc.build(story)

    for temp_file in temp_files:
        try:
            os.remove(temp_file)
        except Exception as e:
            print(f"Warning: Could not delete temp file {temp_file} - {e}")

    return output_pdf_path