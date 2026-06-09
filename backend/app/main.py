import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database.db import get_connection

from app.api.user_api import router as user_router
from app.api.admin_api import router as admin_router
from app.api.resident_api import router as resident_router
from app.api.visitor_api import router as visitor_router
from app.api.notice_api import router as notice_router
from app.api.complaint_api import router as complaint_router
from app.api.maintenance_api import router as maintenance_router
from app.api.payment_api import router as payment_router
from app.api.finance_api import router as finance_router
from app.api.dashboard_api import router as dashboard_router
from app.api.expense_api import router as expense_router
from app.api.portal_api import router as portal_router
from app.api.flat_api import router as flat_router
from app.api.config_api import router as config_router
from app.api.home_api import router as home_router
from app.api.my_dues_api import router as my_dues_router
from app.api.guard_api import router as guard_router

load_dotenv()

app = FastAPI(
    title="Society Management API"
)

frontend_url = os.getenv(
    "FRONTEND_URL",
    "http://localhost:3000"
)

allowed_origins = [
    origin.strip()
    for origin in frontend_url.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uploads_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "uploads"
)
os.makedirs(uploads_path, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")

app.include_router(user_router)
app.include_router(admin_router)
app.include_router(resident_router)
app.include_router(visitor_router)
app.include_router(notice_router)
app.include_router(complaint_router)
app.include_router(maintenance_router)
app.include_router(payment_router)
app.include_router(finance_router)
app.include_router(dashboard_router)
app.include_router(expense_router)
app.include_router(portal_router)
app.include_router(flat_router)
app.include_router(config_router)
app.include_router(home_router)
app.include_router(my_dues_router)
app.include_router(guard_router)


@app.get("/")
def root():
    return {
        "message": "Society Management API Running Successfully"
    }


@app.get("/test-db")
def test_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT DB_NAME()")
        db_name = cursor.fetchone()[0]

        conn.close()

        return {
            "status": "success",
            "database": db_name
        }

    except Exception as ex:
        return {
            "status": "failed",
            "error": str(ex)
        }
