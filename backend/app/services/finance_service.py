from app.database.db import get_connection


def get_finance_dashboard():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ISNULL(SUM(Amount),0)
        FROM MaintenanceInvoices
    """)
    total_invoices = float(cursor.fetchone()[0])

    cursor.execute("""
        SELECT ISNULL(SUM(AmountPaid),0)
        FROM PaymentTransactions
    """)
    total_collected = float(cursor.fetchone()[0])

    cursor.execute("""
        SELECT ISNULL(SUM(Amount),0)
        FROM Expenses
    """)
    total_expenses = float(cursor.fetchone()[0])

    pending_dues = total_invoices - total_collected
    available_balance = total_collected - total_expenses

    conn.close()

    return {
        "total_invoices": total_invoices,
        "total_collected": total_collected,
        "pending_dues": pending_dues,
        "total_expenses": total_expenses,
        "available_balance": available_balance
    }


def get_monthly_report(month: str, year: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            i.InvoiceID,
            r.FullName,
            r.FlatNumber,
            i.Amount,
            i.Status
        FROM MaintenanceInvoices i
        INNER JOIN Residents r
            ON i.ResidentID = r.ResidentID
        WHERE i.InvoiceMonth = ?
          AND i.InvoiceYear = ?
        ORDER BY r.FlatNumber
    """, (month, year))

    invoice_rows = cursor.fetchall()

    cursor.execute("""
        SELECT ISNULL(SUM(Amount),0)
        FROM MaintenanceInvoices
        WHERE InvoiceMonth = ?
          AND InvoiceYear = ?
    """, (month, year))
    total_invoices = float(cursor.fetchone()[0])

    cursor.execute("""
        SELECT
            p.PaymentID,
            p.InvoiceID,
            r.FullName,
            r.FlatNumber,
            p.AmountPaid,
            p.PaymentMode,
            p.PaymentDate
        FROM PaymentTransactions p
        INNER JOIN MaintenanceInvoices i
            ON p.InvoiceID = i.InvoiceID
        INNER JOIN Residents r
            ON i.ResidentID = r.ResidentID
        WHERE i.InvoiceMonth = ?
          AND i.InvoiceYear = ?
        ORDER BY p.PaymentID DESC
    """, (month, year))

    payment_rows = cursor.fetchall()

    cursor.execute("""
        SELECT ISNULL(SUM(p.AmountPaid),0)
        FROM PaymentTransactions p
        INNER JOIN MaintenanceInvoices i
            ON p.InvoiceID = i.InvoiceID
        WHERE i.InvoiceMonth = ?
          AND i.InvoiceYear = ?
    """, (month, year))
    total_collected = float(cursor.fetchone()[0])

    cursor.execute("""
        SELECT
            ExpenseID,
            ExpenseType,
            Amount,
            Description,
            ExpenseDate
        FROM Expenses
        WHERE MONTH(ExpenseDate) = ?
          AND YEAR(ExpenseDate) = ?
        ORDER BY ExpenseID DESC
    """, (_month_number(month), year))

    expense_rows = cursor.fetchall()

    cursor.execute("""
        SELECT ISNULL(SUM(Amount),0)
        FROM Expenses
        WHERE MONTH(ExpenseDate) = ?
          AND YEAR(ExpenseDate) = ?
    """, (_month_number(month), year))
    total_expenses = float(cursor.fetchone()[0])

    conn.close()

    pending_dues = total_invoices - total_collected

    return {
        "month": month,
        "year": year,
        "summary": {
            "total_invoices": total_invoices,
            "total_collected": total_collected,
            "pending_dues": pending_dues,
            "total_expenses": total_expenses,
            "available_balance": total_collected - total_expenses
        },
        "invoices": [
            {
                "invoice_id": row[0],
                "resident_name": row[1],
                "flat_number": row[2],
                "amount": float(row[3]),
                "status": row[4]
            }
            for row in invoice_rows
        ],
        "payments": [
            {
                "payment_id": row[0],
                "invoice_id": row[1],
                "resident_name": row[2],
                "flat_number": row[3],
                "amount_paid": float(row[4]),
                "payment_mode": row[5],
                "payment_date": str(row[6])
            }
            for row in payment_rows
        ],
        "expenses": [
            {
                "expense_id": row[0],
                "expense_type": row[1],
                "amount": float(row[2]),
                "description": row[3],
                "expense_date": str(row[4])
            }
            for row in expense_rows
        ]
    }


def _month_number(month_name: str) -> int:
    months = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12
    }
    return months.get(month_name.strip().lower(), 1)
