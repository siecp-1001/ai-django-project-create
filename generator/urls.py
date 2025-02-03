from django.urls import path
from .views import GenerateProjectView 

urlpatterns = [
    path('generate-project/', GenerateProjectView.as_view(), name='generate-project'),
]
