from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('AHMEDcv/mohamed/', include('AHMEDcv\mohamed.urls')),
]
