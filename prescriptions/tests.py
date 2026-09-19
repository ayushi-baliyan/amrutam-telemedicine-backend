from django.utils import timezone
from datetime import timedelta

from rest_framework.test import APITestCase

from users.models import User
from doctors.models import Doctor, AvailabilitySlot
from consultations.models import Consultation


class PrescriptionAPITest(APITestCase):

    def setUp(self):
        self.patient = User.objects.create_user(
            username="prescriptionpatient",
            password="Patient@12345",
            role="PATIENT",
            email="prespatient@test.com",
        )

        self.doctor_user = User.objects.create_user(
            username="prescriptiondoctor",
            password="Doctor@12345",
            role="DOCTOR",
            email="presdoctor@test.com",
        )

        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialization="Cardiology",
            qualification="MBBS",
            experience_years=5,
            registration_number="PRES-DOC-001",
            consultation_fee=500,
        )

        self.slot = AvailabilitySlot.objects.create(
            doctor=self.doctor,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, minutes=30),
        )

        self.consultation = Consultation.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            slot=self.slot,
            status="BOOKED",
            idempotency_key="prescription-consultation",
        )

    def test_patient_cannot_create_prescription(self):
        self.client.force_authenticate(
            user=self.patient
        )

        response = self.client.post(
            "/api/prescriptions/",
            {
                "consultation": self.consultation.id,
                "medicines": [
                    {
                        "name": "Paracetamol",
                        "dosage": "500mg",
                    }
                ],
                "instructions": "After food",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_doctor_can_create_prescription(self):
        self.client.force_authenticate(
            user=self.doctor_user
        )

        response = self.client.post(
            "/api/prescriptions/",
            {
                "consultation": self.consultation.id,
                "medicines": [
                    {
                        "name": "Paracetamol",
                        "dosage": "500mg",
                        "frequency": "Twice daily",
                        "duration": "3 days",
                    }
                ],
                "instructions": "Take after food.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)