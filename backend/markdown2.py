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
from typing import List, Tuple, Optional
from reportlab.lib.colors import Color

PAGE_WIDTH, PAGE_HEIGHT = A4

def add_watermark(c, doc):
    """Adds a large semi-transparent 'DRAFT' watermark at the center of each page."""
    c.saveState()
    
    c.setFillColor(Color(0.85, 0.85, 0.85, alpha=0.3))
    
    text = "DRAFT"
    font_name = "Helvetica-Bold"
    font_size = 80
    c.setFont(font_name, font_size)

    c.translate(PAGE_WIDTH / 2, PAGE_HEIGHT / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, text)
    c.restoreState()
    
def extract_text_from_pdf(pdf_path: str, chunk_size: int = 1000) -> List[str]:
    """Extracts text from a PDF file and returns it in manageable chunks."""
    doc = fitz.open(pdf_path)
    full_text = "\n".join([page.get_text("text") for page in doc])
    chunks = [full_text[i: i + chunk_size] for i in range(0, len(full_text), chunk_size)]
    return chunks

def find_font_file(font_name: str, fonts_dir: str = "fonts") -> Optional[str]:
    """Searches for a font file in the project-specific fonts directory."""
    font_extensions = (".ttf", ".otf")
    for root, _, files in os.walk(fonts_dir):
        for file in files:
            if file.lower().startswith(font_name.lower()) and file.lower().endswith(font_extensions):
                return os.path.join(root, file)
    return None

def extract_fonts(pdf_path: str) -> Tuple[str, Optional[str]]:
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

def resize_image(image_path: str, max_width: int = 80, max_height: int = 50) -> Optional[str]:
    """Resizes an image to fit within max dimensions while maintaining aspect ratio."""
    try:
        img = PILImage.open(image_path)
        img.thumbnail((max_width, max_height))
        resized_img_path = f"temp_resized_{os.path.basename(image_path)}"
        img.save(resized_img_path)
        return resized_img_path
    except Exception as e:
        return None

def preprocess_table_data(data: List[List[str]]) -> List[List[str]]:
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

def clean_html_for_reportlab(html: str) -> str:
    html = re.sub(r'<b>\s*</b>', '', html)
    html = re.sub(r'<para>\s*</para>', '', html)
    html = re.sub(r'(<br\s*/?>\s*)+', '<br/>', html)
    html = re.sub(r'<para fontSize="(\d+)"><b>(.*?)</b></para>', r'<p style="font-size:\1px; font-weight:bold;">\2</p>', html)
    html = re.sub(r'<para fontSize="(\d+)">(.*?)</para>', r'<p style="font-size:\1px;">\2</p>', html)
    html = re.sub(r'<para>', '<p>', html)
    html = re.sub(r'</para>', '</p>', html)
    html = html.replace('<hr width="100%"/>', '<hr/>')
    return html.strip()

def markdown_to_html(text: str) -> str:
    text = re.sub(r'### (.*?)\s*\n?', r'<para fontSize="14"><b>\1</b></para><br/><br/>', text)
    text = re.sub(r'## (.*?)\s*\n?', r'<para fontSize="12"><b>\1</b></para><br/><br/>', text)
    text = re.sub(r'# (.*?)\s*\n?', r'<para fontSize="16"><b>\1</b></para><br/><br/>', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = re.sub(r'(?m)^\s*[-•] (.*?)$', r'• \1', text)
    text = text.replace("\n", "<br/>")  
    return text

def parse_markdown_table(md_table: str, temp_files: Optional[List[str]] = None) -> Table:
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
                        temp_files.append(resized_img)
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

def create_pdf_file(
    content: str, 
    output_pdf_path: str = "output.pdf", 
    font_name: str = "Times-Roman", 
    font_file: Optional[str] = "fonts/times.ttf",
    isDraft: bool = False
) -> str:
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
    temp_files = []

    try:
        paragraphs = content.split("\n\n")
        table_pattern = re.compile(r"(\|.+?\|(?:\n\|[-:]+[-|:]+\|)+\n(?:\|.+?\|\n?)+)")
        image_pattern = re.compile(r"!\[(.*?)\]\((.*?)\)")

        for para in paragraphs:
            if table_pattern.match(para):
                table = parse_markdown_table(para, temp_files)
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
                                temp_files.append(resized_img_path)
                    elif part.strip() == "---":
                        elements.append(HRFlowable(width="100%", thickness=1, color="black", spaceBefore=10, spaceAfter=10))
                    else:
                        elements.append(Paragraph(part, custom_style))

                story.append(KeepTogether(elements))
            story.append(Spacer(1, 12))
        if isDraft:
            doc.build(story, onFirstPage=add_watermark, onLaterPages=add_watermark)
        else:
            doc.build(story)

        return output_pdf_path

    finally:
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except Exception as e:
                pass

markdown_content = """
# RENTAL AGREEMENT

## BASIC RENTAL DETAILS

### OWNER DETAILS
- **Owner Name:** Sanjay Kulkarni
- **Owner Address:** 701, FC Road, Pune - 411005

### TENANT DETAILS
- **Name:** Ravi Sharma
  **Address:** 101, Kothrud, Pune - 411038
- **Name:** Akash Verma
  **Address:** 202, Viman Nagar, Pune - 411014
- **Name:** Siddharth Joshi
  **Address:** 303, Hinjewadi, Pune - 411057
- **Name:** Rohan Desai
  **Address:** 404, Baner, Pune - 411045

### PROPERTY DETAILS
- **Property Address:** Balewadi, Pune
- **City:** Pune
- **BHK Type:** 4BHK
- **Area:** 1600 sq. ft.
- **Furnishing Type:** semi-furnished

### Financial Details
- **Rent Amount:** Rs. 28000/month
- **Security Deposit:** Rs. 60000

### Term of Agreement
- The agreement is valid for 6 months, from 2025-04-01T10:00:00+00:00 to 2025-10-01T10:00:00+00:00.

### Registration Date
- **Registration Date:** The agreement was registered on **2025-04-01T10:00:00.000Z** in compliance with applicable legal requirements.

## TERMS AND CONDITIONS
### 1. License Fee
- **Rent Payment:** The monthly rent of **Rs. 28000** shall be paid in advance by the **1st of each month**. Any delay in payment beyond the due date may attract a **penalty fee** as specified in the agreement.

### 2. Deposit
- **Security Deposit:** A security deposit of **Rs. 60000** shall be collected prior to occupancy. This deposit will be refunded upon termination of the agreement after deducting any applicable damages or unpaid dues within a period of **30 days**.

### 3. Utilities
- **Responsibility for Bills:** Tenants shall be responsible for all utility bills including electricity, water, and internet services. Any shared costs must be agreed upon in advance and paid promptly to avoid disconnection.

### 4. Tenant Duties
- **Maintenance and Cleanliness:** Tenants are required to maintain the property in a clean and sanitary condition. Any damages caused by the tenants or their guests must be reported immediately, and tenants should refrain from engaging in activities that disturb the peace of the property.

### 5. Owner Rights
- **Property Access:** The owner reserves the right to inspect the property upon providing a **48-hour notice** to the tenants. Access shall be granted for maintenance and inspection purposes during reasonable hours.

### 6. Termination
- **Notice Period:** Either party may terminate the agreement with a **30-day written notice**. Early termination may incur penalties, and the security deposit will be refunded after assessing any damages.

### 7. Alterations
- **Modification Restrictions:** Tenants shall not make any alterations to the property without written consent from the owner. Any approved changes must be restored to the original condition upon termination of the agreement.

### 8. AMENITIES
- **Available Amenities:** The property includes amenities such as Parking, Lift, 24x7 Water Supply, Gym, and Security. Tenants must adhere to the usage rules for these amenities and are responsible for any maintenance required during their tenancy.


## Furniture and Appliances

| Sr. No. | Name              | Units |
|---------|-------------------|-------|
| 1       | Sofa       | 1     |
| 2       | Bed       | 4     |
| 3       | Dining Table       | 1     |
| 4       | Wardrobe       | 4     |



## Approval and Signature

| Name and Address               | Photo           | Signature           |  
|--------------------------------|-----------------|---------------------|  
| **Owner:**                     |                 |                     |  
| **Name:** Sanjay Kulkarni       | [OWNER PHOTO]   | [OWNER SIGNATURE]   |  
| **Address:** 701, FC Road, Pune - 411005 |                 |                     |  
|--------------------------------|-----------------|---------------------|  
| **Tenant 1:**                  |                 |                     |  
| **Name:** Ravi Sharma      | [TENANT 1 PHOTO]| [TENANT 1 SIGNATURE]|  
| **Address:** 101, Kothrud, Pune - 411038 |                 |                     |  
|--------------------------------|-----------------|---------------------|  
| **Tenant 2:**                  |                 |                     |  
| **Name:** Akash Verma      | [TENANT 2 PHOTO]| [TENANT 2 SIGNATURE]|  
| **Address:** 202, Viman Nagar, Pune - 411014 |                 |                     |  
|--------------------------------|-----------------|---------------------|  
| **Tenant 3:**                  |                 |                     |  
| **Name:** Siddharth Joshi      | [TENANT 3 PHOTO]| [TENANT 3 SIGNATURE]|  
| **Address:** 303, Hinjewadi, Pune - 411057 |                 |                     |  
|--------------------------------|-----------------|---------------------|  
| **Tenant 4:**                  |                 |                     |  
| **Name:** Rohan Desai      | [TENANT 4 PHOTO]| [TENANT 4 SIGNATURE]|  
| **Address:** 404, Baner, Pune - 411045 |                 |                     |  
|--------------------------------|-----------------|---------------------|
"""


create_pdf_file(markdown_content, "output.pdf")