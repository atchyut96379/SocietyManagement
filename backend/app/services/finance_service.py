from datetime import datetime

from app.config.accounts import ACCOUNT_CORPUS, ACCOUNT_MAINTENANCE
from app.config.society_config import (
    get_apartment_name,
    get_society_address,
    get_society_registration_number,
)
from app.database.db import get_connection

_MONTH_CASE = """
    CASE LOWER(i.InvoiceMonth)
        WHEN 'january' THEN 1 WHEN 'february' THEN 2
        WHEN 'march' THEN 3 WHEN 'april' THEN 4
        WHEN 'may' THEN 5 WHEN 'june' THEN 6
        WHEN 'july' THEN 7 WHEN 'august' THEN 8
        WHEN 'september' THEN 9 WHEN 'october' THEN 10
        WHEN 'november' THEN 11 WHEN 'december' THEN 12
        ELSE 1
    END
"""


def _month_number(month_name: str) -> int:
    months = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12
    }
    return months.get(month_name.strip().lower(), 1)


def _short_month(month_name: str) -> str:
    return month_name.strip()[:3].title()


MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def _current_period() -> tuple[str, int]:
    now = datetime.now()
    return MONTH_NAMES[now.month - 1], now.year


def _simplify_account_view(account_report: dict) -> dict:
    return {
        "opening_balance": account_report["opening_balance"],
        "collected": account_report["collected"],
        "expenditures": account_report["expense_total"],
        "closing_balance": account_report["closing_balance"],
        "paid_flats_count": account_report["paid_flats_count"],
    }


def _invoice_before_filter() -> str:
    return f"""
        (i.InvoiceYear < ? OR (i.InvoiceYear = ? AND {_MONTH_CASE} < ?))
    """


def _sum_payments_for_account(
    cursor,
    account: str,
    month: str | None,
    year: int | None,
    month_num: int | None,
    before_month: bool,
) -> float:
    if before_month:
        cursor.execute(f"""
            SELECT ISNULL(SUM(p.AmountPaid), 0)
            FROM PaymentTransactions p
            INNER JOIN MaintenanceInvoices i ON p.InvoiceID = i.InvoiceID
            WHERE ISNULL(p.CreditAccount, 'Maintenance') = ?
              AND {_invoice_before_filter()}
        """, (account, year, year, month_num))
    else:
        cursor.execute("""
            SELECT ISNULL(SUM(p.AmountPaid), 0)
            FROM PaymentTransactions p
            INNER JOIN MaintenanceInvoices i ON p.InvoiceID = i.InvoiceID
            WHERE ISNULL(p.CreditAccount, 'Maintenance') = ?
              AND i.InvoiceMonth = ?
              AND i.InvoiceYear = ?
        """, (account, month, year))

    return float(cursor.fetchone()[0])


def _sum_expenses_for_account(
    cursor,
    account: str,
    month_num: int,
    year: int,
    before_month: bool,
) -> float:
    if before_month:
        cursor.execute("""
            SELECT ISNULL(SUM(Amount), 0)
            FROM Expenses
            WHERE ISNULL(PaidFromAccount, 'Maintenance') = ?
              AND (YEAR(ExpenseDate) < ?
                   OR (YEAR(ExpenseDate) = ? AND MONTH(ExpenseDate) < ?))
        """, (account, year, year, month_num))
    else:
        cursor.execute("""
            SELECT ISNULL(SUM(Amount), 0)
            FROM Expenses
            WHERE ISNULL(PaidFromAccount, 'Maintenance') = ?
              AND MONTH(ExpenseDate) = ?
              AND YEAR(ExpenseDate) = ?
        """, (account, month_num, year))

    return float(cursor.fetchone()[0])


def _account_opening_balance(cursor, account: str, month_num: int, year: int) -> float:
    collected = _sum_payments_for_account(
        cursor, account, None, year, month_num, before_month=True
    )
    expenses = _sum_expenses_for_account(
        cursor, account, month_num, year, before_month=True
    )
    return collected - expenses


def _build_account_report(cursor, account: str, month: str, year: int) -> dict:
    month_num = _month_number(month)

    opening_balance = _account_opening_balance(cursor, account, month_num, year)
    collected = _sum_payments_for_account(
        cursor, account, month, year, month_num, before_month=False
    )
    cursor.execute("""
        SELECT
            ExpenseID,
            ExpenseType,
            Amount,
            Description,
            ExpenseDate
        FROM Expenses
        WHERE ISNULL(PaidFromAccount, 'Maintenance') = ?
          AND MONTH(ExpenseDate) = ?
          AND YEAR(ExpenseDate) = ?
        ORDER BY ExpenseID
    """, (account, month_num, year))
    expense_rows = cursor.fetchall()

    expenses = [
        {
            "expense_id": row[0],
            "expense_type": row[1],
            "amount": float(row[2]),
            "description": row[3],
            "expense_date": str(row[4]),
        }
        for row in expense_rows
    ]

    expense_total = sum(item["amount"] for item in expenses)
    total_income = opening_balance + collected
    closing_balance = total_income - expense_total

    cursor.execute("""
        SELECT COUNT(DISTINCT i.ResidentID)
        FROM PaymentTransactions p
        INNER JOIN MaintenanceInvoices i ON p.InvoiceID = i.InvoiceID
        WHERE ISNULL(p.CreditAccount, 'Maintenance') = ?
          AND i.InvoiceMonth = ?
          AND i.InvoiceYear = ?
    """, (account, month, year))
    paid_flats_count = int(cursor.fetchone()[0])

    cursor.execute("""
        SELECT
            r.FlatNumber,
            r.FullName,
            p.AmountPaid
        FROM PaymentTransactions p
        INNER JOIN MaintenanceInvoices i ON p.InvoiceID = i.InvoiceID
        INNER JOIN Residents r ON i.ResidentID = r.ResidentID
        WHERE ISNULL(p.CreditAccount, 'Maintenance') = ?
          AND i.InvoiceMonth = ?
          AND i.InvoiceYear = ?
        ORDER BY r.FlatNumber
    """, (account, month, year))
    payment_detail_rows = cursor.fetchall()

    return {
        "account": account,
        "opening_balance": opening_balance,
        "collected": collected,
        "paid_flats_count": paid_flats_count,
        "total_income": total_income,
        "expenses": expenses,
        "expense_total": expense_total,
        "expenditures": expense_total,
        "closing_balance": closing_balance,
        "payments": [
            {
                "flat_number": row[0],
                "resident_name": row[1],
                "amount_paid": float(row[2]),
            }
            for row in payment_detail_rows
        ],
    }


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

    cursor.execute("""
        SELECT ISNULL(SUM(p.AmountPaid), 0)
        FROM PaymentTransactions p
        WHERE ISNULL(p.CreditAccount, 'Maintenance') = 'Maintenance'
    """)
    maintenance_collected_all = float(cursor.fetchone()[0])

    cursor.execute("""
        SELECT ISNULL(SUM(Amount), 0)
        FROM Expenses
        WHERE ISNULL(PaidFromAccount, 'Maintenance') = 'Maintenance'
    """)
    maintenance_expenses_all = float(cursor.fetchone()[0])

    maintenance_balance = maintenance_collected_all - maintenance_expenses_all

    cursor.execute("""
        SELECT ISNULL(SUM(p.AmountPaid), 0)
        FROM PaymentTransactions p
        WHERE ISNULL(p.CreditAccount, 'Maintenance') = 'Corpus'
    """)
    corpus_collected_all = float(cursor.fetchone()[0])

    cursor.execute("""
        SELECT ISNULL(SUM(Amount), 0)
        FROM Expenses
        WHERE ISNULL(PaidFromAccount, 'Maintenance') = 'Corpus'
    """)
    corpus_expenses_all = float(cursor.fetchone()[0])

    corpus_balance = corpus_collected_all - corpus_expenses_all

    current_month, current_year = _current_period()
    maintenance_period = _build_account_report(
        cursor, ACCOUNT_MAINTENANCE, current_month, current_year
    )
    corpus_period = _build_account_report(
        cursor, ACCOUNT_CORPUS, current_month, current_year
    )

    conn.close()

    pending_dues = total_invoices - total_collected

    return {
        "total_invoices": total_invoices,
        "total_collected": total_collected,
        "pending_dues": pending_dues,
        "total_expenses": total_expenses,
        "available_balance": maintenance_balance + corpus_balance,
        "maintenance_balance": maintenance_balance,
        "corpus_balance": corpus_balance,
        "period_month": current_month,
        "period_year": current_year,
        "maintenance_account": _simplify_account_view(maintenance_period),
        "corpus_account": _simplify_account_view(corpus_period),
    }


def get_monthly_report(month: str, year: int):
    month_num = _month_number(month)
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
            p.PaymentDate,
            ISNULL(p.CreditAccount, 'Maintenance')
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
            ExpenseDate,
            ISNULL(PaidFromAccount, 'Maintenance')
        FROM Expenses
        WHERE MONTH(ExpenseDate) = ?
          AND YEAR(ExpenseDate) = ?
        ORDER BY ExpenseID DESC
    """, (month_num, year))
    expense_rows = cursor.fetchall()

    total_expenses = sum(float(row[2]) for row in expense_rows)

    maintenance_account = _build_account_report(
        cursor, ACCOUNT_MAINTENANCE, month, year
    )
    corpus_account = _build_account_report(
        cursor, ACCOUNT_CORPUS, month, year
    )

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
            "available_balance": (
                maintenance_account["closing_balance"]
                + corpus_account["closing_balance"]
            ),
            "maintenance_balance": maintenance_account["closing_balance"],
            "corpus_balance": corpus_account["closing_balance"],
        },
        "maintenance_account": maintenance_account,
        "corpus_account": corpus_account,
        "invoices": [
            {
                "invoice_id": row[0],
                "resident_name": row[1],
                "flat_number": row[2],
                "amount": float(row[3]),
                "status": row[4],
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
                "payment_date": str(row[6]),
                "credit_account": row[7],
            }
            for row in payment_rows
        ],
        "expenses": [
            {
                "expense_id": row[0],
                "expense_type": row[1],
                "amount": float(row[2]),
                "description": row[3],
                "expense_date": str(row[4]),
                "paid_from_account": row[5],
            }
            for row in expense_rows
        ],
    }


def get_resident_monthly_report(month: str, year: int):
    report = get_monthly_report(month, year)
    from app.services.report_settings_service import get_report_settings

    settings = get_report_settings(month, year)
    report["report_notes"] = settings["notes"]
    report["corpus_pending_flats_text"] = settings["corpus_pending_flats"]
    return report


def build_monthly_report_pdf_data(
    month: str,
    year: int,
    notes: str | None = None,
    corpus_pending_flats: str | None = None,
):
    from app.services.report_settings_service import get_report_settings

    saved = get_report_settings(month, year)
    if notes is None:
        notes = saved["notes"]
    if corpus_pending_flats is None:
        corpus_pending_flats = saved["corpus_pending_flats"]

    report = get_monthly_report(month, year)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.FlatNumber, r.FullName
        FROM MaintenanceInvoices i
        INNER JOIN Residents r ON i.ResidentID = r.ResidentID
        WHERE i.InvoiceMonth = ?
          AND i.InvoiceYear = ?
          AND i.Status <> 'Paid'
        ORDER BY r.FlatNumber
    """, (month, year))
    pending_rows = cursor.fetchall()

    cursor.execute("""
        SELECT
            r.FlatNumber,
            r.FullName,
            ISNULL(i.Amount, 0),
            ISNULL(i.Status, 'No Invoice'),
            i.InvoiceID
        FROM Residents r
        LEFT JOIN MaintenanceInvoices i
            ON i.ResidentID = r.ResidentID
           AND i.InvoiceMonth = ?
           AND i.InvoiceYear = ?
        ORDER BY r.FlatNumber
    """, (month, year))
    resident_rows = cursor.fetchall()

    residents = []
    for row in resident_rows:
        invoice_id = row[4]
        amount_paid = 0.0
        credit_account = None
        if invoice_id:
            cursor.execute("""
                SELECT ISNULL(SUM(AmountPaid), 0),
                       MAX(ISNULL(CreditAccount, 'Maintenance'))
                FROM PaymentTransactions
                WHERE InvoiceID = ?
            """, (invoice_id,))
            paid_row = cursor.fetchone()
            amount_paid = float(paid_row[0])
            credit_account = paid_row[1]

        residents.append({
            "flat_number": row[0],
            "resident_name": row[1],
            "invoice_amount": float(row[2]),
            "amount_paid": amount_paid,
            "status": row[3],
            "credit_account": credit_account,
        })

    conn.close()

    note_lines = [
        line.strip()
        for line in notes.splitlines()
        if line.strip()
    ]

    corpus_pending = []
    for line in corpus_pending_flats.splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            flat, name = line.split(":", 1)
            corpus_pending.append({
                "flat_number": flat.strip(),
                "resident_name": name.strip(),
            })
        else:
            corpus_pending.append({
                "flat_number": line,
                "resident_name": "",
            })

    return {
        "society_name": get_apartment_name(),
        "registration_number": get_society_registration_number(),
        "society_address": get_society_address(),
        "month": _short_month(month),
        "year": year,
        "maintenance_account": report["maintenance_account"],
        "corpus_account": report["corpus_account"],
        "pending_flats": [
            {"flat_number": row[0], "resident_name": row[1]}
            for row in pending_rows
        ],
        "corpus_pending_flats": corpus_pending,
        "notes": note_lines,
        "residents": residents,
    }
