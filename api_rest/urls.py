from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, UserViewSet, RegisterView, LoginView

router = DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
<<<<<<< Updated upstream
    path('', views.get_users, name='get_all_users'),
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login),
    path('user/<str:nick>', views.get_by_nick),
    path('cart/<str:nick>/', views.get_cart, name='get_cart'),
    path('cart/<str:nick>/items/', views.add_to_cart, name='add_to_cart'),
    path('cart/<str:nick>/items/<int:item_id>/', views.cart_item_detail, name='cart_item_detail'),
    path('cart/<str:nick>/checkout/', views.checkout_cart, name='checkout_cart'),
    path('orders/<str:nick>/', views.list_orders, name='list_orders'),
    path('', include(router.urls))
=======
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
>>>>>>> Stashed changes
]
