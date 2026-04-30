from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, UserViewSet, RegisterView, LoginView

router = DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
<<<<<<< Updated upstream
    path('', views.get_users, name='get_all_users'),
    path('auth/register/', views.register),
    path('auth/login/', views.login),
    path('user/<str:nick>', views.get_by_nick),
    path('data/', views.user_manager),
    path('', include(router.urls))
=======
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
>>>>>>> Stashed changes
]
