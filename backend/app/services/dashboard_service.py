from app.database.db import get_connection


def get_dashboard_summary():

    conn = get_connection()
    cursor = conn.cursor()

    # Residents
    cursor.execute("""
        SELECT COUNT(*)
        FROM Residents
    """)
    residents = cursor.fetchone()[0]

    # Visitors
    cursor.execute("""
        SELECT COUNT(*)
        FROM Visitors
    """)
    visitors = cursor.fetchone()[0]

    # Open Complaints
    cursor.execute("""
        SELECT COUNT(*)
        FROM Complaints
        WHERE Status <> 'Resolved'
    """)
    complaints = cursor.fetchone()[0]

    # Collection
    cursor.execute("""
        SELECT ISNULL(SUM(AmountPaid),0)
        FROM PaymentTransactions
    """)
    collection = float(cursor.fetchone()[0])

    conn.close()

    return {
        "total_residents": residents,
        "total_visitors": visitors,
        "pending_complaints": complaints,
        "total_collection": collection
    }