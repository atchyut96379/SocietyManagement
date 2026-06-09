import os
import uuid

from app.config.accounts import normalize_account
from app.database.db import get_connection

UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "uploads",
    "expense_proofs"
)


def _ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def _proof_url(stored_path: str | None) -> str | None:
    if not stored_path:
        return None
    filename = os.path.basename(stored_path)
    return f"/uploads/expense_proofs/{filename}"


def create_expense(
    expense_type: str,
    amount: float,
    description: str,
    expense_date: str,
    proof_file_content: bytes | None = None,
    proof_filename: str | None = None,
    paid_from_account: str = "Maintenance",
):

    proof_path = None

    if proof_file_content:
        _ensure_upload_dir()
        ext = os.path.splitext(proof_filename or "proof.jpg")[1] or ".jpg"
        proof_name = f"{uuid.uuid4().hex}{ext}"
        proof_path = os.path.join(UPLOAD_DIR, proof_name)
        with open(proof_path, "wb") as file:
            file.write(proof_file_content)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Expenses
        (
            ExpenseType,
            Amount,
            Description,
            ExpenseDate,
            ProofImagePath,
            PaidFromAccount
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        expense_type,
        amount,
        description,
        expense_date,
        proof_path,
        normalize_account(paid_from_account),
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
            ExpenseDate,
            ProofImagePath,
            ISNULL(PaidFromAccount, 'Maintenance')
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
            "expense_date": str(row[4]),
            "proof_url": _proof_url(row[5]),
            "paid_from_account": row[6],
        })

    return result
