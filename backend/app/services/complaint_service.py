from app.database.db import get_connection


def create_complaint(complaint):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Complaints
        (
            ResidentID,
            Subject,
            Description
        )
        VALUES (?, ?, ?)
    """,
    (
        complaint.resident_id,
        complaint.subject,
        complaint.description
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Complaint created successfully"
    }


def get_all_complaints():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.ComplaintID,
            c.ResidentID,
            r.FullName,
            r.FlatNumber,
            c.Subject,
            c.Description,
            c.Status,
            c.CreatedDate
        FROM Complaints c
        INNER JOIN Residents r
            ON c.ResidentID = r.ResidentID
        ORDER BY c.ComplaintID DESC
    """)

    complaints = cursor.fetchall()

    conn.close()

    result = []

    for row in complaints:
        result.append({
            "complaint_id": row[0],
            "resident_id": row[1],
            "resident_name": row[2],
            "flat_number": row[3],
            "subject": row[4],
            "description": row[5],
            "status": row[6],
            "created_date": str(row[7])
        })

    return result


def get_complaints_by_resident(resident_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.ComplaintID,
            c.ResidentID,
            r.FullName,
            r.FlatNumber,
            c.Subject,
            c.Description,
            c.Status,
            c.CreatedDate
        FROM Complaints c
        INNER JOIN Residents r
            ON c.ResidentID = r.ResidentID
        WHERE c.ResidentID = ?
        ORDER BY c.ComplaintID DESC
    """, resident_id)

    complaints = cursor.fetchall()
    conn.close()

    result = []

    for row in complaints:
        result.append({
            "complaint_id": row[0],
            "resident_id": row[1],
            "resident_name": row[2],
            "flat_number": row[3],
            "subject": row[4],
            "description": row[5],
            "status": row[6],
            "created_date": str(row[7])
        })

    return result


def update_status(complaint_id, status):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Complaints
        SET
            Status = ?,
            UpdatedDate = GETDATE()
        WHERE ComplaintID = ?
    """,
    (status, complaint_id))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"Complaint marked as {status}"
    }