from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass

from .models import Order


@dataclass(frozen=True)
class OrderItemCreatedEvent:
    event_id: int
    title: str
    quantity: int


@dataclass(frozen=True)
class OrderCreatedEvent:
    event_id: str
    order_id: int
    user_nickname: str
    user_email: str
    created_at: str
    items: list[OrderItemCreatedEvent]

    def to_payload(self) -> dict:
        return asdict(self)


def build_order_created_event(order: Order) -> OrderCreatedEvent:
    items = [
        OrderItemCreatedEvent(
            event_id=item.event_id,
            title=item.event.title,
            quantity=item.quantity,
        )
        for item in order.items.select_related('event').all()
    ]

    return OrderCreatedEvent(
        event_id=str(uuid.uuid4()),
        order_id=order.pk,
        user_nickname=order.user.user_nickname,
        user_email=order.user.user_email,
        created_at=order.created_at.isoformat(),
        items=items,
    )
