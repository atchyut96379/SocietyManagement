# Society Management System

A full-stack application for housing society / apartment association management. **Admin** creates the **Secretary**; the Secretary manages residents, committee roles, visitors, complaints, notices, and finances.

## Architecture

| Layer | Stack |
|-------|-------|
| Frontend | React, Bootstrap, React Router, Axios |
| Backend | FastAPI, JWT auth, pyodbc |
| Database | Microsoft SQL Server |

## Roles & Workflow

| Role | Responsibilities |
|------|------------------|
| **Admin** | Create Secretary only; transfer Secretary role when committee changes |
| **Secretary** | All operational tasks: residents, logins, committee designations, finance, notices |
| **Security** | Visitor gate operations |
| **Resident** | Self-service portal: profile, dues, complaints, online/cash payments |

### Login

- **Username:** mobile number (email is optional)
- **Default passwords:** `{ApartmentPrefix}Sec` for Secretary (e.g. `MarvSec`), `{ApartmentPrefix}{FlatNo}` for residents (e.g. `Marv101`)
- Configure apartment prefix via `APARTMENT_NAME` in `.env` (first 4 characters used)

### First login (residents)

1. Secretary creates resident and login via `POST /resident/create-with-login` (selects flat from auto-generated list)
2. Resident logs in with mobile + default password
3. Resident completes profile: **tenants** must enter **owner name**; all must enter **vehicle details**
4. After profile completion, only **vehicle details** can be edited (mobile, flat, name are locked)

### Flats

Flats are auto-generated per tower and floor: `101–119`, `201–219`, `301–319`, etc.  
Configure towers and floors in `.env`:

```
TOWERS=Tower A,Tower B
FLOORS_COUNT=10
```

### Committee designations

One person per role: President, Vice President, Secretary, Joint Secretary, Treasurer, Member1–Member5.  
Only the Secretary can assign or change committee roles.

### Payments (immutable)

- Payments cannot be edited or deleted once recorded
- **Online:** `GET /portal/invoices/{id}/pay-now` → payment gateway → auto receipt via webhook
- **Cash:** `POST /portal/invoices/{id}/pay-cash` with proof image upload → marked paid + receipt
- Download receipt: `GET /portal/payments/{id}/receipt`

## Prerequisites

- Python 3.10+
- Node.js 18+
- SQL Server (local or named instance)
- [ODBC Driver 18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

## Setup

### 1. Database

```powershell
cd backend
copy .env.example .env
```

Edit `.env` (set `DB_SERVER`, `APARTMENT_NAME`, `TOWERS`, `FLOORS_COUNT`).

```powershell
.\venv\Scripts\python.exe setup_db.py
```

Default logins after setup:

- **Admin:** mobile `9999999999` / `Admin@123`
- **Security:** mobile `8888888888` / `Security@123`

Admin then creates Secretary via API: `POST /admin/secretary` (password auto-generated, e.g. `MarvSec`).

### 2. Backend

```powershell
cd backend
.\venv\Scripts\pip.exe install -r requirements.txt
.\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

## Key API Endpoints

| Method | Path | Who | Description |
|--------|------|-----|-------------|
| POST | `/login` | Public | Login with mobile + password |
| POST | `/admin/secretary` | Admin | Create Secretary (auto password) |
| POST | `/admin/transfer-secretary` | Admin | Transfer Secretary role |
| GET | `/flat/available` | Secretary | List vacant flats |
| POST | `/resident/create-with-login` | Secretary | Create resident + login |
| PUT | `/resident/{id}/committee-role` | Secretary | Assign committee designation |
| POST | `/portal/complete-profile` | Resident | First-login profile (owner name, vehicles) |
| PUT | `/portal/vehicles` | Resident | Edit vehicles only |
| GET | `/portal/invoices/{id}/pay-now` | Resident | Payment gateway link |
| POST | `/portal/invoices/{id}/pay-cash` | Resident | Cash payment + proof upload |
| GET | `/portal/payments/{id}/receipt` | Resident | Download receipt |
| POST | `/payment/webhook` | Gateway | Payment confirmation callback |

## Project Structure

```
SocietyManagement/
├── backend/
│   ├── app/
│   │   ├── api/          # REST endpoints
│   │   ├── auth/         # JWT + role guards
│   │   ├── config/       # Apartment, flats, passwords
│   │   ├── database/     # SQL connection
│   │   ├── schemas/      # Pydantic models
│   │   └── services/     # Business logic
│   ├── database/         # schema.sql + migrations
│   ├── uploads/          # Payment proof images
│   └── setup_db.py
└── scripts/
```

## Troubleshooting

- **Database connection failed** — Verify SQL Server is running and `DB_SERVER` in `.env` matches your instance.
- **401 on API calls** — Log in again; JWT expires after 24 hours.
- **Committee role rejected** — Each designation can only be held by one resident at a time.
