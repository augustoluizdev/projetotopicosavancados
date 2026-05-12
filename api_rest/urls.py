from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views


# O router cria automaticamente as rotas REST de usuarios e eventos.
router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename='event')
router.register(r'users', views.UserViewSet, basename='users')


urlpatterns = [
    # Rotas de autenticacao usadas pelo cadastro e login.
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),

    # Rotas mantidas por compatibilidade com chamadas antigas do projeto.
    path('', views.get_users, name='get_all_users'),
    path('user/<str:nick>/', views.get_by_nick, name='get_by_nick'),

    # Rotas do fluxo de carrinho, checkout e pedidos.
    path('cart/<str:nick>/', views.get_cart, name='get_cart'),
    path('cart/<str:nick>/items/', views.add_to_cart, name='add_to_cart'),
    path('cart/<str:nick>/items/<int:item_id>/', views.cart_item_detail, name='cart_item_detail'),
    path('cart/<str:nick>/checkout/', views.checkout_cart, name='checkout_cart'),
    path('orders/<int:order_id>/status/', views.order_status, name='order_status'),
    path('orders/<str:nick>/', views.list_orders, name='list_orders'),

    # Rotas REST principais: /users/, /events/ e seus detalhes.
    path('', include(router.urls)),
]
