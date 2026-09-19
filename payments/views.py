from django.db import IntegrityError, transaction

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter

from audit_logs.utils import create_audit_log
from consultations.models import Consultation

from .models import Payment
from .serializers import PaymentSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="Idempotency-Key",
            type=str,
            location=OpenApiParameter.HEADER,
            required=True,
            description="Unique key used to make payment creation idempotent.",
        )
    ]
)
class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if request.user.role != "PATIENT":
            return Response(
                {"detail": "Only patients can create payments."},
                status=status.HTTP_403_FORBIDDEN,
            )

        idempotency_key = request.headers.get("Idempotency-Key")

        if not idempotency_key:
            return Response(
                {"detail": "Idempotency-Key header is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        consultation_id = request.data.get("consultation")

        if not consultation_id:
            return Response(
                {"detail": "consultation is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_payment = Payment.objects.filter(
            idempotency_key=idempotency_key
        ).first()

        if existing_payment:
            if existing_payment.patient_id != request.user.id:
                return Response(
                    {"detail": "Idempotency key belongs to another patient."},
                    status=status.HTTP_409_CONFLICT,
                )

            return Response(
                PaymentSerializer(existing_payment).data,
                status=status.HTTP_200_OK,
            )

        try:
            with transaction.atomic():
                consultation = (
                    Consultation.objects
                    .select_for_update()
                    .select_related("doctor")
                    .get(
                        id=consultation_id,
                        patient=request.user,
                    )
                )

                if consultation.status == Consultation.Status.CANCELLED:
                    return Response(
                        {
                            "detail": (
                                "Payment cannot be created for a "
                                "cancelled consultation."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if Payment.objects.filter(
                    consultation=consultation
                ).exists():
                    return Response(
                        {
                            "detail": (
                                "Payment already exists for this consultation."
                            )
                        },
                        status=status.HTTP_409_CONFLICT,
                    )

                amount = consultation.doctor.consultation_fee

                if amount <= 0:
                    return Response(
                        {
                            "detail": (
                                "Doctor consultation fee must be "
                                "greater than zero."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                payment = Payment.objects.create(
                    patient=request.user,
                    consultation=consultation,
                    amount=amount,
                    currency="INR",
                    method=request.data.get("method", "UPI"),
                    status=Payment.Status.PENDING,
                    idempotency_key=idempotency_key,
                )

                create_audit_log(
                    actor=request.user,
                    action="PAYMENT_CREATED",
                    resource_type="Payment",
                    resource_id=payment.id,
                    request=request,
                    metadata={
                        "consultation_id": consultation.id,
                        "amount": str(amount),
                        "currency": "INR",
                    },
                )

        except Consultation.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Consultation not found or does not belong to you."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except IntegrityError:
            payment = Payment.objects.filter(
                idempotency_key=idempotency_key
            ).first()

            if payment:
                if payment.patient_id != request.user.id:
                    return Response(
                        {
                            "detail": (
                                "Idempotency key belongs to another patient."
                            )
                        },
                        status=status.HTTP_409_CONFLICT,
                    )

                return Response(
                    PaymentSerializer(payment).data,
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"detail": "Payment could not be created."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )


class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return Payment.objects.all()

        return Payment.objects.filter(
            patient=user
        ) | Payment.objects.filter(
            consultation__doctor__user=user
        )