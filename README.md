# Society Management System

A full-stack application for housing society / apartment association management. Admins can manage residents, visitors, complaints, notices, and finances from a single portal.

## Architecture

| Layer | Stack |
|-------|-------|
| Frontend | React, Bootstrap, React Router, Axios |
| Backend | FastAPI, JWT auth, pyodbc |
| Database | Microsoft SQL Server |

## Workflow

1. **Login** — Admin signs in with email/password; JWT token is stored in the browser.
2. **Dashboard** — Summary of residents, visitors, open complaints, and total collections.
3. **Residents** — Add, view, and remove flat owners/tenants.
4. **Visitors** — Register visitors, approve entry, and mark exit.
5. **Complaints** — Log resident complaints and mark them resolved.
6. **Notices** — Publish society announcements on the notice board.
7. **Finance** — Generate maintenance invoices, record payments, track expenses, and view balances.

## Prerequisites

- Python 3.10+
- Node.js 18+
- SQL Server (local or named instance)
- [ODBC Driver 18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

## Setup

### 1. Database

Copy the environment file and set your SQL Server instance:

```powershell
cd backend
copy .env.example .env
```

Edit `.env`:

```
DB_SERVER=YOUR_SERVER\INSTANCE
DB_DATABASE=SocietyManagement
DB_DRIVER=ODBC Driver 18 for SQL Server
```

Create tables and seed the default admin:

```powershell
.\venv\Scripts\python.exe setup_db.py
```

Default login after setup:

- **Admin:** `admin@society.com` / `Admin@123`
- **Security (gate):** `security@society.com` / `Security@123`
- **Resident (demo):** first resident email / `Resident@123` (e.g. `ravi@gmail.com`)

Change these passwords after first login in production.

Create more resident logins from **Residents → Login** button (admin only).

### 2. Backend

```powershell
cd backend
.\venv\Scripts\pip.exe install -r requirements.txt
.\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

### 3. Frontend

```powershell
cd frontend
npm install
npm start
```

App: http://localhost:3000

## Production deployment (LAN / office PC)

### 1. Configure backend for network access

In `backend/.env`:

```
JWT_SECRET=your-long-random-secret
FRONTEND_URL=http://localhost:3000,http://YOUR_PC_IP:3000
```

### 2. Start API on all interfaces

```powershell
.\scripts\start-api.ps1
```

API will be available at `http://YOUR_PC_IP:8000`

### 3. Build and serve frontend

```powershell
.\scripts\deploy-production.ps1 -ApiUrl "http://YOUR_PC_IP:8000" -Port 3000
```

Other devices on the same Wi‑Fi/LAN can open `http://YOUR_PC_IP:3000`

## Resident self-service portal

Residents log in and land on `/portal` where they can:

- View flat summary and pending dues
- Read society notices
- Submit and track their own complaints
- View maintenance invoices and payment history

Admin creates resident logins from **Residents → Login** (uses resident email + chosen password).

## Project Structure

```
SocietyManagement/
├── backend/
│   ├── app/
│   │   ├── api/          # REST endpoints
│   │   ├── auth/         # JWT middleware
│   │   ├── database/     # SQL connection
│   │   ├── schemas/      # Pydantic models
│   │   └── services/     # Business logic
│   ├── database/
│   │   └── schema.sql    # Table definitions
│   ├── setup_db.py       # One-time DB initializer
│   └── requirements.txt
└── frontend/
    └── src/
        ├── components/   # Layout, Sidebar, Navbar
        ├── pages/        # Feature screens
        └── services/     # API client
```

## API Endpoints (protected unless noted)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/login` | Login (public) |
| POST | `/register-admin` | Create admin (public) |
| GET | `/dashboard/summary` | Dashboard stats |
| GET/POST/DELETE | `/resident` | Resident CRUD |
| GET/POST | `/visitor` | Visitor management |
| GET/POST | `/complaint` | Complaints |
| GET/POST | `/notice` | Notices |
| GET/POST | `/maintenance` | Maintenance invoices |
| GET/POST | `/payment` | Payment records |
| GET/POST | `/expense` | Society expenses |
| GET/POST | `/maintenance/generate-bulk` | Bulk invoices for all residents |
| GET | `/finance/report?month=&year=` | Monthly finance report |
| DELETE | `/notice/{id}` | Delete notice |
| PUT | `/resident/{id}` | Update resident |
| POST | `/change-password` | Change user password |
| POST | `/register-security` | Create security user |
| POST | `/register-resident` | Create resident login (admin) |
| GET | `/portal/*` | Resident portal (profile, dues, complaints, notices) |

## Troubleshooting

- **Database connection failed** — Verify SQL Server is running and `DB_SERVER` in `.env` matches your instance name (e.g. `MACHINE\SQLEXPRESS`).
- **401 on API calls** — Log in again; the JWT may have expired (24-hour validity).
- **Module not found** — Run `pip install -r requirements.txt` inside the backend virtual environment.
