from rest_framework import serializers
from .models import Prescription


class PrescriptionSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(
        source="consultation.doctor.user.get_full_name",
        read_only=True
    )

    patient_name = serializers.CharField(
        source="consultation.patient.get_full_name",
        read_only=True
    )

    consultation_status = serializers.CharField(
        source="consultation.status",
        read_only=True
    )

    class Meta:
        model = Prescription
        fields = [
            "id",
            "consultation",
            "doctor_name",
            "patient_name",
            "consultation_status",
            "medicines",
            "instructions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "doctor_name",
            "patient_name",
            "consultation_status",
            "created_at",
            "updated_at",
        ]

    def validate_medicines(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Medicines must be a list."
            )

        for medicine in value:
            if not isinstance(medicine, dict):
                raise serializers.ValidationError(
                    "Each medicine must be an object."
                )

            if not medicine.get("name"):
                raise serializers.ValidationError(
                    "Each medicine must have a name."
                )

        return value