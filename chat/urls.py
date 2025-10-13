from django.urls import path
from . import views

urlpatterns = [
    path('ping/', views.ping_endpoint, name='ping_endpoint'),
    path('test/', views.test_endpoint, name='test_endpoint'),
    path('health/', views.health_check, name='health_check'),
    path('chat/', views.chat, name='chat'),
    path('session/<uuid:session_id>/history/', views.session_history, name='session_history'),
    path('leads/', views.leads_list, name='leads_list'),
    path('', views.frontend_view, name='frontend'),
]




