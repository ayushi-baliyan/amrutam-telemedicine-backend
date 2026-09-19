from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import CurrentUserView, AdminAnalyticsView


urlpatterns = [
    path("me/", CurrentUserView.as_view(), name="current-user"),
    path("token/", TokenObtainPairView.as_view(), name="token-obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("admin/analytics/", AdminAnalyticsView.as_view(), name="admin-analytics"),
]