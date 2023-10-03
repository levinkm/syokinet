from django.urls import path, include
from .views import UserRegistrationView
from rest_framework.routers import DefaultRouter


urlpatterns = [
    path("register", UserRegistrationView.as_view(), name="user-registration"),
]
