# pyrefly: ignore [missing-import]
from django.urls import path
from . import views
from .views import LogAPIView, setup_2fa_view # Importação atualizada

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('setup-2fa/', setup_2fa_view, name='setup-2fa'), # Nova rota do QR Code
    path('api/logs/', LogAPIView.as_view(), name='api-logs'),
    path('dependente/novo/', views.register_dependent, name='register_dependent'),
    path('dependente/excluir/<int:id>/', views.delete_dependent, name='delete_dependent'),
    path('registrar/', views.register_user, name='registro'), # Nova URL de Registro
]