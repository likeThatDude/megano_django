from account.models import CustomUser
from catalog.models import Delivery
from catalog.models import Payment
from catalog.models import Price
from django.db import transaction
from django.db.models import Q
from django.db.models import QuerySet
from django.http import HttpRequest
from order.models import Order
from order.models import OrderItem
from rest_framework.exceptions import ValidationError


def get_full_username(user: CustomUser) -> str:
    user_name_data = (user.profile.first_name, user.profile.last_name, user.profile.patronymic)
    full_name = " ".join(data for data in user_name_data if data is not None)
    return full_name


def get_user_data(request: HttpRequest) -> dict[str, str]:
    user = CustomUser.objects.select_related("profile").get(pk=request.user.id)
    full_user_name = get_full_username(user)
    correct_user_data = {
        "name": full_user_name,
        "phone": user.profile.phone,
        "email": user.email,
    }
    return correct_user_data


def get_ids_list(products_list: dict) -> list[tuple[int, int]]:
    product_seller_ids = []
    for key, value in products_list.items():
        data = (value["product_id"], value["seller_id"])
        product_seller_ids.append(data)
    return product_seller_ids


def create_query(product_seller_ids: list[tuple[int, int]]) -> Q:
    query = Q()
    for product_id, seller_id in product_seller_ids:
        query |= Q(product_id=product_id, seller_id=seller_id)
    return query


def get_data_from_database(query: Q) -> QuerySet:
    prices = (
        Price.objects.select_related("product", "seller")
        .prefetch_related("seller__delivery_methods", "seller__payment_methods")
        .filter(query)
    )
    return prices


def get_correct_queryset(products_list: dict[str, dict[str, int | bool]]) -> QuerySet:
    product_seller_ids = get_ids_list(products_list)
    query = create_query(product_seller_ids)
    prices = get_data_from_database(query)
    return prices


def check_data_into_db(
    correct_valid_data: dict[str, str],
    products_list: dict[str, dict[str, int | bool]],
    user_id: int,
):

    with transaction.atomic():
        order = Order.objects.create(
            user_id=user_id,
            delivery_city=correct_valid_data["city"],
            delivery_address=correct_valid_data["address"],
            status=Order.PENDING,
        )

        data = create_order_items_data(correct_valid_data, products_list, order)

        OrderItem.objects.bulk_create(data)
        order.order_items.add(*data)
        order.save()


def create_order_items_data(
    correct_valid_data: dict[str, str],
    products_list: dict[str, dict[str, int | bool]],
    order: Order,
) -> list[OrderItem]:
    order_items = []

    payment_queryset = Payment.objects.all()
    delivery_queryset = Delivery.objects.all()

    payment_dict = {payment.name: payment for payment in payment_queryset}
    delivery_dict = {delivery.name: delivery for delivery in delivery_queryset}

    for key, product_data in products_list.items():
        if correct_valid_data["choice_delivery_type"] == "store":
            delivery = delivery_dict.get(correct_valid_data["delivery"])
            payment = payment_dict.get(correct_valid_data["pay"])

        elif correct_valid_data["choice_delivery_type"] == "seller":
            delivery = delivery_dict.get(correct_valid_data[f"delivery_{product_data['seller_id']}"])
            payment = payment_dict.get(correct_valid_data[f"pay_{product_data['seller_id']}"])

        else:
            raise ValidationError("Не удалось привязать способ оплаты к заказу")

        order_items.append(
            OrderItem(
                seller_id=product_data["seller_id"],
                product_id=product_data["product_id"],
                quantity=product_data["quantity"],
                price=product_data["price"],
                delivery=delivery,
                payment_type=payment,
                order=order,
            )
        )
    return order_items
