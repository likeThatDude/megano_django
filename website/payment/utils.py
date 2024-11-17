from decimal import Decimal

import stripe
from django.db import transaction
from django.db.models import Prefetch
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse
from order.models import Order
from order.models import OrderItem
from stripe.checkout import Session


def get_current_urls_for_payment_response(request: HttpRequest) -> tuple[str, str]:
    success_url = request.build_absolute_uri(reverse("payment:payment_success"))
    cancel_url = request.build_absolute_uri(reverse("payment:payment_cancel"))
    return success_url, cancel_url


def checkout_process(
    order: Order,
    redirect_urls: tuple[str, str],
    all_product: bool = True,
    seller_id: None | int = None,
    total_price: None | Decimal = None,
) -> Session:
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
                "all_order": 1,
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
                            "name": f"Order №{order.id}",
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
                "all_order": 0,
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
            Order.objects.select_related(
                "user",
            ).prefetch_related(
                Prefetch("order_items", queryset=OrderItem.objects.select_related("seller", "product").all())
            ),
            pk=order_id,
        )
    return order


def get_order_total_price(order: Order, seller_id: int) -> Decimal:
    total_price = Decimal(0)
    for item in order.order_items.all():
        if item.seller.pk == seller_id:
            total_price += item.price * item.quantity
    return total_price


def change_order_payment_status(session: Session) -> None:
    if session["payment_status"] == "paid":
        order_id = session["metadata"]["order_id"]
        order = (
            Order.objects.prefetch_related(
                Prefetch(
                    "order_items",
                    queryset=OrderItem.objects.select_related("order").only("payment_status", "order__id"),
                )
            )
            .only("order_items", "paid_status", "status")
            .get(pk=order_id)
        )
        with transaction.atomic():
            order.paid_status = Order.PAID
            order.status = Order.PROCESSING
            order.save()
            order.order_items.update(payment_status=True)


def change_certain_items_payment_status(session: Session) -> None:
    if session["payment_status"] == "paid":
        order_id = session["metadata"]["order_id"]
        seller_id = session["metadata"]["seller_id"]
        order = (
            Order.objects.prefetch_related(
                Prefetch(
                    "order_items",
                    queryset=OrderItem.objects.select_related("order").only("payment_status", "order__id"),
                )
            )
            .only("order_items", "paid_status", "status")
            .get(pk=order_id)
        )

        with transaction.atomic():
            order.order_items.filter(seller_id=seller_id, payment_status=False).update(payment_status=True)
            updated_order_items = (
                OrderItem.objects.select_related("seller", "order", "product")
                .filter(order__id=41)
                .only(
                    "seller__id",
                    "order__id",
                    "payment_status",
                    "quantity",
                    "price",
                    "product__id",
                    "product__name",
                    "seller__name",
                )
            )
            current_payment_status = all([i.payment_status for i in updated_order_items])
            order.paid_status = Order.PAID if current_payment_status else Order.PARTLY_PAID
            order.status = Order.PROCESSING
            order.save()
