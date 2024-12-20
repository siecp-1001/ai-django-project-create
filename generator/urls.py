from django.urls import path
from .views import generate_project

urlpatterns = [
    path("generate/", generate_project, name="generate_project"),
]
