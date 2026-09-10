# pyrefly: ignore [missing-import]
from django.contrib import admin
# pyrefly: ignore [missing-import]
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Essa linha é a ponte que liga o projeto às nossas telas de Login e Dashboard
    path('', include('core.urls')),
]