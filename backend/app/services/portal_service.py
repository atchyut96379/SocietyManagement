import json

from app.database.db import get_connection


def _parse_vehicles(raw):
    if not raw:
        return []
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return [raw] if raw else []


def get_resident_profile(resident_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            r.ResidentID,
            r.FullName,
            r.FlatNumber,
            r.PhoneNumber,
            r.Email,
            r.TowerName,
            r.IsOwner,
            r.OwnerName,
            r.VehicleDetails,
            r.ProfileCompleted,
            r.CommitteeRole
        FROM Residents r
        WHERE r.ResidentID = ?
        """,
        (resident_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "resident_id": row[0],
        "full_name": row[1],
        "flat_number": row[2],
        "phone_number": row[3],
        "email": row[4],
        "tower_name": row[5],
        "is_owner": bool(row[6]),
        "owner_name": row[7],
        "vehicle_details": _parse_vehicles(row[8]),
        "profile_completed": bool(row[9]),
        "committee_role": row[10] or "None",
        "editable_fields": ["vehicle_details"] if row[9] else None
    }


def get_resident_invoices(resident_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT InvoiceID, InvoiceMonth, InvoiceYear, Amount, DueDate, Status
        FROM MaintenanceInvoices
        WHERE ResidentID = ?
        ORDER BY InvoiceID DESC
        """,
        (resident_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "invoice_id": row[0],
            "month": row[1],
            "year": row[2],
            "amount": float(row[3]),
            "due_date": str(row[4]),
            "status": row[5]
        }
        for row in rows
    ]


def get_resident_payments(resident_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            p.PaymentID,
            p.InvoiceID,
            i.InvoiceMonth,
            i.InvoiceYear,
            p.AmountPaid,
            p.PaymentMode,
            p.PaymentDate,
            p.ReceiptNumber
        FROM PaymentTransactions p
        INNER JOIN MaintenanceInvoices i ON p.InvoiceID = i.InvoiceID
        WHERE i.ResidentID = ?
        ORDER BY p.PaymentID DESC
        """,
        (resident_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "payment_id": row[0],
            "invoice_id": row[1],
            "month": row[2],
            "year": row[3],
            "amount_paid": float(row[4]),
            "payment_mode": row[5],
            "payment_date": str(row[6]),
            "receipt_number": row[7]
        }
        for row in rows
    ]


def get_resident_summary(resident_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT ISNULL(SUM(Amount),0)
        FROM MaintenanceInvoices
        WHERE ResidentID = ?
        """,
        (resident_id,)
    )
    total_invoices = float(cursor.fetchone()[0])

    cursor.execute(
        """
        SELECT ISNULL(SUM(p.AmountPaid),0)
        FROM PaymentTransactions p
        INNER JOIN MaintenanceInvoices i ON p.InvoiceID = i.InvoiceID
        WHERE i.ResidentID = ?
        """,
        (resident_id,)
    )
    total_paid = float(cursor.fetchone()[0])

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM Complaints
        WHERE ResidentID = ? AND Status <> 'Resolved'
        """,
        (resident_id,)
    )
    open_complaints = cursor.fetchone()[0]

    conn.close()

    return {
        "total_invoices": total_invoices,
        "total_paid": total_paid,
        "pending_dues": total_invoices - total_paid,
        "open_complaints": open_complaints
    }
