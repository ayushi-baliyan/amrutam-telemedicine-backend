# Amrutam Telemedicine Backend

A production-oriented REST API backend for a telemedicine platform.

The backend supports authentication, role-based access control, doctor discovery, doctor availability, consultation booking, prescriptions, audit logging, API documentation, automated testing, and health monitoring.

---

## Tech Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- JWT Authentication
- drf-spectacular
- Docker
- GitHub Actions

---

## Features

### Authentication

- JWT-based authentication
- Access and refresh tokens
- Role-based users
- Patient, Doctor and Admin roles

### Doctor Management

- Doctor profiles
- Specialization
- Qualification
- Experience
- Registration number
- Consultation fee
- Verification status
- Availability status
- Doctor search and filtering

### Availability

Doctors can create availability slots.

Each slot contains:

- Start time
- End time
- Status
- Doctor

Slot states:

```text
AVAILABLE
BOOKED
BLOCKED
Consultation Booking

Patients can book available doctor slots.

The booking workflow provides:

Database transactions
Row-level locking
Idempotency
Double-booking protection
Audit logging
Prescriptions

Doctors can:

Create prescriptions
Update prescriptions

Patients can access their own prescriptions.

Prescription data includes medicines and instructions.

Audit Logging

Sensitive operations generate audit records containing:

Actor
Action
Resource type
Resource ID
IP address
Metadata
Timestamp
API Protection

The backend includes:

JWT authentication
Role-based authorization
Input validation
API throttling
CORS configuration
Security headers
Environment-based configuration
Project Structure
amrutam-telemedicine-backend/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   ├── asgi.py
│   └── wsgi.py
│
├── users/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── doctors/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── consultations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── prescriptions/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── audit_logs/
│   ├── models.py
│   ├── utils.py
│   └── admin.py
│
├── docs/
│   ├── architecture.md
│   ├── er-diagram.md
│   ├── booking-sequence.md
│   └── security-threat-model.md
│
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
Requirements

Make sure the following are installed:

Python 3.14+
PostgreSQL 18+
Git
Local Setup
1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd amrutam-telemedicine-backend
2. Create virtual environment

Windows:

python -m venv venv

Activate:

.\venv\Scripts\Activate.ps1
3. Install dependencies
python -m pip install -r requirements.txt
4. Configure environment variables

Create a .env file in the project root.

Example:

SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=amrutam_db
DB_USER=amrutam_user
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=5432

Do not commit the real .env file.

Database Setup

Create the PostgreSQL database:

CREATE DATABASE amrutam_db;

Create the database user:

CREATE USER amrutam_user WITH PASSWORD 'your-password';

Grant access:

GRANT ALL PRIVILEGES ON DATABASE amrutam_db TO amrutam_user;

Connect to the database:

\c amrutam_db

Grant schema permissions:

GRANT ALL ON SCHEMA public TO amrutam_user;
Run Migrations
python manage.py migrate
Create Superuser
python manage.py createsuperuser
Run Development Server
python manage.py runserver

The API will be available at:

http://127.0.0.1:8000/
Health Check
GET /health/

Example response:

{
    "status": "ok",
    "database": "ok"
}
API Documentation

Swagger UI:

/api/docs/

OpenAPI schema:

/api/schema/
Main API Endpoints
Users
POST /api/users/register/
GET  /api/users/me/
Authentication
POST /api/users/token/
POST /api/users/token/refresh/
Doctors
GET /api/doctors/
GET /api/doctors/<id>/
GET /api/doctors/availability/
POST /api/doctors/availability/

Doctor filtering examples:

/api/doctors/?specialization=Cardiology
/api/doctors/?verified=true
/api/doctors/?available=true
/api/doctors/?min_experience=5
/api/doctors/?search=doctor
Consultations
GET  /api/consultations/
POST /api/consultations/book/
GET  /api/consultations/<id>/
PATCH /api/consultations/<id>/
PATCH /api/consultations/<id>/status/
Prescriptions
POST /api/prescriptions/
GET  /api/prescriptions/<id>/
PATCH /api/prescriptions/<id>/
Booking Request

Booking requires authentication and an idempotency key.

Example header:

Authorization: Bearer <access-token>
Idempotency-Key: unique-booking-key

Example request:

{
    "slot": 1,
    "notes": "Regular consultation"
}

Successful response:

201 Created

If the slot has already been booked:

409 Conflict
Idempotency

The booking endpoint requires an Idempotency-Key.

Example:

Idempotency-Key: booking-patient1-slot1

If the same request is retried using the same key, the existing consultation is returned instead of creating a duplicate consultation.

Concurrent Booking Protection

The booking workflow uses:

select_for_update()

inside a database transaction.

This locks the availability slot during the booking operation.

Therefore, when multiple patients attempt to book the same slot concurrently, only one booking can successfully reserve the slot.

Testing

Run all tests:

python manage.py test

Current test suite covers:

Authentication
Consultation booking
Duplicate booking protection
Idempotency
Doctor permissions
Prescription permissions
API authorization
Validate OpenAPI Schema
python manage.py spectacular --file schema.yml --validate
Security

Security controls include:

JWT authentication
Role-based authorization
Input validation
API throttling
CORS restrictions
Security headers
Environment variables for secrets
Audit logging
Database constraints
Transactional booking
Row-level locking
Idempotency protection

See:

docs/security-threat-model.md

for the complete security and threat model.

Architecture Documentation

The architecture documentation is available in:

docs/architecture.md
docs/er-diagram.md
docs/booking-sequence.md
docs/security-threat-model.md
Reliability and Scalability

The system is designed with:

PostgreSQL transactional consistency
Row-level locking
Idempotent booking
API throttling
Health checks
Audit logging
Modular Django applications

Future scaling options include:

Redis caching
Background workers
Read replicas
Database connection pooling
Message queues
Horizontal API scaling
Production Checklist

Before production deployment:

Set DEBUG=False
Configure production secret management
Use HTTPS
Restrict CORS
Configure secure security headers
Use encrypted database storage
Enable automated backups
Configure monitoring
Configure centralized logs
Run dependency security scans
Test disaster recovery procedures
Project Documentation

Additional architecture and security documentation:

Architecture: docs/architecture.md
ER Diagram: docs/er-diagram.md
Booking Sequence: docs/booking-sequence.md
Security Threat Model: docs/security-threat-model.md
Status

Core backend workflows implemented and tested.

Automated test suite:

9 tests — PASS

Health check:

PASS

OpenAPI validation:

PASS

Swagger API documentation:

Available