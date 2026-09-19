from django.conf import settings
from django.db import models

from doctors.models import AvailabilitySlot, Doctor


class Consultation(models.Model):

    class Status(models.TextChoices):
        BOOKED = "BOOKED", "Booked"
        CONFIRMED = "CONFIRMED", "Confirmed"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="consultations"
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.PROTECT,
        related_name="consultations"
    )

    slot = models.OneToOneField(
        AvailabilitySlot,
        on_delete=models.PROTECT,
        related_name="consultation"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.BOOKED
    )

    idempotency_key = models.CharField(
        max_length=255,
        unique=True
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.patient.username} - "
            f"{self.doctor} - "
            f"{self.status}"
        )