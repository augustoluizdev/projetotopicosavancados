from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import EventViewSet

from . import views

router = DefaultRouter()
router.register(r'events', EventViewSet)

urlpatterns = [
    path('', views.get_users, name='get_all_users'),
    path('auth/register/', views.register),
    path('auth/login/', views.login),
    path('user/<str:nick>', views.get_by_nick),
    path('data/', views.user_manager),
    path('', include(router.urls))
]
