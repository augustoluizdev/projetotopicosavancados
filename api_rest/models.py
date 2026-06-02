from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class User(models.Model):
    # Usuario simples da API. O nickname funciona como identificador principal.
    user_nickname = models.CharField(max_length=100, primary_key=True)
    user_name = models.CharField(max_length=150, blank=True)
    user_email = models.EmailField(blank=True, unique=True)
    user_age = models.PositiveIntegerField(default=0)
    password = models.CharField(max_length=128)

    def set_password(self, raw_password):
        # Nunca salvamos a senha pura; o Django gera um hash seguro.
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        # Compara a senha recebida com o hash salvo no banco.
        return check_password(raw_password, self.password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return True

    def __str__(self):
        return f'Nickname: {self.user_nickname} - Name: {self.user_name} - Email: {self.user_email} - Age: {self.user_age}'


class Event(models.Model):
    # Evento que pode receber reservas de ingressos via carrinho.
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

    class NotificationStatus(models.TextChoices):
        REQUESTED = 'requested', 'Requested'
        NOTIFICATION_SENT = 'notification_sent', 'Notification sent'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    status_notificacao = models.CharField(
        max_length=30,
        choices=NotificationStatus.choices,
        default=NotificationStatus.REQUESTED,
    )
    data_processamento = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Pedido #{self.pk} - {self.user.user_nickname}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.quantity}x {self.event.title}'


class ProcessedEvent(models.Model):
    event_id = models.CharField(max_length=64, unique=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='processed_event')
    processed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-processed_at']

    def __str__(self):
        return f'Evento {self.event_id} processado para pedido #{self.order_id}'
