from django.conf import settings
from django.db import models
from consultations.models import Consultation


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    class Method(models.TextChoices):
        UPI = "UPI", "UPI"
        CARD = "CARD", "Card"
        NET_BANKING = "NET_BANKING", "Net Banking"
        WALLET = "WALLET", "Wallet"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payments",
    )
    consultation = models.OneToOneField(
        Consultation,
        on_delete=models.PROTECT,
        related_name="payment",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    currency = models.CharField(
        max_length=3,
        default="INR",
    )
    method = models.CharField(
        max_length=20,
        choices=Method.choices,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    transaction_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )
    idempotency_key = models.CharField(
        max_length=255,
        unique=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment {self.id} - {self.status}"