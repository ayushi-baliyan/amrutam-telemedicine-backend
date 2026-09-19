from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from users.models import User
from .models import Doctor, AvailabilitySlot


class DoctorAPITest(APITestCase):

    def setUp(self):
        self.patient = User.objects.create_user(
            username="testpatient",
            password="Patient@12345",
            role="PATIENT",
            email="patient@test.com",
        )

        self.doctor_user = User.objects.create_user(
            username="testdoctor",
            password="Doctor@12345",
            role="DOCTOR",
            email="doctor@test.com",
        )

        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialization="Cardiology",
            qualification="MBBS",
            experience_years=5,
            registration_number="TEST-001",
            consultation_fee=500,
        )

    def test_doctor_list(self):
        response = self.client.get(
            "/api/doctors/"
        )

        self.assertEqual(response.status_code, 200)

    def test_doctor_search(self):
        response = self.client.get(
            "/api/doctors/?search=Cardiology"
        )

        self.assertEqual(response.status_code, 200)

    def test_patient_cannot_create_slot(self):
        self.client.force_authenticate(
            user=self.patient
        )

        response = self.client.post(
            "/api/doctors/availability/",
            {
                "start_time": "2026-10-01T10:00:00Z",
                "end_time": "2026-10-01T10:30:00Z",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)