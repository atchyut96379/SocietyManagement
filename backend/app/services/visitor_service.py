import random
from datetime import datetime, timedelta

from app.database.db import get_connection


def _generate_entry_code(cursor) -> str:
    for _ in range(20):
        code = f"{random.randint(100000, 999999)}"

        cursor.execute(
            """
            SELECT VisitorID FROM Visitors
            WHERE EntryCode = ? AND Status IN ('Pending', 'Approved')
            """,
            code
        )

        if not cursor.fetchone():
            return code

    raise RuntimeError("Unable to generate a unique entry code")


def _visitor_row_to_dict(row):
    return {
        "visitor_id": row[0],
        "visitor_name": row[1],
        "mobile_number": row[2],
        "resident_id": row[3],
        "resident_name": row[4],
        "flat_number": row[5],
        "purpose": row[6],
        "entry_time": str(row[7]) if row[7] else None,
        "status": row[8],
        "entry_code": row[9],
        "valid_until": str(row[10]) if row[10] else None,
        "exit_time": str(row[11]) if len(row) > 11 and row[11] else None,
    }


def _base_select_sql():
    return """
        SELECT
            v.VisitorID,
            v.VisitorName,
            v.MobileNumber,
            v.ResidentID,
            r.FullName,
            r.FlatNumber,
            v.Purpose,
            v.EntryTime,
            v.Status,
            v.EntryCode,
            v.ValidUntil,
            v.ExitTime
        FROM Visitors v
        INNER JOIN Residents r
            ON v.ResidentID = r.ResidentID
    """


def create_visitor(visitor, resident_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    entry_code = _generate_entry_code(cursor)
    valid_until = datetime.now() + timedelta(hours=24)

    cursor.execute("""
        INSERT INTO Visitors
        (
            VisitorName,
            MobileNumber,
            ResidentID,
            Purpose,
            EntryCode,
            ValidUntil,
            Status
        )
        VALUES (?, ?, ?, ?, ?, ?, 'Pending')
    """,
    (
        visitor.visitor_name,
        visitor.mobile_number,
        resident_id,
        visitor.purpose,
        entry_code,
        valid_until,
    ))

    cursor.execute("SELECT @@IDENTITY")
    visitor_id = int(cursor.fetchone()[0])

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Visitor registered. Share the entry code with security.",
        "visitor_id": visitor_id,
        "entry_code": entry_code,
        "valid_until": str(valid_until),
    }


def get_all_visitors():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        _base_select_sql() + " ORDER BY v.VisitorID DESC"
    )

    visitors = cursor.fetchall()
    conn.close()

    return [_visitor_row_to_dict(row) for row in visitors]


def get_visitors_for_resident(resident_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        _base_select_sql() + " WHERE v.ResidentID = ? ORDER BY v.VisitorID DESC",
        resident_id
    )

    visitors = cursor.fetchall()
    conn.close()

    return [_visitor_row_to_dict(row) for row in visitors]


def lookup_visitor_by_code(entry_code: str):
    entry_code = entry_code.strip()

    if not entry_code:
        return {"success": False, "message": "Entry code is required"}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        _base_select_sql() + " WHERE v.EntryCode = ?",
        entry_code
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"success": False, "message": "Invalid entry code"}

    visitor = _visitor_row_to_dict(row)

    if visitor["status"] == "Completed":
        return {
            "success": False,
            "message": "This visitor has already exited"
        }

    valid_until_raw = row[10]
    if valid_until_raw:
        valid_until = (
            valid_until_raw
            if isinstance(valid_until_raw, datetime)
            else datetime.fromisoformat(
                str(valid_until_raw).replace(" ", "T", 1).split(".")[0]
            )
        )
        if datetime.now() > valid_until:
            return {
                "success": False,
                "message": "Entry code has expired"
            }

    return {
        "success": True,
        "visitor": visitor
    }


def verify_entry_code(entry_code: str):
    lookup = lookup_visitor_by_code(entry_code)

    if not lookup.get("success"):
        return lookup

    visitor = lookup["visitor"]

    if visitor["status"] == "Approved":
        return {
            "success": True,
            "message": "Visitor already approved for entry",
            "visitor": visitor
        }

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Visitors
        SET
            Status = 'Approved',
            EntryTime = GETDATE()
        WHERE VisitorID = ?
    """, visitor["visitor_id"])

    conn.commit()
    conn.close()

    visitor["status"] = "Approved"

    return {
        "success": True,
        "message": "Entry approved. Allow visitor inside.",
        "visitor": visitor
    }


def approve_visitor(visitor_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Visitors
        SET Status = 'Approved', EntryTime = GETDATE()
        WHERE VisitorID = ?
    """, visitor_id)

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Visitor approved successfully"
    }


def mark_exit(visitor_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Visitors
        SET
            ExitTime = GETDATE(),
            Status = 'Completed'
        WHERE VisitorID = ?
    """, visitor_id)

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Visitor exit recorded"
    }
