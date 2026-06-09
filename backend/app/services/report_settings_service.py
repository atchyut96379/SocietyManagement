from app.database.db import get_connection


def get_report_settings(month: str, year: int) -> dict:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Notes, CorpusPendingFlats
        FROM MonthlyReportSettings
        WHERE ReportMonth = ? AND ReportYear = ?
    """, (month, year))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"notes": "", "corpus_pending_flats": ""}

    return {
        "notes": row[0] or "",
        "corpus_pending_flats": row[1] or "",
    }


def save_report_settings(
    month: str,
    year: int,
    notes: str = "",
    corpus_pending_flats: str = "",
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ReportSettingID
        FROM MonthlyReportSettings
        WHERE ReportMonth = ? AND ReportYear = ?
    """, (month, year))

    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE MonthlyReportSettings
            SET Notes = ?,
                CorpusPendingFlats = ?,
                UpdatedDate = GETDATE()
            WHERE ReportSettingID = ?
        """, (notes, corpus_pending_flats, existing[0]))
    else:
        cursor.execute("""
            INSERT INTO MonthlyReportSettings
            (ReportMonth, ReportYear, Notes, CorpusPendingFlats)
            VALUES (?, ?, ?, ?)
        """, (month, year, notes, corpus_pending_flats))

    conn.commit()
    conn.close()

    return {"success": True, "message": "Report notes saved"}


def get_available_report_periods():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT InvoiceMonth, InvoiceYear
        FROM MaintenanceInvoices
    """)

    rows = cursor.fetchall()
    conn.close()

    month_order = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12,
    }

    periods = [
        {"month": row[0], "year": int(row[1])}
        for row in rows
    ]

    periods.sort(
        key=lambda item: (
            item["year"],
            month_order.get(item["month"].strip().lower(), 0),
        ),
        reverse=True,
    )

    return periods
