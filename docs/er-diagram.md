# ER Diagram — Amrutam Telemedicine Backend

```text
┌──────────────────────────┐
│          USERS           │
├──────────────────────────┤
│ PK id                    │
│ username                 │
│ email                    │
│ password                │
│ role                     │
│ phone                    │
│ is_mfa_enabled           │
│ created_at               │
│ updated_at               │
└────────────┬─────────────┘
             │
             │ 1 : 1
             ▼
┌──────────────────────────┐
│         DOCTORS          │
├──────────────────────────┤
│ PK id                    │
│ FK user_id               │
│ specialization           │
│ qualification            │
│ experience_years         │
│ registration_number      │
│ consultation_fee         │
│ bio                      │
│ is_verified              │
│ is_available             │
│ created_at               │
│ updated_at               │
└────────────┬─────────────┘
             │
             │ 1 : N
             ▼
┌──────────────────────────┐
│    AVAILABILITY_SLOTS    │
├──────────────────────────┤
│ PK id                    │
│ FK doctor_id             │
│ start_time               │
│ end_time                 │
│ status                   │
│ created_at               │
│ updated_at               │
└────────────┬─────────────┘
             │
             │ 1 : 0..1
             ▼
┌──────────────────────────┐
│      CONSULTATIONS       │
├──────────────────────────┤
│ PK id                    │
│ FK patient_id            │
│ FK doctor_id             │
│ FK slot_id               │
│ status                   │
│ idempotency_key          │
│ notes                    │
│ created_at               │
│ updated_at               │
└────────────┬─────────────┘
             │
             │ 1 : 0..1
             ▼
┌──────────────────────────┐
│       PRESCRIPTIONS      │
├──────────────────────────┤
│ PK id                    │
│ FK consultation_id       │
│ medicines                │
│ instructions             │
│ created_at               │
│ updated_at               │
└──────────────────────────┘


USERS
  │
  │ 1 : N
  ▼
┌──────────────────────────┐
│        AUDIT_LOGS        │
├──────────────────────────┤
│ PK id                    │
│ FK actor_id              │
│ action                   │
│ resource_type            │
│ resource_id              │
│ ip_address               │
│ metadata                 │
│ created_at               │
└──────────────────────────┘
Relationships
User → Doctor

One user can have one doctor profile.

USERS 1 ───────── 1 DOCTORS

The relationship is implemented using a OneToOneField.

Doctor → Availability Slots

A doctor can have multiple availability slots.

DOCTORS 1 ───────── N AVAILABILITY_SLOTS
Availability Slot → Consultation

A slot can be associated with at most one consultation.

AVAILABILITY_SLOTS 1 ───── 0..1 CONSULTATIONS

This relationship helps prevent a slot from being booked multiple times.

User → Consultations

A patient can have multiple consultations.

USERS 1 ───────── N CONSULTATIONS

The patient is stored through patient_id.

Doctor → Consultations

A doctor can have multiple consultations.

DOCTORS 1 ───────── N CONSULTATIONS
Consultation → Prescription

A consultation can have at most one prescription.

CONSULTATIONS 1 ───── 0..1 PRESCRIPTIONS

The prescription uses a OneToOneField with the consultation.

User → Audit Logs

A user can generate multiple audit log entries.

USERS 1 ───────── N AUDIT_LOGS

The actor is nullable so that audit records can remain available even if the original user is deleted.