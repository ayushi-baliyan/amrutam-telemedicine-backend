from rest_framework import serializers

from .models import Consultation


class ConsultationSerializer(serializers.ModelSerializer):

    doctor_name = serializers.CharField(
        source="doctor.user.get_full_name",
        read_only=True
    )

    patient_name = serializers.CharField(
        source="patient.get_full_name",
        read_only=True
    )

    slot_start = serializers.DateTimeField(
        source="slot.start_time",
        read_only=True
    )

    slot_end = serializers.DateTimeField(
        source="slot.end_time",
        read_only=True
    )

    class Meta:
        model = Consultation

        fields = [
            "id",
            "patient",
            "patient_name",
            "doctor",
            "doctor_name",
            "slot",
            "slot_start",
            "slot_end",
            "status",
            "idempotency_key",
            "notes",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "patient",
            "patient_name",
            "doctor",
            "doctor_name",
            "slot_start",
            "slot_end",
            "status",
            "created_at",
        ]