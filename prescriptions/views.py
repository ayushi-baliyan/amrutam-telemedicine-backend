from django.db import IntegrityError

from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from consultations.models import Consultation
from audit_logs.utils import create_audit_log

from .models import Prescription
from .serializers import PrescriptionSerializer


class PrescriptionCreateView(generics.CreateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        consultation_id = request.data.get("consultation")

        if not consultation_id:
            return Response(
                {"detail": "consultation is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.role != "DOCTOR":
            raise PermissionDenied(
                "Only doctors can create prescriptions."
            )

        consultation = get_object_or_404(
            Consultation.objects.select_related(
                "doctor",
                "doctor__user",
                "patient",
            ),
            id=consultation_id,
        )

        if consultation.doctor.user_id != request.user.id:
            raise PermissionDenied(
                "You can only prescribe for your own consultations."
            )

        if hasattr(consultation, "prescription"):
            return Response(
                {
                    "detail": (
                        "A prescription already exists "
                        "for this consultation."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            prescription = serializer.save(
                consultation=consultation
            )
        except IntegrityError:
            return Response(
                {
                    "detail": (
                        "A prescription already exists "
                        "for this consultation."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        create_audit_log(
            actor=request.user,
            action="PRESCRIPTION_CREATED",
            resource_type="PRESCRIPTION",
            resource_id=prescription.id,
            request=request,
            metadata={
                "consultation_id": consultation.id,
                "patient_id": consultation.patient_id,
                "doctor_id": consultation.doctor_id,
            },
        )

        return Response(
            PrescriptionSerializer(prescription).data,
            status=status.HTTP_201_CREATED,
        )


class PrescriptionDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Prescription.objects.select_related(
            "consultation",
            "consultation__doctor",
            "consultation__doctor__user",
            "consultation__patient",
        )

    def get_object(self):
        prescription = super().get_object()

        user = self.request.user

        if user.role == "DOCTOR":
            if prescription.consultation.doctor.user_id != user.id:
                raise PermissionDenied(
                    "You can only access your own prescriptions."
                )

        elif user.role == "PATIENT":
            if prescription.consultation.patient_id != user.id:
                raise PermissionDenied(
                    "You can only access your own prescriptions."
                )

        else:
            raise PermissionDenied(
                "You do not have permission to access this prescription."
            )

        return prescription

    def perform_update(self, serializer):
        if self.request.user.role != "DOCTOR":
            raise PermissionDenied(
                "Only doctors can update prescriptions."
            )

        prescription = serializer.save()

        create_audit_log(
            actor=self.request.user,
            action="PRESCRIPTION_UPDATED",
            resource_type="PRESCRIPTION",
            resource_id=prescription.id,
            request=self.request,
            metadata={
                "consultation_id": prescription.consultation_id,
            },
        )