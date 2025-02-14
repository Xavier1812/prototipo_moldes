from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Panel de administración de Django
    path('', include('moldes.urls')),  # Incluir las URLs de tu aplicación
]