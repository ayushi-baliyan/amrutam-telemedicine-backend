# Security & Threat Model

## 1. Security Objectives

The Amrutam Telemedicine Backend handles user accounts, doctor information, consultations, prescriptions, and audit records.

The main security objectives are:

- Protect user authentication credentials.
- Prevent unauthorized access to patient and doctor data.
- Enforce role-based access control.
- Protect consultation and prescription information.
- Prevent duplicate or manipulated bookings.
- Maintain an audit trail for sensitive operations.
- Protect application configuration and database credentials.
- Reduce API abuse through rate limiting.

---

## 2. Data Classification

| Data | Classification | Protection |
|------|----------------|------------|
| User email | Personal | Authentication and access control |
| User phone | Personal | Access control |
| User password | Sensitive | Django password hashing |
| Doctor registration number | Sensitive | Access control |
| Consultation information | Sensitive | Role-based authorization |
| Prescription information | Highly Sensitive | Patient/doctor authorization |
| Audit logs | Sensitive | Restricted access |
| Database credentials | Secret | Environment variables |
| JWT tokens | Sensitive | Token-based authentication |

---

## 3. Authentication

The API uses JWT authentication for protected endpoints.

Access tokens are short-lived and are configured with a 30-minute lifetime.

Refresh tokens are configured with a 1-day lifetime.

Protected APIs require a valid JWT access token.

Example:

```text
Authorization: Bearer <access-token>
4. Authorization

Role-based authorization is implemented using application roles:

PATIENT
DOCTOR
ADMIN

Examples:

Patient

Patients can:

View their consultations.
Book available consultation slots.
Access their own prescriptions.
Doctor

Doctors can:

Create availability slots.
View their consultations.
Update consultation status.
Create prescriptions for their own consultations.
Admin

Administrative access is restricted to privileged operations.

5. Threat Model
Threat 1 — Unauthorized API Access
Risk

An unauthenticated user could attempt to access protected resources.

Mitigation

JWT authentication and DRF permission classes are used for protected endpoints.

Threat 2 — Broken Object Level Authorization
Risk

A patient could attempt to access another patient's consultation or prescription by changing an object ID.

Mitigation

The API filters consultations and prescriptions according to the authenticated user.

Doctors can access only consultations and prescriptions associated with their own doctor profile.

Patients can access only their own records.

Threat 3 — Double Booking
Risk

Two patients could attempt to book the same availability slot simultaneously.

Mitigation

The booking workflow uses:

select_for_update()

inside a database transaction.

The availability slot is locked while the booking transaction is processed.

Threat 4 — Duplicate Booking Requests
Risk

Network retries or duplicate client requests could create multiple consultations.

Mitigation

The booking endpoint requires an Idempotency-Key.

Repeated requests using the same key return the existing consultation instead of creating another one.

Threat 5 — API Abuse
Risk

An attacker could send a large number of API requests.

Mitigation

DRF throttling is configured.

Anonymous users:

100 requests/hour

Authenticated users:

1000 requests/hour
Threat 6 — Credential Exposure
Risk

Database credentials or application secrets could accidentally be committed to source control.

Mitigation

Configuration values are loaded from environment variables.

Sensitive .env files should not be committed to the Git repository.

A .env.example file can contain the required variable names without real secrets.

Threat 7 — Malicious Input
Risk

Invalid or malicious input could reach application logic.

Mitigation

Django REST Framework serializers validate API input before database operations.

Database constraints provide an additional layer of data integrity.

Threat 8 — Clickjacking
Risk

Attackers could attempt to embed the application in a malicious iframe.

Mitigation

The application configures:

X_FRAME_OPTIONS = "DENY"
Threat 9 — MIME Sniffing
Risk

Browsers could incorrectly interpret response content types.

Mitigation

The application configures:

SECURE_CONTENT_TYPE_NOSNIFF = True
Threat 10 — Audit Tampering
Risk

Sensitive actions could occur without an audit trail.

Mitigation

Important operations create audit log entries containing:

Actor
Action
Resource
Resource ID
IP address
Metadata
Timestamp
6. Security Controls

The current implementation includes:

JWT authentication
Role-based authorization
Serializer validation
API throttling
CORS configuration
X-Frame-Options
Content-type protection
Environment-based configuration
Database constraints
Audit logging
Transactional booking
Row-level locking
Idempotency protection
7. Production Security Checklist

Before production deployment:

 Set DEBUG=False
 Use a strong production SECRET_KEY
 Store secrets in a secret manager
 Use HTTPS
 Restrict CORS to trusted frontend domains
 Configure secure cookies where applicable
 Configure HTTPS-related security headers
 Enable database encryption at rest
 Encrypt backups
 Configure database access restrictions
 Enable dependency vulnerability scanning
 Rotate secrets periodically
 Monitor authentication failures
 Monitor suspicious API activity
 Test database backup restoration
8. Security Incident Response

If suspicious activity is detected:

Identify the affected account or resource.
Review audit logs.
Review application logs.
Revoke or rotate compromised credentials.
Disable affected accounts if necessary.
Investigate the affected resources.
Restore from a known-good backup if required.
Document the incident and remediation.
9. Future Improvements

Future production improvements can include:

Multi-factor authentication enforcement
Redis-based distributed rate limiting
Secret management using a cloud secret manager
Web Application Firewall
Centralized logging
Distributed tracing
Automated dependency scanning
Database encryption and key rotation
Security monitoring and alerting

### Save karo

```text
Ctrl + S

Ab docs folder me:

docs/
├── architecture.md
├── er-diagram.md
├── booking-sequence.md
└── security-threat-model.md