from app.database.db import get_connection


def create_visitor(visitor):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Visitors
        (
            VisitorName,
            MobileNumber,
            ResidentID,
            Purpose
        )
        VALUES (?, ?, ?, ?)
    """,
    (
        visitor.visitor_name,
        visitor.mobile_number,
        visitor.resident_id,
        visitor.purpose
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Visitor created successfully"
    }


def get_all_visitors():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            v.VisitorID,
            v.VisitorName,
            v.MobileNumber,
            v.ResidentID,
            r.FullName,
            r.FlatNumber,
            v.Purpose,
            v.EntryTime,
            v.Status
        FROM Visitors v
        INNER JOIN Residents r
            ON v.ResidentID = r.ResidentID
        ORDER BY v.VisitorID DESC
    """)

    visitors = cursor.fetchall()

    conn.close()

    result = []

    for row in visitors:
        result.append({
            "visitor_id": row[0],
            "visitor_name": row[1],
            "mobile_number": row[2],
            "resident_id": row[3],
            "resident_name": row[4],
            "flat_number": row[5],
            "purpose": row[6],
            "entry_time": str(row[7]),
            "status": row[8]
        })

    return result


def approve_visitor(visitor_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Visitors
        SET Status = 'Approved'
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