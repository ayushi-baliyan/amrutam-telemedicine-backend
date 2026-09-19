from django.utils import timezone
from datetime import timedelta

from rest_framework.test import APITestCase

from users.models import User
from doctors.models import Doctor, AvailabilitySlot
from .models import Consultation


class ConsultationAPITest(APITestCase):

    def setUp(self):
        self.patient = User.objects.create_user(
            username="patienttest",
            password="Patient@12345",
            role="PATIENT",
            email="patient@test.com",
        )

        self.doctor_user = User.objects.create_user(
            username="doctortest",
            password="Doctor@12345",
            role="DOCTOR",
            email="doctor@test.com",
        )

        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialization="Cardiology",
            qualification="MBBS",
            experience_years=5,
            registration_number="DOC-TEST-001",
            consultation_fee=500,
        )

        self.slot = AvailabilitySlot.objects.create(
            doctor=self.doctor,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, minutes=30),
        )

    def test_booking_requires_authentication(self):
        response = self.client.post(
            "/api/consultations/book/",
            {
                "slot": self.slot.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_patient_can_book(self):
        self.client.force_authenticate(
            user=self.patient
        )

        response = self.client.post(
            "/api/consultations/book/",
            {
                "slot": self.slot.id,
                "notes": "Test consultation",
            },
            HTTP_IDEMPOTENCY_KEY="test-booking-001",
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_idempotent_booking(self):
        self.client.force_authenticate(
            user=self.patient
        )

        data = {
            "slot": self.slot.id,
            "notes": "Test consultation",
        }

        first = self.client.post(
            "/api/consultations/book/",
            data,
            HTTP_IDEMPOTENCY_KEY="same-key",
            format="json",
        )

        second = self.client.post(
            "/api/consultations/book/",
            data,
            HTTP_IDEMPOTENCY_KEY="same-key",
            format="json",
        )

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)

        self.assertEqual(
            first.data["id"],
            second.data["id"],
        )

    def test_double_booking_blocked(self):
        self.client.force_authenticate(
            user=self.patient
        )

        self.client.post(
            "/api/consultations/book/",
            {"slot": self.slot.id},
            HTTP_IDEMPOTENCY_KEY="booking-one",
            format="json",
        )

        another_patient = User.objects.create_user(
            username="anotherpatient",
            password="Patient@12345",
            role="PATIENT",
            email="another@test.com",
        )

        self.client.force_authenticate(
            user=another_patient
        )

        response = self.client.post(
            "/api/consultations/book/",
            {"slot": self.slot.id},
            HTTP_IDEMPOTENCY_KEY="booking-two",
            format="json",
        )

        self.assertEqual(response.status_code, 409)