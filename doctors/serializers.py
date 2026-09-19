from rest_framework import serializers
from .models import Doctor, AvailabilitySlot


class DoctorSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source="user.get_full_name",
        read_only=True
    )

    class Meta:
        model = Doctor
        fields = [
            "id",
            "user",
            "user_name",
            "specialization",
            "qualification",
            "experience_years",
            "registration_number",
            "consultation_fee",
            "bio",
            "is_verified",
            "is_available",
        ]
        read_only_fields = ["id"]


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilitySlot
        fields = [
            "id",
            "doctor",
            "start_time",
            "end_time",
            "status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "doctor",
            "status",
            "created_at",
        ]

    def validate(self, data):
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError(
                "End time must be after start time."
            )
        return data