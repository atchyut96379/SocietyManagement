from app.database.db import get_connection


def record_payment(payment, recorded_by: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO PaymentTransactions
        (
            InvoiceID,
            AmountPaid,
            PaymentMode,
            TransactionReference,
            RecordedBy
        )
        VALUES (?, ?, ?, ?, ?)
    """,
    (
        payment.invoice_id,
        payment.amount_paid,
        payment.payment_mode,
        payment.transaction_reference,
        recorded_by
    ))

    cursor.execute("""
        UPDATE MaintenanceInvoices
        SET Status = 'Paid'
        WHERE InvoiceID = ?
    """,
    payment.invoice_id)

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Payment recorded successfully"
    }


def delete_payment(payment_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT InvoiceID FROM PaymentTransactions WHERE PaymentID = ?",
        payment_id
    )

    row = cursor.fetchone()

    if not row:
        conn.close()
        return {
            "success": False,
            "message": "Payment not found"
        }

    invoice_id = row[0]

    cursor.execute(
        "DELETE FROM PaymentTransactions WHERE PaymentID = ?",
        payment_id
    )

    cursor.execute("""
        UPDATE MaintenanceInvoices
        SET Status = 'Pending'
        WHERE InvoiceID = ?
    """, invoice_id)

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Payment deleted successfully"
    }


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
            u.FullName
        FROM PaymentTransactions p
        LEFT JOIN Users u
            ON p.RecordedBy = u.UserID
        ORDER BY p.PaymentID DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    result = []

    for row in rows:
        result.append({
            "payment_id": row[0],
            "invoice_id": row[1],
            "amount_paid": float(row[2]),
            "payment_mode": row[3],
            "transaction_reference": row[4],
            "payment_date": str(row[5]),
            "recorded_by": row[6] or "Unknown"
        })

    return result
