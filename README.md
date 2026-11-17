# AI-Powered Resume Parser & Multi-Channel 2FA Onboarding Pipeline

A FastAPI backend for student registration. The user uploads a resume, the system reads the details, the user registers, verifies with a 2FA code, edits the profile, and gets redirected to the student dashboard.

## Tech Stack
- Python 3.11+, FastAPI
- PostgreSQL with SQLAlchemy (async) and asyncpg
- Pydantic v2 for validation
- Argon2id (passlib) for password hashing
- PyJWT for access tokens
- pdfplumber and python-docx for resume parsing
- pyotp for browser TOTP
- Alembic for database migrations

## Features
- Upload a PDF or DOCX resume and get Name, Email, Phone, Skills, Experience as JSON
- Register with a hashed password (Argon2id)
- 2FA by Email OTP, WhatsApp OTP, or Browser TOTP
- OTPs are stored as hashes and expire in 5 minutes
- JWT token after successful verification
- View and edit profile (protected by JWT)
- Dashboard endpoint with redirect URL

## Project Structure
```
resume_pipeline/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/      (user, resume, otp)
│   ├── schemas/     (auth, profile)
│   ├── services/    (parser, security, otp)
│   └── routers/     (resume, auth, profile)
├── alembic/         (migration scripts)
├── alembic.ini
├── requirements.txt
└── README.md
```

## Setup
1. Clone the repo and open the folder.
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install packages:
   ```
   pip install -r requirements.txt
   ```
4. Create a PostgreSQL database named `resume_db`.
5. Create a `.env` file in the root folder:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/resume_db
   SECRET_KEY=use-a-long-random-secret-key-of-32-characters-or-more
   SMTP_HOST=
   SMTP_PORT=587
   SMTP_USER=
   SMTP_PASSWORD=
   ```
   If SMTP is empty, OTPs are printed in the terminal (mock mode).

6. Create the database tables using Alembic:
   ```
   alembic upgrade head
   ```

## Run
```
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs to test the APIs.

## API Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/v1/resume/parse | Upload resume, get extracted JSON |
| POST | /api/v1/auth/register | Register user and send 2FA |
| POST | /api/v1/auth/verify-2fa | Verify code and get JWT token |
| GET | /api/v1/profile | View profile (token needed) |
| PATCH | /api/v1/profile | Update profile (token needed) |
| GET | /api/v1/dashboard | Get redirect URL /dashboard/student |

## Testing Flow
1. Parse a resume and note the `resume_id`.
2. Register with that `resume