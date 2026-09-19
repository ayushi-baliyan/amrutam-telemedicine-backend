from django.db import IntegrityError, transaction

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from doctors.models import AvailabilitySlot
from audit_logs.utils import create_audit_log

from .models import Consultation
from .serializers import ConsultationSerializer


class ConsultationListView(generics.ListAPIView):
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "DOCTOR":
            return Consultation.objects.select_related(
                "patient",
                "doctor",
                "doctor__user",
                "slot",
            ).filter(doctor__user=user)

        return Consultation.objects.select_related(
            "patient",
            "doctor",
            "doctor__user",
            "slot",
        ).filter(patient=user)


class ConsultationCreateView(generics.CreateAPIView):
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        slot_id = request.data.get("slot")
        idempotency_key = request.headers.get("Idempotency-Key")

        if not slot_id:
            return Response(
                {"detail": "slot is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not idempotency_key:
            return Response(
                {"detail": "Idempotency-Key header is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing = Consultation.objects.filter(
            idempotency_key=idempotency_key
        ).first()

        if existing:
            if existing.patient_id != request.user.id:
                return Response(
                    {
                        "detail": (
                            "Idempotency-Key is already used "
                            "by another user."
                        )
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            return Response(
                ConsultationSerializer(existing).data,
                status=status.HTTP_200_OK,
            )

        try:
            with transaction.atomic():
                slot = (
                    AvailabilitySlot.objects
                    .select_for_update()
                    .select_related("doctor", "doctor__user")
                    .get(id=slot_id)
                )

                if slot.status != AvailabilitySlot.Status.AVAILABLE:
                    return Response(
                        {"detail": "This slot is not available."},
                        status=status.HTTP_409_CONFLICT,
                    )

                if not slot.doctor.is_available:
                    return Response(
                        {"detail": "Doctor is currently unavailable."},
                        status=status.HTTP_409_CONFLICT,
                    )

                try:
                    with transaction.atomic():
                        consultation = Consultation.objects.create(
                            patient=request.user,
                            doctor=slot.doctor,
                            slot=slot,
                            idempotency_key=idempotency_key,
                            notes=request.data.get("notes", ""),
                            status=Consultation.Status.BOOKED,
                        )

                except IntegrityError:
                    existing = Consultation.objects.filter(
                        idempotency_key=idempotency_key
                    ).first()

                    if existing:
                        if existing.patient_id != request.user.id:
                            return Response(
                                {
                                    "detail": (
                                        "Idempotency-Key is already "
                                        "used by another user."
                                    )
                                },
                                status=status.HTTP_409_CONFLICT,
                            )

                        return Response(
                            ConsultationSerializer(existing).data,
                            status=status.HTTP_200_OK,
                        )

                    return Response(
                        {"detail": "Booking conflict. Please retry."},
                        status=status.HTTP_409_CONFLICT,
                    )

                slot.status = AvailabilitySlot.Status.BOOKED
                slot.save(
                    update_fields=["status", "updated_at"]
                )

                create_audit_log(
                    actor=request.user,
                    action="CONSULTATION_BOOKED",
                    resource_type="CONSULTATION",
                    resource_id=consultation.id,
                    request=request,
                    metadata={
                        "doctor_id": consultation.doctor_id,
                        "slot_id": consultation.slot_id,
                    },
                )

        except AvailabilitySlot.DoesNotExist:
            return Response(
                {"detail": "Availability slot not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            ConsultationSerializer(consultation).data,
            status=status.HTTP_201_CREATED,
        )


class ConsultationDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "DOCTOR":
            return Consultation.objects.select_related(
                "patient",
                "doctor",
                "doctor__user",
                "slot",
            ).filter(doctor__user=user)

        return Consultation.objects.select_related(
            "patient",
            "doctor",
            "doctor__user",
            "slot",
        ).filter(patient=user)

    def perform_update(self, serializer):
        consultation = self.get_object()

        if self.request.user.role == "PATIENT":
            allowed_fields = {"notes"}
            submitted_fields = set(self.request.data.keys())

            if not submitted_fields.issubset(allowed_fields):
                raise PermissionDenied(
                    "Patients can only update consultation notes."
                )

        if self.request.user.role not in ["PATIENT", "DOCTOR"]:
            raise PermissionDenied(
                "You do not have permission to update this consultation."
            )

        serializer.save()


class ConsultationStatusUpdateView(generics.UpdateAPIView):
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Consultation.objects.select_related(
            "patient",
            "doctor",
            "doctor__user",
            "slot",
        )

    def update(self, request, *args, **kwargs):
        consultation = self.get_object()

        if request.user.role != "DOCTOR":
            raise PermissionDenied(
                "Only doctors can update consultation status."
            )

        if consultation.doctor.user_id != request.user.id:
            raise PermissionDenied(
                "You can only update your own consultations."
            )

        new_status = request.data.get("status")

        allowed_statuses = {
            Consultation.Status.CONFIRMED,
            Consultation.Status.COMPLETED,
            Consultation.Status.CANCELLED,
        }

        if new_status not in allowed_statuses:
            return Response(
                {
                    "detail": (
                        "Invalid status. Allowed values: "
                        "CONFIRMED, COMPLETED, CANCELLED."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        consultation.status = new_status
        consultation.save(
            update_fields=["status", "updated_at"]
        )

        create_audit_log(
            actor=request.user,
            action="CONSULTATION_STATUS_UPDATED",
            resource_type="CONSULTATION",
            resource_id=consultation.id,
            request=request,
            metadata={
                "new_status": new_status,
            },
        )

        return Response(
            ConsultationSerializer(consultation).data,
            status=status.HTTP_200_OK,
        )