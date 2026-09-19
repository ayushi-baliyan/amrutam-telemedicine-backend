from django.db import models
from consultations.models import Consultation


class Prescription(models.Model):
    consultation = models.OneToOneField(
        Consultation,
        on_delete=models.CASCADE,
        related_name="prescription",
    )
    medicines = models.JSONField(default=list)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prescription for Consultation #{self.consultation.id}"