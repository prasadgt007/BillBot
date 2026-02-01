import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from reportlab.graphics import renderPDF


def generate_pdf(data, filename, company_details=None):
    """
    Generate a professional invoice PDF with GST calculations.
    
    Args:
        data (dict): Order data with structure:
            {
                'customer': str,
                'items': [
                    {'name': str, 'qty': int, 'rate': float}
                ]
            }
        filename (str): Name of the PDF file (without path)
        company_details (dict, optional): Company information:
            {
                'name': str,
                'address': str,
                'gstin': str,
                'logo_path': str
            }
    
    Returns:
        str: Full path to the generated PDF file
    """
    # Default company details if none provided
    if not company_details:
        company_details = {
            'name': 'BillBot Services',
            'address': '123 Business Street, City, State - 123456',
            'gstin': '29XXXXX1234X1ZX'
        }
    
    # Ensure static folder exists
    static_folder = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_folder, exist_ok=True)
    
    # Full path for the PDF
    pdf_path = os.path.join(static_folder, filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#283593'),
        spaceAfter=12
    )
    
    normal_style = styles['Normal']
    
    # Invoice Header
    elements.append(Paragraph("INVOICE", title_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Company/Business Info from database
    company_name = company_details.get('name', 'BillBot Services')
    company_address = company_details.get('address', 'N/A')
    company_gstin = company_details.get('gstin', 'N/A')
    
    elements.append(Paragraph(f"<b>{company_name}</b>", heading_style))
    if company_address and company_address != 'N/A':
        elements.append(Paragraph(company_address, normal_style))
    if company_gstin and company_gstin != 'N/A':
        elements.append(Paragraph(f"GSTIN: {company_gstin}", normal_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Customer and Invoice Details
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    invoice_date = datetime.now().strftime('%d-%b-%Y')
    
    customer_info = [
        [Paragraph("<b>Bill To:</b>", normal_style), Paragraph(f"<b>Invoice #:</b> {invoice_number}", normal_style)],
        [Paragraph(f"<b>{data.get('customer', 'N/A')}</b>", normal_style), Paragraph(f"<b>Date:</b> {invoice_date}", normal_style)]
    ]
    
    customer_table = Table(customer_info, colWidths=[3.5 * inch, 3.5 * inch])
    customer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 0.4 * inch))
    
    # Prepare table data
    table_data = [
        ['Item', 'Qty', 'Rate', 'Tax (18%)', 'Total']
    ]
    
    # Tax rates
    CGST_RATE = 0.09  # 9%
    SGST_RATE = 0.09  # 9%
    TOTAL_TAX_RATE = CGST_RATE + SGST_RATE  # 18%
    
    subtotal = 0
    total_tax = 0
    
    # Process items
    for item in data.get('items', []):
        item_name = item.get('name', 'Unknown Item')
        qty = item.get('qty', 1)
        rate = item.get('rate', 0.0)
        
        # Calculate amounts
        item_subtotal = qty * rate
        item_tax = item_subtotal * TOTAL_TAX_RATE
        item_total = item_subtotal + item_tax
        
        # Add to running totals
        subtotal += item_subtotal
        total_tax += item_tax
        
        # Add row to table (using Rs. instead of ₹ for better PDF compatibility)
        table_data.append([
            item_name,
            str(qty),
            f"Rs. {rate:.2f}",
            f"Rs. {item_tax:.2f}",
            f"Rs. {item_total:.2f}"
        ])
    
    # Calculate grand total
    grand_total = subtotal + total_tax
    
    # Add tax breakdown and totals (using Rs. for better PDF compatibility)
    table_data.append(['', '', '', '', ''])
    table_data.append(['', '', 'Subtotal:', '', f"Rs. {subtotal:.2f}"])
    table_data.append(['', '', f'CGST (9%):', '', f"Rs. {subtotal * CGST_RATE:.2f}"])
    table_data.append(['', '', f'SGST (9%):', '', f"Rs. {subtotal * SGST_RATE:.2f}"])
    table_data.append(['', '', 'Total Tax:', '', f"Rs. {total_tax:.2f}"])
    table_data.append(['', '', Paragraph('<b>Grand Total:</b>', normal_style), '', Paragraph(f"<b>Rs. {grand_total:.2f}</b>", normal_style)])
    
    # Create table
    item_table = Table(table_data, colWidths=[2.8 * inch, 0.8 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch])
    
    # Style the table
    table_style = TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#283593')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -7), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        
        # Grid
        ('GRID', (0, 0), (-1, -7), 1, colors.HexColor('#bdbdbd')),
        ('LINEBELOW', (0, -7), (-1, -7), 1, colors.HexColor('#bdbdbd')),
        
        # Totals section
        ('FONTNAME', (0, -6), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (2, -6), (-1, -6), 1, colors.HexColor('#757575')),
        
        # Grand total row
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e3f2fd')),
        ('LINEABOVE', (2, -1), (-1, -1), 2, colors.HexColor('#283593')),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        
        # Alternating row colors for items
        ('ROWBACKGROUNDS', (0, 1), (-1, -7), [colors.white, colors.HexColor('#f5f5f5')]),
    ])
    
    item_table.setStyle(table_style)
    elements.append(item_table)
    
    # Footer
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("<i>Thank you for your business!</i>", normal_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("This is a computer generated invoice.", 
                             ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.grey)))
    
    # Build PDF with barcode
    def add_barcode(canvas_obj, doc_obj):
        """
        Add barcode to the top-right corner of the PDF
        """
        # Extract barcode data from filename (remove .pdf extension)
        barcode_data = filename.replace('.pdf', '')
        
        # Create Code128 barcode
        barcode = code128.Code128(barcode_data, barWidth=0.8, barHeight=30)
        
        # Draw barcode at top-right corner with padding (360, 780)
        barcode.drawOn(canvas_obj, 360, 780)
    
    doc.build(elements, onFirstPage=add_barcode, onLaterPages=add_barcode)
    
    print(f"Invoice generated successfully: {pdf_path}")
    return pdf_path


# Example usage
if __name__ == "__main__":
    # Test data
    sample_data = {
        "customer": "John Doe",
        "items": [
            {"name": "Premium Widget", "qty": 2, "rate": 500.0},
            {"name": "Standard Gadget", "qty": 5, "rate": 200.0},
            {"name": "Deluxe Service", "qty": 1, "rate": 1500.0}
        ]
    }
    
    generate_pdf(sample_data, "test_invoice.pdf")
    print("Test invoice created in static folder!")
