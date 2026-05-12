from django.contrib import admin

from .models import Cart, CartItem, Event, Order, OrderItem, ProcessedEvent, User


# Registro dos modelos para facilitar consulta e manutencao pelo painel admin.
admin.site.register(User)
admin.site.register(Event)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ProcessedEvent)
