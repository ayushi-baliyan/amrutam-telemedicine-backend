# Amrutam Telemedicine Backend — Architecture

## 1. Overview

The Amrutam Telemedicine Backend is a production-oriented REST API designed to support telemedicine workflows such as user authentication, doctor discovery, doctor availability, consultation booking, prescriptions, and audit logging.

The backend is implemented using:

- Python
- Django
- Django REST Framework
- PostgreSQL
- JWT Authentication
- Docker
- GitHub Actions

The architecture focuses on security, reliability, scalability, observability, and maintainability.

---

## 2. High-Level Architecture

```text
                    ┌─────────────────────┐
                    │   Client / Frontend │
                    └──────────┬──────────┘
                               │ HTTPS
                               ▼
                    ┌─────────────────────┐
                    │     API Layer       │
                    │ Django REST API     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌───────────┐    ┌────────────┐   ┌─────────────┐
        │   Users   │    │  Doctors   │   │Consultations│
        └───────────┘    └────────────┘   └─────────────┘
              │                │                │
              │                │                ▼
              │                │         ┌──────────────┐
              │                │         │Prescriptions │
              │                │         └──────────────┘
              │                │
              └────────────────┼─────────────────┐
                               ▼                 ▼
                       ┌──────────────┐   ┌─────────────┐
                       │ PostgreSQL   │   │ Audit Logs  │
                       └──────────────┘   └─────────────┘
3. Main Components
Users

The users module manages:

Patient accounts
Doctor accounts
Admin users
User roles
Email
Phone number
MFA configuration

JWT authentication is used for API authentication.

Doctors

The doctors module manages:

Doctor profiles
Specialization
Qualification
Experience
Registration number
Consultation fee
Verification status
Availability status
Availability slots

Doctor search supports filtering by specialization, verification status, availability, experience, and search terms.

Consultations

The consultation module manages:

Appointment booking
Consultation status
Patient-doctor relationship
Availability slot relationship
Consultation notes

The booking workflow uses database transactions and row-level locking to prevent double booking.

Prescriptions

The prescription module allows doctors to create and update prescriptions associated with consultations.

Patients can access their own prescriptions, while doctors can access prescriptions belonging to their consultations.

Audit Logs

Security-sensitive operations generate audit records containing:

Actor
Action
Resource type
Resource ID
IP address
Metadata
Timestamp
4. Authentication and Authorization

JWT authentication is used for protected API endpoints.

The system defines three main roles:

PATIENT
DOCTOR
ADMIN

Role-based authorization ensures that users can only perform operations permitted for their role.

Examples:

Patients can book consultations.
Doctors can create availability slots.
Doctors can create prescriptions.
Users can access their own consultation data.
Doctors can access consultations assigned to them.
5. Booking Flow

The consultation booking process follows these steps:

Patient authenticates using JWT.
Patient sends a booking request.
API validates the slot and idempotency key.
Database transaction starts.
The requested availability slot is locked using select_for_update().
The API verifies that the slot is still available.
Consultation is created.
Slot status changes from AVAILABLE to BOOKED.
Audit log is created.
Transaction commits.
API returns the consultation response.

Row-level locking prevents two concurrent requests from successfully booking the same slot.

6. Idempotency

Booking requests require an Idempotency-Key header.

If the same patient retries a request using the same key, the existing consultation is returned instead of creating another consultation.

If another patient attempts to reuse an existing key, the request is rejected.

This protects the booking workflow against duplicate requests caused by:

Network retries
Client retries
Duplicate button clicks
Temporary connection failures
7. Database Design

PostgreSQL is used as the primary relational database.

Core entities include:

Users
Doctors
Availability Slots
Consultations
Prescriptions
Audit Logs

Foreign keys and unique constraints maintain data integrity.

Important constraints include:

Unique doctor registration number
Unique doctor slot start time
One consultation per availability slot
Unique idempotency key
One prescription per consultation
8. Security

Security controls implemented in the backend include:

JWT authentication
Role-based authorization
Input validation
API throttling
CORS configuration
Secure content type headers
X-Frame-Options
Environment-based configuration
Audit logging
Database-level constraints
Protected prescription and consultation access

Secrets such as database credentials are stored through environment variables rather than application code.

9. Rate Limiting

DRF throttling is enabled for anonymous and authenticated users.

Default limits:

Anonymous users: 100 requests/hour
Authenticated users: 1000 requests/hour

These limits provide basic protection against API abuse.

10. Reliability

The backend uses database transactions for critical workflows.

The booking flow uses row-level locking to prevent concurrent booking conflicts.

Idempotency protects against duplicate booking requests.

The health endpoint verifies application and database connectivity.

The endpoint is:

GET /health/

11. Observability

The backend provides:

Structured application logging
Health checks
Audit logs
API request status logging
OpenAPI documentation

The API documentation is available through Swagger UI.

Endpoint:

/api/docs/

12. Scalability

The backend is designed so that the API layer can be horizontally scaled.

Multiple application instances can run behind a load balancer.

PostgreSQL remains the primary source of truth.

Potential future scalability improvements include:

Redis caching
Background task queues
Read replicas
Database connection pooling
Message queues
Dedicated search infrastructure

The booking transaction remains protected by database locking even when multiple API instances are running.

13. Failure Handling

For transient failures, clients can safely retry idempotent operations.

For booking requests, the idempotency key prevents duplicate consultation creation.

Database transactions ensure that partially completed booking operations are rolled back.

Future production deployment can add:

Exponential backoff
Circuit breakers
Background job retries
Dead-letter queues
14. Deployment

The application can be containerized using Docker.

A production deployment can use:

Internet
   |
Load Balancer
   |
Django API Containers
   |
PostgreSQL
   |
Redis / Background Workers

CI/CD can automatically run:

Dependency installation
Django system checks
Database migrations
Automated tests
OpenAPI validation
15. Backup and Disaster Recovery

PostgreSQL should use automated backups in production.

Recommended production controls include:

Daily full backups
Point-in-time recovery
Backup encryption
Backup retention policies
Periodic restore testing

Recovery procedures should be documented and tested regularly.

16. Conclusion

The architecture separates major telemedicine responsibilities into modular Django applications while using PostgreSQL for transactional consistency.

The implementation prioritizes secure authentication, role-based authorization, reliable consultation booking, idempotency, auditability, API validation, and automated testing.

The architecture can be extended with Redis, asynchronous workers, read replicas, and horizontal API scaling as traffic increases.