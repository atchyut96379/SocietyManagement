import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def create_receipt_pdf(receipt_dir: str, receipt_number: str, payment_data: dict) -> str:
    os.makedirs(receipt_dir, exist_ok=True)

    filename = f"{receipt_number}.pdf"
    path = os.path.join(receipt_dir, filename)

    pdf = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    y = height - 80

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(72, y, "Society Management - Payment Receipt")

    y -= 40
    pdf.setFont("Helvetica", 11)

    lines = [
        f"Receipt No: {receipt_number}",
        f"Date: {payment_data.get('payment_date', datetime.utcnow().strftime('%d-%m-%Y %H:%M'))}",
        f"Invoice ID: {payment_data['invoice_id']}",
        f"Flat Number: {payment_data.get('flat_number', '')}",
        f"Resident: {payment_data.get('resident_name', '')}",
        f"Amount Paid: INR {payment_data['amount_paid']:.2f}",
        f"Payment Source: {payment_data.get('payment_source', '')}",
        f"Transaction Ref: {payment_data.get('transaction_reference', '')}",
        f"Gateway Payment ID: {payment_data.get('gateway_payment_id', 'N/A')}",
        "",
        "This is an auto-generated receipt.",
        "Payment records are immutable and cannot be modified.",
    ]

    for line in lines:
        pdf.drawString(72, y, line)
        y -= 22

    pdf.line(72, y, width - 72, y)
    y -= 30
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(72, y, "Thank you for your payment.")

    pdf.save()
    return path
