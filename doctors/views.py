from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Doctor, AvailabilitySlot
from .serializers import DoctorSerializer, AvailabilitySlotSerializer


class DoctorListView(generics.ListAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Doctor.objects.select_related("user").all()

        specialization = self.request.query_params.get("specialization")
        verified = self.request.query_params.get("verified")
        available = self.request.query_params.get("available")
        min_experience = self.request.query_params.get("min_experience")
        search = self.request.query_params.get("search")

        if specialization:
            queryset = queryset.filter(
                specialization__icontains=specialization
            )

        if verified in ["true", "false"]:
            queryset = queryset.filter(
                is_verified=(verified == "true")
            )

        if available in ["true", "false"]:
            queryset = queryset.filter(
                is_available=(available == "true")
            )

        if min_experience:
            try:
                queryset = queryset.filter(
                    experience_years__gte=int(min_experience)
                )
            except ValueError:
                pass

        if search:
            from django.db.models import Q

            queryset = queryset.filter(
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(specialization__icontains=search)
                | Q(qualification__icontains=search)
            )

        return queryset.order_by(
            "-is_verified",
            "-experience_years"
        )


class DoctorDetailView(generics.RetrieveAPIView):
    queryset = Doctor.objects.select_related("user").all()
    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]


class AvailabilitySlotListCreateView(generics.ListCreateAPIView):
    serializer_class = AvailabilitySlotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = AvailabilitySlot.objects.select_related(
            "doctor",
            "doctor__user",
        )

        doctor_id = self.request.query_params.get("doctor")

        if doctor_id:
            queryset = queryset.filter(
                doctor_id=doctor_id
            )

        return queryset

    def perform_create(self, serializer):
        if self.request.user.role != "DOCTOR":
            raise PermissionDenied(
                "Only doctors can create availability slots."
            )

        doctor = self.request.user.doctor_profile

        serializer.save(doctor=doctor)