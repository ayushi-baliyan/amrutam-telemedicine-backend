from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "patient",
            "consultation",
            "amount",
            "currency",
            "method",
            "status",
            "transaction_id",
            "idempotency_key",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "patient",
            "status",
            "transaction_id",
            "created_at",
            "updated_at",
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Payment amount must be greater than zero."
            )
        return value

    def validate_currency(self, value):
        return value.upper()