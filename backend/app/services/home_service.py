from datetime import datetime

from app.database.db import get_connection

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def _current_period():
    now = datetime.now()
    return MONTH_NAMES[now.month - 1], now.year


def _last_period():
    now = datetime.now()
    if now.month == 1:
        return "December", now.year - 1
    return MONTH_NAMES[now.month - 2], now.year


def get_home_summary():
    current_month, current_year = _current_period()
    last_month, last_year = _last_period()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT ISNULL(SUM(Amount), 0)
        FROM MaintenanceInvoices
        WHERE InvoiceMonth = ? AND InvoiceYear = ?
        """,
        (current_month, current_year)
    )
    billed_this_month = float(cursor.fetchone()[0])

    cursor.execute(
        """
        SELECT ISNULL(SUM(AmountPaid), 0)
        FROM PaymentTransactions
        WHERE MONTH(PaymentDate) = ?
          AND YEAR(PaymentDate) = ?
        """,
        (datetime.now().month, current_year)
    )
    collected_this_month = float(cursor.fetchone()[0])

    cursor.execute(
        """
        SELECT ISNULL(SUM(Amount), 0)
        FROM MaintenanceInvoices
        """
    )
    total_invoices = float(cursor.fetchone()[0])

    cursor.execute(
        """
        SELECT ISNULL(SUM(AmountPaid), 0)
        FROM PaymentTransactions
        """
    )
    total_collected = float(cursor.fetchone()[0])

    pending_amount = total_invoices - total_collected

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM Complaints
        WHERE Status <> 'Resolved'
        """
    )
    open_complaints = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT ISNULL(SUM(AmountPaid), 0)
        FROM PaymentTransactions
        WHERE PaymentDate < DATEFROMPARTS(?, ?, 1)
        """,
        (current_year, datetime.now().month)
    )
    collections_before_month = float(cursor.fetchone()[0])

    cursor.execute(
        """
        SELECT ISNULL(SUM(Amount), 0)
        FROM Expenses
        WHERE ExpenseDate < DATEFROMPARTS(?, ?, 1)
        """,
        (current_year, datetime.now().month)
    )
    expenses_before_month = float(cursor.fetchone()[0])

    last_month_closing = collections_before_month - expenses_before_month

    cursor.execute(
        """
        SELECT ISNULL(SUM(Amount), 0)
        FROM Expenses
        """
    )
    total_expenses = float(cursor.fetchone()[0])

    present_account_balance = total_collected - total_expenses

    conn.close()

    return {
        "current_month": current_month,
        "current_year": current_year,
        "billed_this_month": billed_this_month,
        "collected_this_month": collected_this_month,
        "pending_amount": pending_amount,
        "open_complaints": open_complaints,
        "last_month_closing": last_month_closing,
        "present_account_balance": present_account_balance,
    }
