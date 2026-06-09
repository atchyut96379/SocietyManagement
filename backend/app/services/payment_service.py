import os
import uuid
from datetime import datetime

from app.config.accounts import normalize_account
from app.database.db import get_connection
from app.services.razorpay_service import (
    create_order,
    generate_test_signature,
    verify_signature,
)

UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "uploads",
    "payment_proofs"
)

RECEIPT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "uploads",
    "receipts"
)


def _ensure_dirs():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(RECEIPT_DIR, exist_ok=True)


def _generate_receipt_number() -> str:
    return f"RCP-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"


def _get_invoice_details(invoice_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            i.InvoiceID, i.Amount, i.Status, i.ResidentID,
            r.FullName, r.FlatNumber
        FROM MaintenanceInvoices i
        INNER JOIN Residents r ON i.ResidentID = r.ResidentID
        WHERE i.InvoiceID = ?
    """, invoice_id)

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "invoice_id": row[0],
        "amount": float(row[1]),
        "status": row[2],
        "resident_id": row[3],
        "resident_name": row[4],
        "flat_number": row[5],
    }


def _invoice_already_paid(invoice_id: int) -> bool:
    invoice = _get_invoice_details(invoice_id)
    return invoice is not None and invoice["status"] == "Paid"


def _create_receipt_file(receipt_number: str, payment_data: dict) -> str:
    _ensure_dirs()
    from app.services.receipt_pdf import create_receipt_pdf

    return create_receipt_pdf(RECEIPT_DIR, receipt_number, payment_data)


def _record_immutable_payment(
    invoice_id: int,
    amount_paid: float,
    payment_source: str,
    transaction_reference: str,
    recorded_by: int | None,
    proof_image_path: str | None = None,
    gateway_order_id: str | None = None,
    gateway_payment_id: str | None = None,
    credit_account: str | None = None,
):
    if _invoice_already_paid(invoice_id):
        return {
            "success": False,
            "message": "Invoice is already paid"
        }

    invoice = _get_invoice_details(invoice_id)
    if not invoice:
        return {"success": False, "message": "Invoice not found"}

    receipt_number = _generate_receipt_number()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO PaymentTransactions
        (
            InvoiceID, AmountPaid, PaymentMode, TransactionReference,
            RecordedBy, PaymentSource, ProofImagePath, ReceiptNumber,
            GatewayOrderId, GatewayPaymentId, IsImmutable, CreditAccount
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        """,
        (
            invoice_id,
            amount_paid,
            "Razorpay" if payment_source == "Gateway" else "Cash",
            transaction_reference,
            recorded_by,
            payment_source,
            proof_image_path,
            receipt_number,
            gateway_order_id,
            gateway_payment_id,
            normalize_account(credit_account),
        )
    )

    cursor.execute(
        "SELECT @@IDENTITY"
    )
    payment_id = int(cursor.fetchone()[0])

    cursor.execute(
        """
        UPDATE MaintenanceInvoices
        SET Status = 'Paid'
        WHERE InvoiceID = ?
        """,
        invoice_id
    )

    conn.commit()
    conn.close()

    receipt_path = _create_receipt_file(
        receipt_number,
        {
            "invoice_id": invoice_id,
            "amount_paid": amount_paid,
            "payment_source": payment_source,
            "transaction_reference": transaction_reference,
            "gateway_payment_id": gateway_payment_id,
            "flat_number": invoice["flat_number"],
            "resident_name": invoice["resident_name"],
            "payment_date": datetime.utcnow().isoformat(),
        }
    )

    return {
        "success": True,
        "message": "Payment recorded successfully",
        "payment_id": payment_id,
        "receipt_number": receipt_number,
        "receipt_path": receipt_path,
    }


def create_payment_order(invoice_id: int, resident_id: int | None = None):
    invoice = _get_invoice_details(invoice_id)

    if not invoice:
        return {"success": False, "message": "Invoice not found"}

    if invoice["status"] == "Paid":
        return {"success": False, "message": "Invoice is already paid"}

    if resident_id and invoice["resident_id"] != resident_id:
        return {
            "success": False,
            "message": "You can only pay your own invoices"
        }

    return create_order(
        invoice_id=invoice_id,
        amount=invoice["amount"],
        resident_name=invoice["resident_name"],
        flat_number=invoice["flat_number"],
    )


def verify_and_record_gateway_payment(
    invoice_id: int,
    order_id: str,
    payment_id: str,
    signature: str,
    resident_id: int | None = None,
):
    invoice = _get_invoice_details(invoice_id)

    if not invoice:
        return {"success": False, "message": "Invoice not found"}

    if resident_id and invoice["resident_id"] != resident_id:
        return {
            "success": False,
            "message": "You can only pay your own invoices"
        }

    if not verify_signature(order_id, payment_id, signature):
        return {"success": False, "message": "Payment verification failed"}

    return _record_immutable_payment(
        invoice_id=invoice_id,
        amount_paid=invoice["amount"],
        payment_source="Gateway",
        transaction_reference=payment_id,
        recorded_by=None,
        gateway_order_id=order_id,
        gateway_payment_id=payment_id,
    )


def record_cash_payment(
    invoice_id: int,
    amount_paid: float,
    transaction_reference: str,
    recorded_by: int,
    proof_file_content: bytes,
    proof_filename: str,
    credit_account: str = "Maintenance",
):
    invoice = _get_invoice_details(invoice_id)

    if not invoice:
        return {"success": False, "message": "Invoice not found"}

    _ensure_dirs()

    ext = os.path.splitext(proof_filename)[1] or ".jpg"
    proof_name = f"cash_{invoice_id}_{uuid.uuid4().hex[:8]}{ext}"
    proof_path = os.path.join(UPLOAD_DIR, proof_name)

    with open(proof_path, "wb") as file:
        file.write(proof_file_content)

    return _record_immutable_payment(
        invoice_id=invoice_id,
        amount_paid=amount_paid,
        payment_source="Cash",
        transaction_reference=transaction_reference,
        recorded_by=recorded_by,
        proof_image_path=proof_path,
        credit_account=credit_account,
    )


def get_payment_history():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            p.PaymentID,
            p.InvoiceID,
            p.AmountPaid,
            p.PaymentMode,
            p.TransactionReference,
            p.PaymentDate,
            p.PaymentSource,
            p.ReceiptNumber,
            p.ProofImagePath,
            p.GatewayPaymentId,
            p.IsImmutable,
            ISNULL(p.CreditAccount, 'Maintenance'),
            u.FullName,
            r.FlatNumber,
            r.FullName
        FROM PaymentTransactions p
        INNER JOIN MaintenanceInvoices i ON p.InvoiceID = i.InvoiceID
        INNER JOIN Residents r ON i.ResidentID = r.ResidentID
        LEFT JOIN Users u ON p.RecordedBy = u.UserID
        ORDER BY p.PaymentID DESC
    """)

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
            "payment_source": row[6],
            "receipt_number": row[7],
            "proof_image_path": row[8],
            "gateway_payment_id": row[9],
            "is_immutable": bool(row[10]),
            "credit_account": row[11],
            "recorded_by": row[12] or "System",
            "flat_number": row[13],
            "resident_name": row[14],
        }
        for row in rows
    ]


def get_receipt_path(payment_id: int, resident_id: int | None = None):
    conn = get_connection()
    cursor = conn.cursor()

    if resident_id:
        cursor.execute("""
            SELECT p.ReceiptNumber
            FROM PaymentTransactions p
            INNER JOIN MaintenanceInvoices i ON p.InvoiceID = i.InvoiceID
            WHERE p.PaymentID = ? AND i.ResidentID = ?
        """, (payment_id, resident_id))
    else:
        cursor.execute(
            "SELECT ReceiptNumber FROM PaymentTransactions WHERE PaymentID = ?",
            payment_id
        )

    row = cursor.fetchone()
    conn.close()

    if not row or not row[0]:
        return None

    receipt_number = row[0]
    pdf_path = os.path.join(RECEIPT_DIR, f"{receipt_number}.pdf")

    if os.path.exists(pdf_path):
        return pdf_path

    return None


def get_test_payment_credentials(invoice_id: int, resident_id: int):
    order = create_payment_order(invoice_id, resident_id)

    if not order.get("success"):
        return order

    test_payment_id = f"pay_test_{uuid.uuid4().hex[:12]}"
    test_signature = generate_test_signature(
        order["order_id"],
        test_payment_id
    )

    return {
        **order,
        "test_payment_id": test_payment_id,
        "test_signature": test_signature,
    }
