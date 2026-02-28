# 🚀 Warehouse ERP API

Welcome to the backend for the Warehouse Inventory and Logistic ERP System. 

This project is built fully asynchronously using **FastAPI** and **asyncpg**, connecting directly to a **Neon PostgreSQL Database**. 

---

## 🏗️ 1. Project Setup
This project uses [uv](https://docs.astral.sh/uv/) as the package manager instead of basic pip for lightning-fast dependency resolution.

**Prerequisites:**
1. Install Python 3.12+
2. Install `uv`: 
   - Windows: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
   - Mac/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`

**Installation:**
Clone the repository and install dependencies:
```bash
git clone <repository_url>
cd "Warehouse ERp"

# This will automatically create a `.venv` and install everything from pyproject.toml
uv sync
```

---

## 🔑 2. Environment Variables (`.env`)
Before running the app, you MUST create a `.env` file in the root directory. **Do not commit this file to git.**

Create `.env` and paste the following, replacing the Neon URL with the real one from our team dashboard:


## 💻 3. Running Locally (Development)
The fastest way to test code changes is to run the app directly on your machine. The server will auto-reload every time you save a python file.

```bash
# Activate the virtual environment if not already activated
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

# Start the server
python main.py
```
> **Note:** We use a wrapper in `main.py` that automatically launches `uvicorn app.main:app --reload`.

### Testing the Endpoints:
Once running, open your browser and go to:
👉 **http://127.0.0.1:8000/docs**

This opens the interactive Swagger UI where you can test all the Supplier and Bank Details endpoints directly.

---

## 🐳 4. Running with Docker
If you want to test the production build or don't want to install Python locally, you can run the app via Docker.

**Build the image:**
```bash
docker build -t warehouse-erp .
```

**Run the container:**
*(Note: It reads your `.env` file automatically to inject the Neon credentials)*
```bash
docker run --env-file .env -p 8000:8000 warehouse-erp
```
The API docs will be available at http://localhost:8000/docs

---

## 📂 5. Architecture & File Structure
We use a standard layered architecture to keep routing isolated from database logic.

```
app/
├── main.py              # App definition & lifespan events (pool startup)
├── database.py          # asyncpg connection pool configuration
├── config.py            # Pydantic settings loading from .env
├── api/
│   └── v1/
│       ├── api.py       # Central router registration
│       └── endpoints/   # FastAPI Route definitions (Controllers)
├── dto/                 # Data Transfer Objects (Pydantic Models)
└── repositories/        # Database Access Layer (Raw SQL queries via asyncpg)
```

### 🧠 Important Development Rules:
1. **Never use ORMs like SQLAlchemy here**. We use raw SQL queries via `asyncpg` within the `repositories/` folder for maximum performance.
2. **Handle Neon Idle Timeouts**. Neon serverless DBs go to sleep after inactivity. Our `database.py` connection pool handles this, but be aware that the *first* request of the day might take 2-3 seconds as the DB wakes up.
3. **DTO Separation**. Keep `Supplier` and `SupplierBankDetails` Pydantic models in their respective files inside the `app/dto/` folder to avoid circular imports.
