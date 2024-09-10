from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
import base64

def generate_exact_payslip_pdf(employee):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontName='Times-Roman',  # Specify the font name
        fontSize=22,
        alignment=1,  # Center align
    )
    address_style = ParagraphStyle(
        'Address',
        parent=styles['Normal'],
        fontSize=9,  # Decreased font size for address
        alignment=1,  # Center align
    )
    normal_style = styles['Normal']
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=1,  # Center align
    )

    # Helper function to safely get attribute values
    def get_attr(attr, default="N/A"):
        return getattr(employee, attr, default)

    logo = Image("sun_1.jpg", width=2.0*inch, height=0.6*inch)
    logo_space = Spacer(1, 0.5*inch)  # Spacer to move logo right

    # Create a table with the logo and company details
    logo_table_data = [
        [logo, Paragraph("Sun E-Learning", title_style)],
        ["", Paragraph("Dwaraka Pride, Huda Enclave Hitech City, Madhapur, Hyderabad-500081", address_style)],
    ]

    logo_table = Table(logo_table_data, colWidths=[2.0*inch, 5.0*inch])
    logo_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ('ALIGN', (1, 1), (1, 1), 'RIGHT'),
        ('TOPPADDING', (1, 0), (1, 0), 0),  # Move logo down
        ('LEFTPADDING', (0, 0), (-1, -1), 50),  # Adds 10 units of padding to the left side of all cells
        # ('BOTTOMPADDING', (0, 0), (-1, -1), 2) # Adds 5 units of padding to the bottom of all cells

]))

    elements.append(logo_table)
    elements.append(Spacer(1, 0.25*inch))

    # Title
    elements.append(Paragraph("Salary Slip", title_style))
    elements.append(Spacer(1, 0.25*inch))

    # Employee Details Table
    employee_data = [
        ["Employee ID", get_attr('employee_id', '#N/A'), "Employee Name", get_attr('employee_name', '#N/A')],
        ["Designation", get_attr('designation', '#N/A'), "Month/Year", f"{get_attr('month_year', '#N/A')}"],
        ["Date of Joining", get_attr('date_of_joining', '#N/A'), "PAN Card", get_attr('pan_card', '#N/A')],
    ]

    employee_table = Table(employee_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    employee_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        
    ]))
    elements.append(employee_table)
    elements.append(Spacer(1, 0.25*inch))

    # Earnings and Deductions Table
    earnings_deductions_data = [
        ["Earnings", "", "Deductions", ""],
        ["Basic Pay", get_attr('basic_pay', '#N/A'), "Provident Fund", get_attr('provident_fund', '0')],
        ["HRA", get_attr('hra', '#N/A'), "ESI", get_attr('esi', '#N/A')],
        ["LTA", get_attr('lta', '#N/A'), "Professional Tax", get_attr('professional_tax', '#N/A')],
        ["Other Allowance", get_attr('other_allowance', '#N/A'), "Tax", get_attr('tax', '0')],
        ["Total Addition", get_attr('total_addition', '#N/A'), "Total Deductions", get_attr('total_deductions', '0')],
    ]

    earnings_deductions_table = Table(earnings_deductions_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    earnings_deductions_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),  # Header for Earnings
        ('BACKGROUND', (2, 0), (3, 0), colors.lightgrey),
        ('SPAN', (0, 0), (1, 0)),  # Merge cells for "Earnings" heading
        ('SPAN', (2, 0), (3, 0)),  # Merge cells for "Deductions" heading
        ('ALIGN', (0, 0), (3, 0), 'CENTER'),  # Center align the headers
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        
    ]))
    elements.append(earnings_deductions_table)
    elements.append(Spacer(1, 0.25*inch))

    #  Additional Details
    additional_data = [
        ["No of days worked this month",get_attr('days_worked', "#N/A")],
        ["Net Salary", get_attr('net_salary', '#N/A')],
        ["Salary in words", get_attr('salary_in_words','#N/A')],
    ]

    additional_table = Table(additional_data, colWidths=[2*inch, 4*inch])
    additional_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    elements.append(additional_table)

    # Footer
    footer_text = "This is a computer-generated copy. Salary Paid By: Cash, Bank Transfer ✔️,  Cheque"
    elements.append(Spacer(1, 0.55*inch))
    elements.append(Paragraph(footer_text, footer_style))


    # # Net Salary
    # elements.append(Paragraph(f"Net Salary: {get_attr('net_salary', '0')}", normal_style))
    # elements.append(Spacer(1, 0.25*inch))

    # Save the PDF
    doc.build(elements)
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()

    # Encode PDF to base64
    pdf_base64 = base64.b64encode(pdf).decode('utf-8')
    return f'<a href="data:application/pdf;base64,{pdf_base64}" download="payslip.pdf">Download Payslip</a>'


# from reportlab.lib import colors
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, Flowable
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from reportlab.lib.pagesizes import legal

# from io import BytesIO
# import base64

# class BorderedPage(Flowable):
#     def __init__(self, width, height):
#         Flowable.__init__(self)
#         self.width = width
#         self.height = height

#     def draw(self):
#         # Draw the border slightly inside the frame
#         inset = 1  # 1 point inset
#         self.canv.rect(inset, inset, self.width - 2*inset, self.height - 2*inset)

# def generate_exact_payslip_pdf(employee):
#     buffer = BytesIO()

#     custom_page_size = (8.5*inch, 14*inch)  # Using legal size paper
#     doc = SimpleDocTemplate(buffer, pagesize=custom_page_size, topMargin=0.2*inch, bottomMargin=0.2*inch, leftMargin=0.2*inch, rightMargin=0.2*inch)
#     elements = []

#     page_width, page_height = custom_page_size
#     frame_width = page_width - 0.4*inch  # Subtracting left and right margins
#     frame_height = page_height - 0.4*inch  # Subtracting top and bottom margins
#     elements.append(BorderedPage(frame_width, frame_height))


#     # Rest of the code remains the same...
#     # Styles
#     styles = getSampleStyleSheet()
#     title_style = ParagraphStyle(
#         'Title',
#         parent=styles['Heading1'],
#         fontName='Times-Roman',
#         fontSize=22,
#         alignment=1,
#     )
#     address_style = ParagraphStyle(
#         'Address',
#         parent=styles['Normal'],
#         fontSize=9,
#         alignment=1,
#     )
#     normal_style = styles['Normal']
#     footer_style = ParagraphStyle(
#         'Footer',
#         parent=styles['Normal'],
#         fontSize=8,
#         alignment=1,
#     )

#     # Helper function to safely get attribute values
#     def get_attr(attr, default="N/A"):
#         return getattr(employee, attr, default)

#     logo = Image("sun_1.jpg", width=2.0*inch, height=0.6*inch)
#     logo_space = Spacer(1, 0.5*inch)

#     # Create a table with the logo and company details
#     logo_table_data = [
#         [logo, Paragraph("Sun E-Learning", title_style)],
#         ["", Paragraph("Dwaraka Pride, Huda Enclave Hitech City, Madhapur, Hyderabad-500081", address_style)],
#     ]

#     logo_table = Table(logo_table_data, colWidths=[2.0*inch, 5.0*inch])
#     logo_table.setStyle(TableStyle([
#         ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
#         ('ALIGN', (0, 0), (0, 0), 'CENTER'),
#         ('ALIGN', (1, 0), (1, 0), 'LEFT'),
#         ('ALIGN', (1, 1), (1, 1), 'RIGHT'),
#         ('TOPPADDING', (1, 0), (1, 0), 0),
#         ('LEFTPADDING', (0, 0), (-1, -1), 50),
#     ]))

#     elements.append(logo_table)
#     elements.append(Spacer(1, 0.25*inch))

#     # Title
#     elements.append(Paragraph("Salary Slip", title_style))
#     elements.append(Spacer(1, 0.25*inch))

#     # Employee Details Table
#     employee_data = [
#         ["Employee ID", get_attr('employee_id', '#N/A'), "Employee Name", get_attr('employee_name', '#N/A')],
#         ["Designation", get_attr('designation', '#N/A'), "Month/Year", f"{get_attr('month_year', '#N/A')}"],
#         ["Date of Joining", get_attr('date_of_joining', '#N/A'), "PAN Card", get_attr('pan_card', '#N/A')],
#     ]

#     employee_table = Table(employee_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
#     employee_table.setStyle(TableStyle([
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#         ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
#         ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
#     ]))
#     elements.append(employee_table)
#     elements.append(Spacer(1, 0.25*inch))

#     # Earnings and Deductions Table
#     earnings_deductions_data = [
#         ["Earnings", "", "Deductions", ""],
#         ["Basic Pay", get_attr('basic_pay', '#N/A'), "Provident Fund", get_attr('provident_fund', '0')],
#         ["HRA", get_attr('hra', '#N/A'), "ESI", get_attr('esi', '#N/A')],
#         ["LTA", get_attr('lta', '#N/A'), "Professional Tax", get_attr('professional_tax', '#N/A')],
#         ["Other Allowance", get_attr('other_allowance', '#N/A'), "Tax", get_attr('tax', '0')],
#         ["Total Addition", get_attr('total_addition', '#N/A'), "Total Deductions", get_attr('total_deductions', '0')],
#     ]

#     earnings_deductions_table = Table(earnings_deductions_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
#     earnings_deductions_table.setStyle(TableStyle([
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#         ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
#         ('BACKGROUND', (2, 0), (3, 0), colors.lightgrey),
#         ('SPAN', (0, 0), (1, 0)),
#         ('SPAN', (2, 0), (3, 0)),
#         ('ALIGN', (0, 0), (3, 0), 'CENTER'),
#         ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
#     ]))
#     elements.append(earnings_deductions_table)
#     elements.append(Spacer(1, 0.25*inch))

#     # Additional Details
#     additional_data = [
#         ["No of days worked this month", get_attr('days_worked', "#N/A")],
#         ["Net Salary", get_attr('net_salary', '#N/A')],
#         ["Salary in words", get_attr('salary_in_words', '#N/A')],
#     ]

#     additional_table = Table(additional_data, colWidths=[2*inch, 4*inch])
#     additional_table.setStyle(TableStyle([
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#         ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
#     ]))
#     elements.append(additional_table)

#     # Footer
#     footer_text = "This is a computer-generated copy. Salary Paid By: Cash, Bank Transfer ✔️,  Cheque"
#     elements.append(Spacer(1, 0.55*inch))
#     elements.append(Paragraph(footer_text, footer_style))

#     # Save the PDF
#     doc.build(elements)
#     buffer.seek(0)
#     pdf = buffer.getvalue()
#     buffer.close()

#     # Encode PDF to base64
#     pdf_base64 = base64.b64encode(pdf).decode('utf-8')
#     return f'<a href="data:application/pdf;base64,{pdf_base64}" download="payslip.pdf">Download Payslip</a>'