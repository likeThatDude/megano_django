from decimal import Decimal

import stripe
from django.db.models import Prefetch
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse
from stripe.checkout import Session

from order.models import Order, OrderItem


def get_current_urls_for_payment_response(request: HttpRequest) -> tuple[str, str]:
    success_url = request.build_absolute_uri(reverse("payment:payment_success"))
    cancel_url = request.build_absolute_uri(reverse("payment:payment_cancel"))
    return success_url, cancel_url


def checkout_process(
        order: Order,
        redirect_urls: tuple[str, str],
        all_product: bool = True,
        seller_id: None | int = None,
        total_price: None | Decimal = None) -> Session:
    if all_product:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Order №{order.id}",
                        },
                        "unit_amount": int((order.total_price + order.delivery_price.price) * 100),
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=redirect_urls[0] + f"?order_id={order.id}",
            cancel_url=redirect_urls[1] + f"?order_id={order.id}",
            metadata={
                "all_order": False,
                "order_id": order.id,
            },
        )
    else:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Order #{order.id}",
                        },
                        "unit_amount": int(total_price * 100),
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=redirect_urls[0] + f"?order_id={order.id}",
            cancel_url=redirect_urls[1] + f"?order_id={order.id}",
            metadata={
                "all_order": False,
                "order_id": order.id,
                "seller_id": seller_id,
            },
        )

    return session


def get_order_from_db(order_id: int, all_product: bool = True) -> Order:
    if all_product:
        order = get_object_or_404(Order, pk=order_id)
    else:
        order = get_object_or_404(
            Order.objects
            .select_related(
                'user',
            )
            .prefetch_related(
                Prefetch(
                    'order_items',
                    queryset=OrderItem.objects.select_related('seller', 'product').all()
                )
            )
            ,
            pk=order_id
        )
    return order


def get_order_total_price(order: Order, seller_id: int) -> Decimal:
    total_price = Decimal(0)
    for item in order.order_items.all():
        if item.seller.pk == seller_id:
            total_price += item.price * item.quantity
    return total_price
