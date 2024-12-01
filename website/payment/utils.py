from datetime import datetime
from decimal import Decimal
from itertools import product

import stripe
from django.db import transaction
from django.db.models import Prefetch
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse
from order.models import Order
from order.models import OrderItem
from rest_framework.reverse import reverse_lazy
from stripe.checkout import Session

"""
Функции для работы с оплатой заказов через Stripe.

Содержит утилиты для создания сессий оплаты, получения данных о заказах,
изменения статусов оплаты и обработки событий Stripe.

Функции:
- get_current_urls_for_payment_response: Генерация URL-адресов для успешной и отмененной оплаты.
- checkout_process: Создание Stripe Checkout сессии для всех товаров или товаров конкретного продавца.
- get_order_from_db: Получение объекта заказа из базы данных.
- get_order_total_price: Расчет общей стоимости товаров для конкретного продавца.
- change_order_payment_status: Обновление статуса оплаты всего заказа.
- change_certain_items_payment_status: Обновление статуса оплаты определенных товаров в заказе.
- create_recipes_url_for_db: Генерация URL чека, для сохранения в базе данных после оплаты.
- get_paid_order: Проверка оплаченного заказа и получение его данных для текущего пользователя.
"""


def get_current_urls_for_payment_response(request: HttpRequest) -> tuple[str, str]:
    """
    Генерирует абсолютные URL-адреса для успешной и отмененной оплаты.

    Параметры:
        - request (HttpRequest): Текущий HTTP-запрос.

    Возвращает:
        - tuple[str, str]: Кортеж из двух URL:
            - success_url: URL для успешной оплаты.
            - cancel_url: URL для отмененной оплаты.
    """
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
    """
    Создает Stripe Checkout сессию для оплаты заказа.

    Параметры:
        - order (Order): Объект заказа.
        - redirect_urls (tuple[str, str]): URL-адреса для успешной и отмененной оплаты.
        - all_product (bool): Если True, оплачиваются все товары в заказе. По умолчанию True.
        - seller_id (int | None): ID продавца для оплаты конкретных товаров. По умолчанию None.
        - total_price (Decimal | None): Сумма для оплаты, если оплачиваются товары конкретного продавца. По умолчанию None.

    Возвращает:
        - Session: Объект Stripe Checkout Session.
    """
    products_ids = list()
    print(f'{order=}')
    for i in order.order_items.all():
        print(f'{i=}')
        products_ids.append(i.product_id)
    print(f'{products_ids=}')
    products_ids = ','.join((str(num) for num in products_ids))
    print(f'{products_ids=}')
    now = datetime.now()
    formatted_date = now.strftime("%H:%M %d.%m.%Y")
    date_to_db = "%20".join(formatted_date.split(" "))
    if all_product:
        total_price_all = int((order.total_price + order.delivery_price.price) * 100)
        url_total_price = order.total_price + order.delivery_price.price

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Order №{order.id}",
                        },
                        "unit_amount": total_price_all,
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=redirect_urls[0] + f"?order_id={order.id}&total_price={url_total_price}"
            f"&date={formatted_date}&delivery_price={order.delivery_price.price}",
            cancel_url=redirect_urls[1] + f"?order_id={order.id}",
            metadata={
                "all_order": 1,
                "order_id": order.id,
                "total_price": url_total_price,
                "date": formatted_date,
                "url": f"?order_id={order.id}&total_price={url_total_price}&date={date_to_db}"
                       f"&delivery_price={order.delivery_price.price}",
                "delivery_price": order.delivery_price.price,
                "products_ids": products_ids,
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
            success_url=redirect_urls[0] + f"?order_id={order.id}&seller_id={seller_id}"
            f"&total_price={total_price}&date={formatted_date}",
            cancel_url=redirect_urls[1] + f"?order_id={order.id}&seller_id={seller_id}",
            metadata={
                "all_order": 0,
                "order_id": order.id,
                "seller_id": seller_id,
                "total_price": total_price,
                "date": formatted_date,
                "url": f"?order_id={order.id}&seller_id={seller_id}" f"&total_price={total_price}&date={date_to_db}",
                "products_ids": products_ids,
            },
        )

    return session


def get_order_from_db(order_id: int, all_product: bool = True) -> Order:
    """
    Получает объект заказа из базы данных.

    Параметры:
        - order_id (int): ID заказа.
        - all_product (bool): Если True, возвращает заказ с минимальными связями. Иначе загружает связанные данные. По умолчанию True.

    Возвращает:
        - Order: Объект заказа.
    """
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
    """
    Рассчитывает общую стоимость товаров для конкретного продавца.

    Параметры:
        - order (Order): Объект заказа.
        - seller_id (int): ID продавца.

    Возвращает:
        - Decimal: Общая стоимость товаров продавца в заказе.
    """
    total_price = Decimal(0)
    for item in order.order_items.all():
        if item.seller.pk == seller_id:
            total_price += item.price * item.quantity
    return total_price


def change_order_payment_status(session: Session) -> None:
    """
    Обновляет статус оплаты всего заказа.

    Параметры:
        - session (Session): Объект Stripe Session с информацией об оплате.

    Действия:
        - Устанавливает статус заказа как "оплачен".
        - Обновляет статус всех товаров в заказе.
    """
    if session["payment_status"] == "paid":
        order_id = session["metadata"]["order_id"]
        current_receipt_url = create_recipes_url_for_db(session)

        order = (
            Order.objects.prefetch_related(
                Prefetch(
                    "order_items",
                    queryset=OrderItem.objects.select_related("order").only(
                        "payment_status",
                        "order__id",
                        "receipt_url",
                    ),
                )
            )
            .only("order_items", "paid_status", "status")
            .get(pk=order_id)
        )
        with transaction.atomic():
            order.paid_status = Order.PAID
            order.status = Order.PROCESSING
            order.save()
            order.order_items.update(payment_status=True, receipt_url=current_receipt_url)


def change_certain_items_payment_status(session: Session) -> None:
    """
    Обновляет статус оплаты определенных товаров в заказе.

    Параметры:
        - session (Session): Объект Stripe Session с информацией об оплате.

    Действия:
        - Устанавливает статус оплаты для товаров конкретного продавца.
        - Проверяет статус всех товаров в заказе и обновляет общий статус заказа.
    """
    if session["payment_status"] == "paid":
        order_id = session["metadata"]["order_id"]
        seller_id = session["metadata"]["seller_id"]
        current_receipt_url = create_recipes_url_for_db(session)

        order = (
            Order.objects.prefetch_related(
                Prefetch(
                    "order_items",
                    queryset=OrderItem.objects.select_related("order").only(
                        "payment_status",
                        "order__id",
                        "receipt_url",
                    ),
                )
            )
            .only("order_items", "paid_status", "status")
            .get(pk=order_id)
        )

        with transaction.atomic():
            order.order_items.filter(seller_id=seller_id).update(payment_status=True, receipt_url=current_receipt_url)
            updated_order_items = (
                OrderItem.objects.select_related("seller", "order", "product")
                .filter(order_id=order_id)
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


def create_recipes_url_for_db(session: Session) -> str:
    """
    Генерирует URL чека, для сохранения в базе данных после успешной оплаты.

    Параметры:
        - session (Session): Объект Stripe Session с метаданными об оплате.

    Возвращает:
        - str: Сформированный URL.
    """
    current_receipt_url = session["metadata"]["url"]
    correct_payment_success_url = reverse("payment:payment_success")
    ready_url = correct_payment_success_url + current_receipt_url
    return ready_url


def get_paid_order(order_id: int, user_id: int, seller_id: int | None = None) -> Order | bool:
    """
    Получает оплаченный заказ текущего пользователя.
    Под запрос получения данных зависит от seller_id.

    Параметры:
        - order_id (int): ID заказа.
        - user_id (int): ID текущего пользователя.
        - seller_id (int | None): ID продавца (опционально).

    Возвращает:
        - Order | bool: Объект заказа, если пользователь имеет доступ, иначе False.
    """
    if seller_id is None:
        queryset = OrderItem.objects.select_related("order").only("payment_status", "order__id")
    else:
        queryset = (
            OrderItem.objects.select_related("order", "seller", "product")
            .filter(seller_id=seller_id)
            .only("order__id", "seller__name", "product__name", "price", "quantity")
        )

    order = (
        Order.objects.select_related("user")
        .prefetch_related(
            Prefetch(
                "order_items",
                queryset=queryset,
            )
        )
        .only("order_items", "paid_status", "status", "user__id")
        .get(pk=order_id)
    )
    if user_id == order.user.pk:
        return order

    return False
