from django.db.models import Count

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from consultations.models import Consultation
from doctors.models import Doctor
from payments.models import Payment

from .models import User
from .serializers import UserSerializer
from drf_spectacular.utils import extend_schema


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema(
    responses={200: dict},
    description="Returns admin-only platform analytics."
)
class AdminAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != User.Role.ADMIN:
            return Response(
                {"detail": "Only admins can access analytics."},
                status=status.HTTP_403_FORBIDDEN,
            )

        consultation_counts = Consultation.objects.values(
            "status"
        ).annotate(
            count=Count("id")
        )

        payment_counts = Payment.objects.values(
            "status"
        ).annotate(
            count=Count("id")
        )

        return Response(
            {
                "users": {
                    "total": User.objects.count(),
                    "patients": User.objects.filter(
                        role=User.Role.PATIENT
                    ).count(),
                    "doctors": User.objects.filter(
                        role=User.Role.DOCTOR
                    ).count(),
                    "admins": User.objects.filter(
                        role=User.Role.ADMIN
                    ).count(),
                },
                "doctors": {
                    "total": Doctor.objects.count(),
                    "verified": Doctor.objects.filter(
                        is_verified=True
                    ).count(),
                    "available": Doctor.objects.filter(
                        is_available=True
                    ).count(),
                },
                "consultations": {
                    "total": Consultation.objects.count(),
                    "by_status": {
                        item["status"]: item["count"]
                        for item in consultation_counts
                    },
                },
                "payments": {
                    "total": Payment.objects.count(),
                    "by_status": {
                        item["status"]: item["count"]
                        for item in payment_counts
                    },
                },
            }
        )