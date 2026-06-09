from app.database.db import get_connection


def create_notice(notice, user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Notices
        (
            Title,
            Description,
            CreatedBy
        )
        VALUES (?, ?, ?)
    """,
    (
        notice.title,
        notice.description,
        user_id
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Notice created successfully"
    }


def get_notices():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            NoticeID,
            Title,
            Description,
            CreatedDate
        FROM Notices
        ORDER BY NoticeID DESC
    """)

    notices = cursor.fetchall()

    conn.close()

    result = []

    for row in notices:

        result.append({
            "notice_id": row[0],
            "title": row[1],
            "description": row[2],
            "created_date": str(row[3])
        })

    return result


def delete_notice(notice_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM Notices
        WHERE NoticeID = ?
    """, notice_id)

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Notice deleted successfully"
    }