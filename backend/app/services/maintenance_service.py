from app.database.db import get_connection


def generate_invoice(invoice):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT InvoiceID
        FROM MaintenanceInvoices
        WHERE ResidentID = ?
          AND InvoiceMonth = ?
          AND InvoiceYear = ?
    """,
    (
        invoice.resident_id,
        invoice.invoice_month,
        invoice.invoice_year
    ))

    if cursor.fetchone():
        conn.close()
        return {
            "success": False,
            "message": "Invoice already exists for this resident and period"
        }

    cursor.execute("""
        INSERT INTO MaintenanceInvoices
        (
            ResidentID,
            InvoiceMonth,
            InvoiceYear,
            Amount,
            DueDate
        )
        VALUES (?, ?, ?, ?, ?)
    """,
    (
        invoice.resident_id,
        invoice.invoice_month,
        invoice.invoice_year,
        invoice.amount,
        invoice.due_date
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Maintenance invoice generated"
    }


def generate_bulk_invoices(invoice):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ResidentID
        FROM Residents
        ORDER BY ResidentID
    """)

    residents = cursor.fetchall()
    created = 0
    skipped = 0

    for row in residents:
        resident_id = row[0]

        cursor.execute("""
            SELECT InvoiceID
            FROM MaintenanceInvoices
            WHERE ResidentID = ?
              AND InvoiceMonth = ?
              AND InvoiceYear = ?
        """,
        (
            resident_id,
            invoice.invoice_month,
            invoice.invoice_year
        ))

        if cursor.fetchone():
            skipped += 1
            continue

        cursor.execute("""
            INSERT INTO MaintenanceInvoices
            (
                ResidentID,
                InvoiceMonth,
                InvoiceYear,
                Amount,
                DueDate
            )
            VALUES (?, ?, ?, ?, ?)
        """,
        (
            resident_id,
            invoice.invoice_month,
            invoice.invoice_year,
            invoice.amount,
            invoice.due_date
        ))

        created += 1

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"Generated {created} invoices, skipped {skipped} duplicates",
        "created": created,
        "skipped": skipped
    }


def get_all_invoices():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            i.InvoiceID,
            i.ResidentID,
            r.FullName,
            r.FlatNumber,
            i.InvoiceMonth,
            i.InvoiceYear,
            i.Amount,
            i.DueDate,
            i.Status
        FROM MaintenanceInvoices i
        INNER JOIN Residents r
            ON i.ResidentID = r.ResidentID
        ORDER BY i.InvoiceID DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    result = []

    for row in rows:
        result.append({
            "invoice_id": row[0],
            "resident_id": row[1],
            "resident_name": row[2],
            "flat_number": row[3],
            "month": row[4],
            "year": row[5],
            "amount": float(row[6]),
            "due_date": str(row[7]),
            "status": row[8]
        })

    return result
