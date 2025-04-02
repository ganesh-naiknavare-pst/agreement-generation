from typing import Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import re

def doc_template(output_pdf_path):
    return SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

def get_styles(font_name, font_file):
    styles = getSampleStyleSheet()
    custom_styles = {
        "heading1": ParagraphStyle(name='CustomHeading1', parent=styles['Heading1'], fontName=font_name if font_file else "Helvetica", fontSize=16, spaceAfter=2),
        "heading2": ParagraphStyle(name='CustomHeading2', parent=styles['Heading2'], fontName=font_name if font_file else "Helvetica", fontSize=14, spaceAfter=2),
        "heading3": ParagraphStyle(name='CustomHeading3', parent=styles['Heading3'], fontName=font_name if font_file else "Helvetica", fontSize=12, spaceAfter=2),
        "bullet": ParagraphStyle(name='CustomBullet', parent=styles['Normal'], fontName=font_name if font_file else "Helvetica", leftIndent=12, spaceAfter=5),
        "normal": ParagraphStyle(name='CustomNormal', parent=styles['Normal'], fontName=font_name if font_file else "Helvetica", fontSize=10, spaceAfter=2),
    }
    return custom_styles

def process_heading(line, custom_styles):
    if line.startswith('# '):
        return Paragraph(line[2:], custom_styles['heading1']), Spacer(1, 6)
    elif line.startswith('## '):
        return Paragraph(line[3:], custom_styles['heading2']), Spacer(1, 4)
    elif line.startswith('### '):
        return Paragraph(line[4:], custom_styles['heading3']), Spacer(1, 2)
    return None

def process_bullet(line, custom_styles):
    content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line[2:])
    return Paragraph('• ' + content, custom_styles['bullet'])

def process_table(lines, index, custom_styles, doc):
    table_data = []
    header_row = [cell.strip() for cell in lines[index].split('|')[1:-1]]
    table_data.append([Paragraph(h, custom_styles['normal']) for h in header_row])
    index += 2
    
    while index < len(lines) and lines[index].startswith('|'):
        row_cells = [re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', cell.strip()) for cell in lines[index].split('|')[1:-1]]
        table_data.append([Paragraph(cell, custom_styles['normal']) for cell in row_cells])
        index += 1
    
    col_width = doc.width / len(header_row)
    table = Table(table_data, colWidths=[col_width] * len(header_row))
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    return table, Spacer(1, 12), index - 1

def create_pdf_file(
    content: str, 
    output_pdf_path: str = "output.pdf", 
    font_name: str = "Times-Roman", 
    font_file: Optional[str] = "fonts/times.ttf",
    isDraft: bool = False
) -> str:
    doc = doc_template(output_pdf_path)
    custom_styles = get_styles(font_name, font_file)
    elements = []
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        if heading := process_heading(line, custom_styles):
            elements.extend(heading)
        elif line.startswith('- '):
            elements.append(process_bullet(line, custom_styles))
        elif line.startswith('|') and i + 2 < len(lines) and lines[i+1].startswith('|---'):
            table, spacer, i = process_table(lines, i, custom_styles, doc)
            elements.append(table)
            elements.append(spacer)
        elif line:
            line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            elements.append(Paragraph(line, custom_styles['normal']))
            elements.append(Spacer(1, 6))
        
        i += 1
    
    
    doc.build(elements)
    print(f"PDF created successfully at {output_pdf_path}")

# Example usage
if __name__ == "__main__":
    # For actual usage with the provided markdown
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

| Name & Address                                    | Photo           | Signature           |  
|--------------------------------------------------|-----------------|---------------------|  
|**Owner:**<br/>**Name:** Sanjay Kulkarni<br/>**Address:**701, FC Road, Pune - 411005 | [OWNER PHOTO]   | [OWNER SIGNATURE]   |  
|**Tenant 1**:<br/>**Name:**Ravi Sharma<br/>**Address:**101, Kothrud, Pune - 411038  | [TENANT 1 PHOTO] | [TENANT 1 SIGNATURE] |  
|**Tenant 2:**<br/>**Name:**Akash Verma<br/>**Address:**202, Viman Nagar, Pune - 411014 | [TENANT 2 PHOTO] | [TENANT 2 SIGNATURE] |  
|**Tenant 3:**<br/>**Name:**Siddharth Joshi<br/>**Address:**303, Hinjewadi, Pune - 411057 | [TENANT 3 PHOTO] | [TENANT 3 SIGNATURE] |  
|**Tenant 4:**<br/>**Name:**Rohan Desai<br/>**Address:**404, Baner, Pune - 411045 | [TENANT 4 PHOTO] | [TENANT 4 SIGNATURE] |  
 
"""
    
    create_pdf_file(markdown_content, "rental_agreement.pdf")