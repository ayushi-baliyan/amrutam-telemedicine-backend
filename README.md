# Amrutam Telemedicine Backend

A production-oriented REST API backend for a scalable telemedicine platform.

The backend supports authentication, role-based access control, doctor discovery, availability management, consultation booking, prescriptions, payments, audit logging, admin analytics, API documentation, automated testing, health monitoring, Prometheus metrics, and CI validation.

---

## Tech Stack

- Python 3.14+
- Django 6
- Django REST Framework
- PostgreSQL 18
- JWT Authentication
- drf-spectacular
- django-prometheus
- Docker
- Gunicorn
- GitHub Actions

---

## Core Features

### Authentication

- JWT-based authentication
- Access and refresh tokens
- Token refresh support
- Role-based users
- Patient, Doctor and Admin roles
- Protected API endpoints

### Doctor Management

- Doctor profiles
- Specialization
- Qualification
- Experience
- Registration number
- Consultation fee
- Verification status
- Availability status
- Doctor search
- Doctor filtering

### Doctor Availability

Doctors can create and manage availability slots.

Each slot contains:

- Doctor
- Start time
- End time
- Status
- Created/updated timestamps

Slot states:

```text
AVAILABLE
BOOKED
BLOCKED

Consultation Booking

Patients can book available doctor slots.

The booking workflow provides:

Database transactions
Row-level locking using select_for_update()
Idempotency
Double-booking protection
Doctor availability validation
Audit logging
Concurrent booking protection
Prescriptions

Doctors can:

Create prescriptions
Update prescriptions
Access prescriptions for their consultations

Patients can:

View their own prescriptions

Prescription data includes:

Medicines
Instructions
Consultation reference
Timestamps
Payments

The backend includes a payment workflow associated with consultations.

Supported payment methods:

UPI
CARD
NET_BANKING
WALLET

Payment states:

PENDING
SUCCESS
FAILED
REFUNDED

Payment features:

Patient-only payment creation
Server-side consultation fee calculation
Payment idempotency
Duplicate payment protection
Transactional payment creation
Payment access control
Payment audit logging
Admin Analytics

Admin users can access platform-level analytics including:

Total users
Total patients
Total doctors
Total admins
Verified doctors
Available doctors
Total consultations
Consultation status counts
Total payments
Payment status counts

Endpoint:

GET /api/users/admin/analytics/

Only users with the ADMIN role can access this endpoint.

Audit Logging

Sensitive operations generate audit records containing:

Actor
Action
Resource type
Resource ID
IP address
Metadata
Timestamp

Audit logging is implemented for important workflows such as:

Consultation booking
Prescription creation/update
Payment creation
API Protection

The backend includes:

JWT authentication
Role-based authorization
Input validation
API throttling
CORS configuration
Security headers
Environment-based configuration
Database constraints
Transactional workflows
Idempotency protection
Observability

The backend provides basic production observability capabilities.

Health Check
GET /health/

Example:

{
  "status": "ok",
  "database": "ok"
}

The health endpoint verifies database connectivity and returns an appropriate HTTP status.

Prometheus Metrics

Metrics endpoint:

GET /metrics/

The backend uses django-prometheus to expose HTTP request and Django application metrics.

Application Logging

Structured console logging is configured for:

Django application events
HTTP request warnings/errors
Application-level logs
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
├── payments/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
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
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
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

Docker is supported through the included Docker configuration.

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

5. Run migrations
python manage.py migrate
6. Create admin user
python manage.py createsuperuser
7. Run development server
python manage.py runserver

The API will be available at:

http://127.0.0.1:8000/
Database

The project uses PostgreSQL for transactional consistency and relational data integrity.

Main database entities include:

Users
Doctors
Availability Slots
Consultations
Prescriptions
Payments
Audit Logs

Database constraints and transactions are used to protect critical workflows.

API Documentation
Swagger UI
/api/docs/
OpenAPI Schema
/api/schema/

The OpenAPI schema is validated using:

python manage.py spectacular --file schema.yml --validate
Main API Endpoints
Users
GET  /api/users/me/
POST /api/users/token/
POST /api/users/token/refresh/
GET  /api/users/admin/analytics/
Doctors
GET  /api/doctors/
GET  /api/doctors/<id>/
GET  /api/doctors/availability/
POST /api/doctors/availability/

Doctor filtering examples:

/api/doctors/?specialization=Cardiology
/api/doctors/?verified=true
/api/doctors/?available=true
/api/doctors/?min_experience=5
/api/doctors/?search=doctor
Consultations
GET   /api/consultations/
POST  /api/consultations/book/
GET   /api/consultations/<id>/
PATCH /api/consultations/<id>/
PATCH /api/consultations/<id>/status/
Prescriptions
POST  /api/prescriptions/
GET   /api/prescriptions/<id>/
PATCH /api/prescriptions/<id>/
Payments
POST /api/payments/
GET  /api/payments/<id>/
Monitoring
GET /health/
GET /metrics/
Booking Request

Booking requires authentication and an idempotency key.

Example headers:

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
Booking Idempotency

The consultation booking endpoint requires an Idempotency-Key.

Example:

Idempotency-Key: booking-patient1-slot1

If the same booking request is retried using the same idempotency key, the existing consultation is returned instead of creating a duplicate consultation.

This protects the API against duplicate requests caused by:

Client retries
Network failures
Timeouts
Duplicate submissions
Concurrent Booking Protection

The booking workflow uses:

select_for_update()

inside a database transaction.

The availability slot is locked while the booking transaction is being processed.

Therefore, concurrent requests attempting to reserve the same slot are serialized and only one request can successfully book the available slot.

Payment Idempotency

Payment creation also requires an idempotency key.

Example:

Idempotency-Key: payment-patient1-consultation1

Repeated requests using the same key return the existing payment instead of creating a duplicate payment.

The payment amount is derived from the doctor's consultation fee on the server side.

Testing

Run the complete test suite:

python manage.py test

Current test suite:

14 tests — PASS

Tests cover areas including:

Authentication
Consultation booking
Duplicate booking protection
Booking idempotency
Concurrent booking protection
Doctor permissions
Availability permissions
Prescription permissions
Payment creation
Payment idempotency
Payment authorization
API authorization
CI/CD

GitHub Actions is configured to automatically run:

Dependency installation
Django system checks
Database migrations
Automated tests
OpenAPI schema validation

Workflow file:

.github/workflows/ci.yml

The CI environment uses PostgreSQL as a service dependency.

Docker

The repository includes:

Dockerfile
docker-compose.yml
.dockerignore

The Docker setup provides:

Python application container
PostgreSQL database container
Gunicorn application server
Database migrations during startup

Docker Desktop is not required for local development if the application is run directly with Python and PostgreSQL.

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
Protected resource access

See:

docs/security-threat-model.md

for the security and threat model.

Architecture Documentation

The repository includes dedicated architecture documentation:

docs/architecture.md
docs/er-diagram.md
docs/booking-sequence.md
docs/security-threat-model.md

These documents cover:

High-level architecture
Data flow
Database relationships
Booking sequence
Security threats
Mitigations
Scalability considerations
Reliability and Scalability

The backend is designed with:

PostgreSQL transactional consistency
Row-level locking
Idempotent operations
API throttling
Health checks
Audit logging
Modular Django applications
Database constraints
Server-side validation

Potential production scaling options include:

Redis caching
Background workers
Read replicas
Database connection pooling
Message queues
Horizontal API scaling
Centralized observability infrastructure
Production Checklist

Before production deployment:

Set DEBUG=False
Configure production secret management
Use HTTPS
Restrict CORS to trusted origins
Configure secure security headers
Use encrypted database storage
Enable automated backups
Configure monitoring
Configure centralized logging
Run dependency security scans
Configure database connection pooling
Test disaster recovery procedures
Configure production WSGI/ASGI deployment
Project Status

Core backend workflows have been implemented and tested.

Verification Status
Django system check       PASS
Migrations check          PASS
Automated tests            14 PASS
OpenAPI validation         PASS
Health check               PASS
Prometheus metrics         PASS
Swagger documentation      Available
JWT authentication         Implemented
Role-based access          Implemented
Booking idempotency        Implemented
Payment idempotency        Implemented
Audit logging              Implemented
Admin analytics            Implemented
CI workflow                Configured
Docker configuration       Included
License

This project was developed as part of a backend engineering assignment.

