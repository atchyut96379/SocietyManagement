# Marvel Rocks — Azure Deployment Guide

Use this guide with your existing Azure resources in **rg-marvelrocks-prod**.

| Resource | Name | Purpose |
|----------|------|---------|
| Static Web App | `marvelrocks-web` | React frontend → **www.marvelrocks.in** |
| App Service | `marvelrocks-api` | FastAPI backend → **api.marvelrocks.in** |
| SQL Server | `marvelrocks-sql-96379` | Database server |
| SQL Database | `mygatesociety` | Application data |
| Container Registry | `marvelrocksacr` | API Docker images |

---

## Part 1 — Azure SQL firewall (one time)

1. Azure Portal → **SQL servers** → `marvelrocks-sql-96379`
2. **Networking** → check **Allow Azure services and resources to access this server**
3. Add your PC public IP (for running `setup_db.py` from home)
4. Save

---

## Part 2 — Initialize database

On your PC, create `backend/.env` (never commit this file).

**Option A — separate variables (Azure App Service):**

```env
DB_SERVER=marvelrocks-sql-96379.database.windows.net
DB_DATABASE=mygatesociety
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_USER=YOUR_SQL_ADMIN
DB_PASSWORD=YOUR_SQL_PASSWORD
```

**Option B — legacy `DATABASE_URL` from old MyGate project:**

```env
DATABASE_URL=sqlserver://marvelrocks-sql-96379.database.windows.net:1433;database=mygatesociety;user=YOUR_USER;password=YOUR_PASSWORD;encrypt=true;trustServerCertificate=true
```

**Shared settings (both options):**

```env
JWT_SECRET=create-a-long-random-secret-here
FRONTEND_URL=https://www.marvelrocks.in,https://marvelrocks-web.azurestaticapps.net
APARTMENT_NAME=Marvel Rock Flat Owners Welfare Association
SOCIETY_REG_NO=316/2024
SOCIETY_ADDRESS=Sangivalasa, Bheemunipatnam Mandal, Visakhapatnam
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret
RAZORPAY_TEST_MODE=false
```

| Old project variable | This project |
|---------------------|--------------|
| `DATABASE_URL` (localhost) | Use Azure host: `marvelrocks-sql-96379.database.windows.net` |
| `JWT_SECRET` | Same name |
| `RAZORPAY_KEY_ID` / `SECRET` | Same names |
| `CRON_SECRET` | Not used |
| `VAPID_*` | Not used (no push notifications yet) |

Run migrations and seed data:

```powershell
cd backend
.\venv\Scripts\pip.exe install -r requirements.txt
.\venv\Scripts\python.exe setup_db.py
```

---

## Part 3 — Configure API App Service (`marvelrocks-api`)

Azure Portal → **marvelrocks-api** → **Settings** → **Environment variables** → add:

| Name | Value |
|------|--------|
| `DB_SERVER` | `marvelrocks-sql-96379.database.windows.net` |
| `DB_DATABASE` | `mygatesociety` |
| `DB_DRIVER` | `ODBC Driver 18 for SQL Server` |
| `DB_USER` | SQL admin username |
| `DB_PASSWORD` | SQL admin password |
| `JWT_SECRET` | same as local |
| `FRONTEND_URL` | `https://www.marvelrocks.in,https://marvelrocks-web.azurestaticapps.net` |
| `APARTMENT_NAME` | `Marvel Rock Flat Owners Welfare Association` |
| `SOCIETY_REG_NO` | `316/2024` |
| `SOCIETY_ADDRESS` | `Sangivalasa, Bheemunipatnam Mandal, Visakhapatnam` |
| `RAZORPAY_KEY_ID` | Your Razorpay key |
| `RAZORPAY_KEY_SECRET` | Your Razorpay secret |
| `RAZORPAY_TEST_MODE` | `false` |
| `WEBSITES_PORT` | `8000` |
| `PORT` | `8000` |

Alternatively set a single `DATABASE_URL` instead of `DB_SERVER` / `DB_USER` / `DB_PASSWORD`.

### Connect API to Container Registry

1. **marvelrocks-api** → **Deployment Center**
2. Source: **Container Registry** → `marvelrocksacr`
3. Image: `society-management-api:latest`
4. Enable **Continuous deployment**

Or use GitHub Actions (Part 5).

### Custom domain for API

1. **marvelrocks-api** → **Custom domains** → Add `api.marvelrocks.in`
2. Copy the CNAME target shown by Azure

---

## Part 4 — Configure Static Web App (`marvelrocks-web`)

### Custom domain for frontend

1. **marvelrocks-web** → **Custom domains** → `www.marvelrocks.in` (may already exist)
2. This replaces the old website when new build is deployed

### GitHub deployment

1. **marvelrocks-web** → **Manage deployment token** → copy token
2. Add to GitHub repo secrets (Part 5)

---

## Part 5 — GitHub secrets

GitHub → **SocietyManagement** → **Settings** → **Secrets and variables** → **Actions**

| Secret | How to get it |
|--------|----------------|
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | marvelrocks-web → Manage deployment token |
| `REACT_APP_API_URL` | `https://api.marvelrocks.in` (or `https://marvelrocks-api.azurewebsites.net` until DNS is ready) |
| `AZURE_CREDENTIALS` | Azure CLI service principal JSON (see below) |
| `ACR_USERNAME` | marvelrocksacr → Access keys → Username |
| `ACR_PASSWORD` | marvelrocksacr → Access keys → password |

### Create AZURE_CREDENTIALS (PowerShell)

```powershell
az login
az ad sp create-for-rbac --name "github-marvelrocks-deploy" --role contributor --scopes /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/rg-marvelrocks-prod --sdk-auth
```

Copy the full JSON output into GitHub secret `AZURE_CREDENTIALS`.

Grant the service principal **AcrPush** on `marvelrocksacr`:

```powershell
az role assignment create --assignee APP_ID_FROM_JSON --role AcrPush --scope /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/rg-marvelrocks-prod/providers/Microsoft.ContainerRegistry/registries/marvelrocksacr
```

---

## Part 6 — Deploy from GitHub

Push code to `master`. Two workflows run automatically:

- **deploy-marvelrocks-web.yml** → builds React → deploys to Static Web App
- **deploy-marvelrocks-api.yml** → builds Docker image → pushes to ACR → updates API

Manual run: GitHub → **Actions** → select workflow → **Run workflow**

---

## Part 7 — Hostinger DNS (marvelrocks.in)

| Type | Name | Value |
|------|------|--------|
| CNAME | `www` | value from Static Web App custom domain |
| CNAME | `api` | `marvelrocks-api.azurewebsites.net` |

Wait 15–60 minutes, then test:

- https://www.marvelrocks.in
- https://api.marvelrocks.in/
- Login: `9999999999` / `Admin@123`

---

## Part 8 — Verify

| Check | Expected |
|-------|----------|
| API root | `{"message":"Society Management API Running Successfully"}` |
| Frontend | Login page loads |
| Login | Admin dashboard opens |
| Portal | Resident can view monthly reports |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| API 500 / DB error | Check env vars on marvelrocks-api; verify SQL firewall |
| CORS error | Add your URL to `FRONTEND_URL` on API |
| Blank page after login | Check `REACT_APP_API_URL` secret matches live API URL |
| 404 on refresh | `staticwebapp.config.json` is deployed (included in repo) |

---

## Default logins (after setup_db)

| Role | Mobile | Password |
|------|--------|----------|
| Admin | `9999999999` | `Admin@123` |
| Secretary | auto | `MyGaSec` (if APARTMENT_NAME=MyGate…) |

Change passwords after first production login.
