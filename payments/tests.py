from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase

from consultations.models import Consultation
from doctors.models import AvailabilitySlot, Doctor
from users.models import User

from .models import Payment


class PaymentAPITests(APITestCase):

    def setUp(self):
        self.patient = User.objects.create_user(
            username="payment_patient",
            password="Patient@12345",
            email="payment_patient@example.com",
            role=User.Role.PATIENT,
        )

        self.other_patient = User.objects.create_user(
            username="other_payment_patient",
            password="Patient@12345",
            email="other_payment_patient@example.com",
            role=User.Role.PATIENT,
        )

        self.doctor_user = User.objects.create_user(
            username="payment_doctor",
            password="Doctor@12345",
            email="payment_doctor@example.com",
            role=User.Role.DOCTOR,
        )

        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialization="General Physician",
            qualification="MBBS",
            experience_years=5,
            registration_number="PAY-TEST-001",
            consultation_fee=Decimal("800.00"),
            is_verified=True,
            is_available=True,
        )

        self.slot = AvailabilitySlot.objects.create(
            doctor=self.doctor,
            start_time="2027-01-10T10:00:00Z",
            end_time="2027-01-10T10:30:00Z",
            status=AvailabilitySlot.Status.BOOKED,
        )

        self.consultation = Consultation.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            slot=self.slot,
            status=Consultation.Status.BOOKED,
            idempotency_key="consultation-payment-test-001",
        )

        self.url = reverse("payment-create")

    def test_patient_can_create_payment(self):
        self.client.force_authenticate(user=self.patient)

        response = self.client.post(
            self.url,
            {
                "consultation": self.consultation.id,
                "method": "UPI",
            },
            format="json",
            HTTP_IDEMPOTENCY_KEY="payment-test-001",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], Payment.Status.PENDING)
        self.assertEqual(response.data["amount"], "800.00")
        self.assertEqual(response.data["currency"], "INR")

    def test_same_idempotency_key_returns_same_payment(self):
        self.client.force_authenticate(user=self.patient)

        headers = {
            "HTTP_IDEMPOTENCY_KEY": "payment-idempotency-test"
        }

        first_response = self.client.post(
            self.url,
            {
                "consultation": self.consultation.id,
                "method": "UPI",
            },
            format="json",
            **headers,
        )

        second_response = self.client.post(
            self.url,
            {
                "consultation": self.consultation.id,
                "method": "UPI",
            },
            format="json",
            **headers,
        )

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(
            first_response.data["id"],
            second_response.data["id"],
        )
        self.assertEqual(Payment.objects.count(), 1)

    def test_payment_requires_idempotency_key(self):
        self.client.force_authenticate(user=self.patient)

        response = self.client.post(
            self.url,
            {
                "consultation": self.consultation.id,
                "method": "UPI",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_other_patient_cannot_pay_for_consultation(self):
        self.client.force_authenticate(user=self.other_patient)

        response = self.client.post(
            self.url,
            {
                "consultation": self.consultation.id,
                "method": "UPI",
            },
            format="json",
            HTTP_IDEMPOTENCY_KEY="other-patient-payment-test",
        )

        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_user_cannot_create_payment(self):
        response = self.client.post(
            self.url,
            {
                "consultation": self.consultation.id,
                "method": "UPI",
            },
            format="json",
            HTTP_IDEMPOTENCY_KEY="unauthenticated-payment-test",
        )

        self.assertEqual(response.status_code, 401)