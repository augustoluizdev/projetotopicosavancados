from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    user_nickname = models.CharField(max_length=100, primary_key=True)
    user_name = models.CharField(max_length=150, blank=True)
    user_email = models.EmailField(unique=True)
    user_age = models.PositiveIntegerField(default=0)
    password = models.CharField(max_length=128)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f'Nickname: {self.user_nickname} - Name: {self.user_name} - Email: {self.user_email} - Age: {self.user_age}'

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    max_participants = models.PositiveIntegerField()

    def __str__(self):
        return self.title

    @property
    def sold_tickets(self):
        sold = (
            self.order_items.filter(order__status=Order.Status.REQUESTED)
            .aggregate(total=models.Sum('quantity'))
            .get('total')
        )
        return sold or 0

    @property
    def available_tickets(self):
        return self.max_participants - self.sold_tickets


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Carrinho de {self.user.user_nickname}'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'event')

    def __str__(self):
        return f'{self.quantity}x {self.event.title}'


class Order(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'requested', 'Requested'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Pedido #{self.pk} - {self.user.user_nickname}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.quantity}x {self.event.title}'
