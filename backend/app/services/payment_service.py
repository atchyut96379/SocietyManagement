import os
import uuid
from datetime import datetime

from app.config.society_config import get_upload_dir
from app.database.db import get_connection


def _generate_receipt_number() -> str:
    return f"RCP-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"


def _get_invoice_details(invoice_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            i.InvoiceID,
            i.ResidentID,
            i.Amount,
            i.Status,
            i.InvoiceMonth,
            i.InvoiceYear,
            r.FullName,
            r.FlatNumber,
            r.TowerName
        FROM MaintenanceInvoices i
        INNER JOIN Residents r ON i.ResidentID = r.ResidentID
        WHERE i.InvoiceID = ?
        """,
        (invoice_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "invoice_id": row[0],
        "resident_id": row[1],
        "amount": float(row[2]),
        "status": row[3],
        "month": row[4],
        "year": row[5],
        "resident_name": row[6],
        "flat_number": row[7],
        "tower_name": row[8]
    }


def record_payment(payment, recorded_by: int, payment_source: str = "Manual"):

    invoice = _get_invoice_details(payment.invoice_id)
    if not invoice:
        return {"success": False, "message": "Invoice not found"}

    if invoice["status"] == "Paid":
        return {"success": False, "message": "Invoice is already paid"}

    receipt_number = _generate_receipt_number()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO PaymentTransactions
        (InvoiceID, AmountPaid, PaymentMode, TransactionReference,
         RecordedBy, PaymentSource, ReceiptNumber, IsImmutable)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            payment.invoice_id,
            payment.amount_paid,
            payment.payment_mode,
            payment.transaction_reference,
            recorded_by,
            payment_source,
            receipt_number
        )
    )

    cursor.execute(
        "UPDATE MaintenanceInvoices SET Status = 'Paid' WHERE InvoiceID = ?",
        (payment.invoice_id,)
    )

    conn.commit()

    cursor.execute(
        "SELECT PaymentID FROM PaymentTransactions WHERE ReceiptNumber = ?",
        (receipt_number,)
    )
    payment_id = cursor.fetchone()[0]

    conn.close()

    return {
        "success": True,
        "message": "Payment recorded successfully",
        "payment_id": payment_id,
        "receipt_number": receipt_number
    }


def record_cash_payment(
    invoice_id: int,
    amount_paid: float,
    proof_path: str,
    resident_id: int,
    transaction_reference: str = None
):

    invoice = _get_invoice_details(invoice_id)
    if not invoice:
        return {"success": False, "message": "Invoice not found"}

    if invoice["resident_id"] != resident_id:
        return {"success": False, "message": "You can only pay your own invoices"}

    if invoice["status"] == "Paid":
        return {"success": False, "message": "Invoice is already paid"}

    if not proof_path:
        return {
            "success": False,
            "message": "Payment proof image is required for cash payments"
        }

    receipt_number = _generate_receipt_number()
    ref = transaction_reference or f"CASH-{receipt_number}"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO PaymentTransactions
        (InvoiceID, AmountPaid, PaymentMode, TransactionReference,
         PaymentSource, PaymentProofPath, ReceiptNumber, IsImmutable)
        VALUES (?, ?, 'Cash', ?, 'Cash', ?, ?, 1)
        """,
        (invoice_id, amount_paid, ref, proof_path, receipt_number)
    )

    cursor.execute(
        "UPDATE MaintenanceInvoices SET Status = 'Paid' WHERE InvoiceID = ?",
        (invoice_id,)
    )

    conn.commit()

    cursor.execute(
        "SELECT PaymentID FROM PaymentTransactions WHERE ReceiptNumber = ?",
        (receipt_number,)
    )
    payment_id = cursor.fetchone()[0]

    conn.close()

    return {
        "success": True,
        "message": "Cash payment recorded with proof",
        "payment_id": payment_id,
        "receipt_number": receipt_number
    }


def create_gateway_payment_link(invoice_id: int, resident_id: int):

    invoice = _get_invoice_details(invoice_id)
    if not invoice:
        return {"success": False, "message": "Invoice not found"}

    if invoice["resident_id"] != resident_id:
        return {"success": False, "message": "You can only pay your own invoices"}

    if invoice["status"] == "Paid":
        return {"success": False, "message": "Invoice is already paid"}

    gateway_ref = f"GW-{uuid.uuid4().hex[:12].upper()}"
    base_url = os.getenv("PAYMENT_GATEWAY_URL", "https://pay.example.com/checkout")
    api_base = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

    payment_link = (
        f"{base_url}?ref={gateway_ref}"
        f"&amount={invoice['amount']}"
        f"&invoice_id={invoice_id}"
    )

    return {
        "success": True,
        "payment_link": payment_link,
        "gateway_reference": gateway_ref,
        "amount": invoice["amount"],
        "invoice_id": invoice_id,
        "callback_url": f"{api_base}/payment/webhook",
        "note": "Complete payment on the gateway. Receipt will be generated automatically."
    }


def process_gateway_webhook(gateway_reference: str, invoice_id: int, amount_paid: float):

    invoice = _get_invoice_details(invoice_id)
    if not invoice:
        return {"success": False, "message": "Invoice not found"}

    if invoice["status"] == "Paid":
        return {"success": False, "message": "Invoice already paid"}

    receipt_number = _generate_receipt_number()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO PaymentTransactions
        (InvoiceID, AmountPaid, PaymentMode, TransactionReference,
         PaymentSource, GatewayTransactionId, ReceiptNumber, IsImmutable)
        VALUES (?, ?, 'Online', ?, 'Gateway', ?, ?, 1)
        """,
        (
            invoice_id,
            amount_paid,
            gateway_reference,
            gateway_reference,
            receipt_number
        )
    )

    cursor.execute(
        "UPDATE MaintenanceInvoices SET Status = 'Paid' WHERE InvoiceID = ?",
        (invoice_id,)
    )

    conn.commit()

    cursor.execute(
        "SELECT PaymentID FROM PaymentTransactions WHERE ReceiptNumber = ?",
        (receipt_number,)
    )
    payment_id = cursor.fetchone()[0]

    conn.close()

    return {
        "success": True,
        "message": "Gateway payment confirmed",
        "payment_id": payment_id,
        "receipt_number": receipt_number
    }


def get_payment_receipt(payment_id: int, resident_id: int = None):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            p.PaymentID,
            p.InvoiceID,
            p.AmountPaid,
            p.PaymentMode,
            p.TransactionReference,
            p.PaymentDate,
            p.ReceiptNumber,
            p.PaymentSource,
            p.PaymentProofPath,
            i.InvoiceMonth,
            i.InvoiceYear,
            r.FullName,
            r.FlatNumber,
            r.TowerName,
            r.ResidentID
        FROM PaymentTransactions p
        INNER JOIN MaintenanceInvoices i ON p.InvoiceID = i.InvoiceID
        INNER JOIN Residents r ON i.ResidentID = r.ResidentID
        WHERE p.PaymentID = ?
        """,
        (payment_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    if resident_id and row[14] != resident_id:
        return None

    return {
        "payment_id": row[0],
        "invoice_id": row[1],
        "amount_paid": float(row[2]),
        "payment_mode": row[3],
        "transaction_reference": row[4],
        "payment_date": str(row[5]),
        "receipt_number": row[6],
        "payment_source": row[7],
        "has_proof": bool(row[8]),
        "invoice_month": row[9],
        "invoice_year": row[10],
        "resident_name": row[11],
        "flat_number": row[12],
        "tower_name": row[13]
    }


def get_payment_history():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            p.PaymentID,
            p.InvoiceID,
            p.AmountPaid,
            p.PaymentMode,
            p.TransactionReference,
            p.PaymentDate,
            u.FullName,
            p.ReceiptNumber,
            p.PaymentSource
        FROM PaymentTransactions p
        LEFT JOIN Users u ON p.RecordedBy = u.UserID
        ORDER BY p.PaymentID DESC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "payment_id": row[0],
            "invoice_id": row[1],
            "amount_paid": float(row[2]),
            "payment_mode": row[3],
            "transaction_reference": row[4],
            "payment_date": str(row[5]),
            "recorded_by": row[6] or "System",
            "receipt_number": row[7],
            "payment_source": row[8]
        }
        for row in rows
    ]


def save_payment_proof(file_content: bytes, filename: str) -> str:

    upload_dir = os.path.join(get_upload_dir(), "payments")
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(filename)[1] or ".jpg"
    safe_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, safe_name)

    with open(file_path, "wb") as f:
        f.write(file_content)

    return file_path
