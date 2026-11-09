# Nestack Secure Records API

**Cybersecurity Technical Assessment – Secure Multi-Tenant Records API**

## 1. Project Overview

Nestack Secure Records API is a Python-based REST API designed to demonstrate secure authentication, session management, multi-tenant data isolation, and role-based access control.

The application allows registered users to create and access their own private records. Administrators can access records across users.

The implementation focuses on preventing common security vulnerabilities, including broken access control, unauthorized privilege escalation, SQL injection, credential exposure, and brute-force login attempts.

## 2. Technology Stack

- **Language:** Python
- **Backend Framework:** FastAPI
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Password Hashing:** Argon2id
- **Authentication:** Custom opaque bearer-token sessions
- **Validation:** Pydantic
- **Testing:** Pytest and HTTPX

## 3. Project Structure

```text
Nestack_Submission/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   │
│   ├── security/
│   │   ├── passwords.py
│   │   ├── sessions.py
│   │   └── permissions.py
│   │
│   └── routes/
│       ├── auth.py
│       └── records.py
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_access_control.py
│   └── test_lockout.py
│
├── scripts/
│   └── create_admin.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 4. Installation and Setup

### Prerequisites

- Python 3.10 or later
- pip
- Git

### Step 1: Clone the repository

```bash
git clone <https://github.com/M-sahithya/VenkataNagaSahithyaMitta_Nestack_Submission>
cd Nestack_Submission
```

### Step 2: Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Activate it on Linux/macOS:

```bash
source venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure environment variables

Create a `.env` file using `.env.example` as a reference.

Default configuration:

```env
DATABASE_URL=sqlite:///./nestack.db
SESSION_EXPIRE_MINUTES=30
```

Do not commit `.env` or database files to version control.

### Step 5: Start the application

```bash
uvicorn app.main:app --reload
```

Application URL:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

## 5. Security Implementation

### 5.1 Password Security

- Passwords are hashed using Argon2id.
- Plain-text passwords are never stored in the database.
- Password length and input validation are enforced.
- Password verification uses the Argon2 password verification implementation.

### 5.2 Session Management

- Sessions use cryptographically secure random opaque tokens.
- Raw session tokens are returned only to the authenticated client.
- SHA-256 hashes of session tokens are stored in the database.
- Sessions have a configurable expiration time.
- Expired sessions are rejected.
- Logout revokes the associated server-side session.

### 5.3 Authentication and Authorization

- Protected endpoints require bearer-token authentication.
- Unauthenticated requests are rejected with HTTP 401.
- Administrative access is controlled through server-side roles.
- Public registration always assigns the `user` role.
- Client-supplied role fields are rejected.

### 5.4 Multi-Tenant Data Isolation

- Every record is associated with an owner ID.
- The owner ID is assigned from the authenticated user's identity.
- Normal users can access only their own records.
- Administrators can access records across users.
- Unauthorized and nonexistent records return HTTP 404 to reduce record enumeration.

### 5.5 Brute-Force Protection

- Failed login attempts are tracked per account.
- Five consecutive failed login attempts trigger a temporary account lockout.
- The lockout duration is 15 minutes.
- Successful authentication resets the failed-attempt counter.

### 5.6 Input and Database Security

- Pydantic validates request data.
- Unexpected request fields are rejected.
- Invalid request data is returned as HTTP 400.
- SQLAlchemy ORM is used for parameterized database operations.
- Request bodies are limited to 16 KB.

## 6. API Endpoints

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| POST | `/register` | Register a new user | No |
| POST | `/login` | Authenticate and create session | No |
| POST | `/logout` | Revoke current session | Yes |
| POST | `/records` | Create a private record | Yes |
| GET | `/records/{record_id}` | Retrieve an authorized record | Yes |
| GET | `/` | Application status | No |
| GET | `/health` | Health check | No |

## 7. Administrator Account

An administrator can be created using:

```powershell
python -m scripts.create_admin
```

The script requests an administrator username and password through the terminal.

Administrator privileges are assigned server-side and cannot be obtained through public registration.

## 8. Testing

Run the automated test suite:

```bash
python -m pytest -v
```

The test suite covers the implemented authentication, registration, account lockout, record ownership, unauthorized access, administrator access, logout, request-size limits, and invalid record IDs.

**Test results:** Update this section with the actual final test count after running the complete test suite.

## 9. Threat Model

| Threat | Security Mitigation |
|---|---|
| Password exposure | Argon2id password hashing |
| Session token database exposure | SHA-256 token hashing |
| Session reuse after logout | Server-side session revocation |
| Brute-force login | Account lockout |
| Broken Object Level Authorization | Owner-based record filtering |
| Privilege escalation | Server-controlled roles |
| SQL injection | SQLAlchemy ORM parameterized operations |
| Invalid input | Strict Pydantic validation |
| Oversized request bodies | 16 KB request-size limit |

## 10. Assumptions and Limitations

- SQLite is used for the assessment environment.
- Session tokens are transmitted using the Authorization Bearer header.
- The implementation is designed as an assessment prototype, not a production deployment.
- Production deployment should use HTTPS, secure operational secrets, a production database, centralized rate limiting, audit logging, and hardened infrastructure.
- The current account lockout mechanism is application-level and should be strengthened with concurrency-safe atomic updates for production use.

## 11. Security Design Principles

The application follows these principles:

- Least privilege
- Secure password storage
- Server-side authorization
- Defense in depth
- Explicit input validation
- Secure session lifecycle management
- Multi-tenant data isolation

## 12. Author

Venkata Naga Sahithya Mitta

Cybersecurity | Application Security | API Security

Project: Nestack Secure Records API  
Purpose: Cybersecurity Technical Assessment
