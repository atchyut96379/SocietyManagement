from app.config.accounts import VALID_ACCOUNTS, normalize_account
from app.database.db import get_connection


def create_transfer(
    from_account: str,
    to_account: str,
    amount: float,
    description: str,
    transfer_date: str,
):
    from_account = normalize_account(from_account)
    to_account = normalize_account(to_account)

    if from_account not in VALID_ACCOUNTS or to_account not in VALID_ACCOUNTS:
        return {"success": False, "message": "Invalid account selected"}

    if from_account == to_account:
        return {
            "success": False,
            "message": "From and To accounts must be different"
        }

    if amount <= 0:
        return {"success": False, "message": "Transfer amount must be greater than zero"}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO AccountTransfers
        (FromAccount, ToAccount, Amount, Description, TransferDate)
        VALUES (?, ?, ?, ?, ?)
    """, (from_account, to_account, amount, description, transfer_date))

    conn.commit()
    conn.close()

    return {"success": True, "message": "Account transfer recorded"}


def get_transfers():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            TransferID,
            FromAccount,
            ToAccount,
            Amount,
            Description,
            TransferDate
        FROM AccountTransfers
        ORDER BY TransferID DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "transfer_id": row[0],
            "from_account": row[1],
            "to_account": row[2],
            "amount": float(row[3]),
            "description": row[4],
            "transfer_date": str(row[5]),
        }
        for row in rows
    ]
