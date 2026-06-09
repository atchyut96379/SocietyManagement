from app.database.db import get_connection


def create_expense(expense):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Expenses
        (
            ExpenseType,
            Amount,
            Description,
            ExpenseDate
        )
        VALUES (?, ?, ?, ?)
    """,
    (
        expense.expense_type,
        expense.amount,
        expense.description,
        expense.expense_date
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Expense added successfully"
    }


def get_expenses():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ExpenseID,
            ExpenseType,
            Amount,
            Description,
            ExpenseDate
        FROM Expenses
        ORDER BY ExpenseID DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    result = []

    for row in rows:

        result.append({
            "expense_id": row[0],
            "expense_type": row[1],
            "amount": float(row[2]),
            "description": row[3],
            "expense_date": str(row[4])
        })

    return result