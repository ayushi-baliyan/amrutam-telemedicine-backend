# Consultation Booking — Sequence Diagram

## Booking Flow

```text
Patient                API                 Database
   │                     │                     │
   │                     │                     │
   │  Login / JWT        │                     │
   ├────────────────────>│                     │
   │                     │                     │
   │<────────────────────┤                     │
   │       JWT Token     │                     │
   │                     │                     │
   │                     │                     │
   │ POST /book/         │                     │
   │ Idempotency-Key     │                     │
   ├────────────────────>│                     │
   │                     │                     │
   │                     │ Check existing      │
   │                     │ idempotency key     │
   │                     ├────────────────────>│
   │                     │                     │
   │                     │<────────────────────┤
   │                     │                     │
   │                     │ Begin Transaction   │
   │                     │                     │
   │                     │ SELECT slot         │
   │                     │ FOR UPDATE          │
   │                     ├────────────────────>│
   │                     │                     │
   │                     │<────────────────────┤
   │                     │ Slot locked         │
   │                     │                     │
   │                     │ Check slot status   │
   │                     │                     │
   │                     │ AVAILABLE?          │
   │                     │                     │
   │                     │ Create Consultation │
   │                     ├────────────────────>│
   │                     │                     │
   │                     │ Update Slot         │
   │                     │ AVAILABLE → BOOKED  │
   │                     ├────────────────────>│
   │                     │                     │
   │                     │ Create Audit Log    │
   │                     ├────────────────────>│
   │                     │                     │
   │                     │ Commit Transaction  │
   │                     ├────────────────────>│
   │                     │                     │
   │                     │<────────────────────┤
   │                     │                     │
   │<────────────────────┤                     │
   │  201 Created        │                     │
   │  Consultation       │                     │
   │                     │                     │
   Detailed Flow
1. Authentication

The patient first authenticates and receives a JWT access token.

The token is sent with subsequent protected API requests.

2. Booking Request

The patient sends:

POST /api/consultations/book/

The request contains the availability slot ID and an Idempotency-Key header.

Example:

Idempotency-Key: booking-patient1-slot1
3. Idempotency Check

The API first checks whether the idempotency key already exists.

If the same patient already created a consultation using the key, the existing consultation is returned.

This prevents duplicate bookings caused by retries.

4. Database Transaction

The booking operation runs inside a database transaction.

The requested availability slot is selected using:

select_for_update()

This locks the database row until the transaction completes.

5. Availability Validation

The API verifies:

The slot exists.
The slot is still available.
The doctor is available.

If the slot is already booked, the API returns:

409 Conflict
6. Consultation Creation

If the slot is available, the system creates a consultation containing:

Patient
Doctor
Availability slot
Consultation status
Idempotency key
Notes

The initial consultation status is:

BOOKED
7. Slot Update

After creating the consultation, the slot status changes:

AVAILABLE → BOOKED
8. Audit Logging

A CONSULTATION_BOOKED audit record is created.

The audit record contains information such as:

Actor
Consultation ID
Doctor ID
Slot ID
IP address
Timestamp
9. Transaction Commit

After all operations succeed, the transaction is committed.

If an error occurs before the commit, the transaction is rolled back.

This prevents partially completed bookings.

Concurrent Booking Protection

Consider two patients trying to book the same slot simultaneously.

Patient A ──┐
            ├──> Same Slot
Patient B ──┘

The database row lock ensures that only one transaction can modify the slot at a time.

Example:

Patient A
   │
   ├── SELECT ... FOR UPDATE
   │
   ├── Slot locked
   │
   ├── Create consultation
   │
   └── Slot → BOOKED
             │
             ▼
        Transaction commits

Patient B
   │
   └── waits for database lock
              │
              ▼
        Slot is now BOOKED
              │
              ▼
        409 Conflict

This prevents double booking.

Retry Protection

If the network fails after the booking is created, the client can retry using the same idempotency key.

Example:

First request:
Idempotency-Key: booking-patient1-slot1
→ Consultation #1 created

Retry:
Idempotency-Key: booking-patient1-slot1
→ Existing Consultation #1 returned

No duplicate consultation is created.
