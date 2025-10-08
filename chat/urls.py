from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('session/<uuid:session_id>/history/', views.session_history, name='session_history'),
    path('leads/', views.leads_list, name='leads_list'),
    path('', views.frontend_view, name='frontend'),
]
