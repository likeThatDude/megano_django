from decimal import ROUND_HALF_UP
from decimal import Decimal
from multiprocessing.connection import deliver_challenge
from typing import Any
from typing import List

from account.models import CustomUser
from catalog.models import Delivery
from catalog.models import Payment
from catalog.models import Price
from django.db import transaction
from django.db.models import Q
from django.db.models import QuerySet
from django.http import HttpRequest
from order.models import DeliveryPrice
from order.models import Order
from order.models import OrderItem
from rest_framework.exceptions import ValidationError


def get_full_username(user: CustomUser) -> str:
    """
    Формирует полное имя пользователя на основе его данных профиля.
    Для предзаполнения данных в форме заказа.

    Этот метод извлекает из профиля пользователя имя, фамилию и отчество (если они есть)
    и объединяет их в строку, разделяя пробелами.

    Параметры:
        user (CustomUser): Объект пользователя, для которого формируется полное имя.

    Возвращает:
        str: Полное имя пользователя, состоящее из имени, фамилии и отчества (если они присутствуют).
    """
    user_name_data = (user.profile.first_name, user.profile.last_name, user.profile.patronymic)
    full_name = " ".join(data for data in user_name_data if data is not None)
    return full_name


def get_user_data(request: HttpRequest) -> dict[str, str]:
    """
    Извлекает данные пользователя из базы данных и формирует словарь с информацией о пользователе.

    Этот метод извлекает пользователя по его ID из запроса, получает данные из профиля (имя, телефон)
    и возвращает словарь с полным именем, номером телефона и email.

    Параметры:
        request (HttpRequest): Объект HTTP-запроса, содержащий информацию о текущем аутентифицированном пользователе.

    Возвращает:
        dict[str, str]: Словарь, содержащий полное имя пользователя, его номер телефона и email.
    """
    user = CustomUser.objects.select_related("profile").get(pk=request.user.id)
    full_user_name = get_full_username(user)
    correct_user_data = {
        "name": full_user_name,
        "phone": user.profile.phone,
        "email": user.email,
    }
    return correct_user_data


def get_ids_list(products_list: dict) -> list[tuple[int, int]]:
    """
    Извлекает список кортежей с идентификаторами продуктов и продавцов из словаря с данными товаров.

    Этот метод обрабатывает словарь товаров, где каждый товар имеет ключи 'product_id' и 'seller_id',
    и возвращает список кортежей, содержащих соответствующие идентификаторы.

    Параметры:
        products_list (dict): Словарь, содержащий данные товаров, где для каждого товара есть
                               'product_id' и 'seller_id'.

    Возвращает:
        list[tuple[int, int]]: Список кортежей, каждый из которых содержит идентификатор продукта
        и идентификатор продавца.
    """
    product_seller_ids = []
    for key, value in products_list.items():
        data = (value["product_id"], value["seller_id"])
        product_seller_ids.append(data)
    return product_seller_ids


def create_query(product_seller_ids: list[tuple[int, int]]) -> Q:
    """
    Создает сложный запрос для фильтрации продуктов по их идентификатору и идентификатору продавца.

    Этот метод принимает список кортежей, где каждый кортеж содержит идентификаторы продукта и продавца,
    и формирует запрос, который будет использоваться для фильтрации объектов, например, в Django ORM.

    Параметры:
        product_seller_ids (list[tuple[int, int]]): Список кортежей, где каждый кортеж содержит идентификатор продукта
                                                   и идентификатор продавца.

    Возвращает:
        Q: Объект Q, представляющий логический запрос для фильтрации объектов по продукту и продавцу.
    """
    query = Q()
    for product_id, seller_id in product_seller_ids:
        query |= Q(product_id=product_id, seller_id=seller_id)
    return query


def get_data_from_database(query: Q) -> QuerySet:
    """
    Извлекает данные из базы данных на основе переданного запроса.

    Этот метод выполняет запрос к базе данных для получения объектов модели `Price`,
    используя фильтрацию с помощью переданного объекта `Q` для выборки нужных данных.
    Также применяются методы `select_related` и `prefetch_related` для оптимизации запросов.

    Параметры:
        query (Q): Объект Q, содержащий условие для фильтрации данных в базе.

    Возвращает:
        QuerySet: Набор объектов `Price`, соответствующих заданным условиям.
    """
    prices = (
        Price.objects.select_related("product", "seller")
        .prefetch_related("seller__delivery_methods", "seller__payment_methods")
        .filter(query)
    )
    return prices


def get_correct_queryset(products_list: dict[str, dict[str, int | bool]]) -> QuerySet:
    """
    Формирует и выполняет запрос к базе данных для получения данных о ценах.

    Эта функция принимает список продуктов с дополнительными данными, извлекает из него
    соответствующие идентификаторы товаров и продавцов, затем формирует запрос на выборку
    данных о ценах для этих товаров и продавцов из базы данных.

    Параметры:
        products_list (dict): Словарь, где ключами являются строки, а значениями —
        словари с дополнительной информацией о каждом товаре. Эти данные используются для
        формирования запроса к базе данных.

    Возвращает:
        QuerySet: Набор объектов `Price`, соответствующих запросу, включая связи с продуктами и продавцами.
    """
    product_seller_ids = get_ids_list(products_list)
    query = create_query(product_seller_ids)
    prices = get_data_from_database(query)
    return prices


def data_preparation_and_recording(
    correct_valid_data: dict[str, str],
    products_list: dict[str, dict[str, int | bool]],
    user_id: int,
):
    """
    Подготавливает и сохраняет данные о заказе в базе данных.

    Эта функция получает корректные данные формы заказа, список продуктов в корзине и идентификатор пользователя,
    затем создает новый заказ, добавляет соответствующие товары в заказ и сохраняет всю информацию в базе данных.

    Параметры:
        correct_valid_data (dict): Словарь, содержащий корректные данные формы заказа (например, адрес, телефон, email).
        products_list (dict): Словарь, содержащий данные о продуктах в корзине
                              (например, id продукта, id продавца, количество).
        user_id (int): Идентификатор пользователя, который сделал заказ.

    Возвращает:
        None

    Используется транзакция для обеспечения целостности данных при записи в базу.
    """
    total_price = get_total_price(products_list)
    deliver_price = set_delivery_price(correct_valid_data, products_list, total_price)

    with transaction.atomic():
        order = Order.objects.create(
            user_id=user_id,
            name=correct_valid_data["name"],
            delivery_city=correct_valid_data["city"],
            delivery_address=correct_valid_data["address"],
            recipient_phone=correct_valid_data["phone"],
            recipient_email=correct_valid_data["mail"],
            status=Order.PENDING,
            comment=correct_valid_data["comment"],
            total_price=total_price,
            delivery_price=deliver_price,
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
    """
    Создает список объектов OrderItem для добавления в заказ.

    Эта функция создает данные для каждой позиции заказа, включая информацию о продавце, продукте, количестве,
    цене, способе доставки и оплате. Все эти данные используются для создания объектов OrderItem, которые затем
    добавляются в заказ.

    Параметры:
        correct_valid_data (dict): Словарь с правильными данными формы заказа (например, способ доставки, способ оплаты).
        products_list (dict): Словарь, содержащий информацию о продуктах в корзине (например, id продукта,
                              id продавца, количество).
        order (Order): Объект заказа, к которому будут привязаны созданные OrderItem.

    Возвращает:
        list[OrderItem]: Список объектов OrderItem, который будет добавлен в заказ.

    Исключения:
        ValidationError: Если не удается привязать способ оплаты к заказу.

    Примечание:
        Функция использует данные о доставке и оплате из переданных параметров, чтобы правильно привязать каждый товар
        к его способу доставки и оплаты.
    """
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


def create_product_context_data(
    products_list: dict[str, dict[str, int | bool]]
) -> dict[int | str, dict[str, int] | Decimal]:
    """
    Создает контекст данных для продуктов, который включает информацию о цене, количестве
    каждого продукта, а также общую стоимость.

    Функция преобразует информацию о товарах в корзине в формат, удобный для отображения на странице,
    где для каждого продукта создается словарь с его ценой и количеством. Также вычисляется общая стоимость
    всех товаров в корзине.

    Параметры:
        products_list (dict): Словарь, содержащий информацию о продуктах в корзине, включая id продукта, цену и количество.

    Возвращает:
        dict: Словарь, в котором ключи — это id продукта или строковый ключ "total_price", а значения — это
              либо словари с ценой и количеством продукта, либо общая цена всех товаров.

    Примечание:
        Значение цены для каждого товара преобразуется в объект Decimal для корректной работы с финансовыми данными.
    """
    correct_data: dict[int | str, dict[str, int] | Decimal] = dict()

    for value in products_list.values():
        correct_data[value["product_id"]] = {
            "price": Decimal(str(value["price"])),
            "quantity": value["quantity"],
        }

    total_price = get_total_price(products_list)

    correct_data["total_price"] = total_price

    return correct_data


def get_total_price(products_list: dict[str, dict[str, int | bool]]) -> Decimal:
    """
    Вычисляет общую стоимость товаров в корзине.

    Функция суммирует стоимость всех продуктов в корзине, используя их цены,
    и округляет результат до двух знаков после запятой.

    Параметры:
        products_list (dict): Словарь, где каждый элемент представляет товар с его ценой и количеством.

    Возвращает:
        Decimal: Общая стоимость товаров в корзине, округленная до двух знаков после запятой.

    Примечание:
        Цена каждого товара преобразуется в объект Decimal для точных вычислений с денежными суммами.
    """
    total_price = sum(Decimal(str(value["price"])) for value in products_list.values())
    correct_total_price = total_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return correct_total_price


def set_delivery_price(
    correct_valid_data: dict[str, str],
    products_list: dict[str, dict[str, int | bool]],
    total_price: Decimal,
):
    """
    Определяет цену доставки для заказа в зависимости от выбранного способа доставки.

    Функция проверяет тип доставки (по продавцу или в магазин), а также общую стоимость
    товаров в заказе и количество продавцов. В зависимости от этих факторов назначается
    подходящая цена доставки.

    Параметры:
        correct_valid_data (dict): Словарь, содержащий валидные данные формы с информацией о доставке.
        products_list (dict): Словарь с информацией о товарах в корзине, включая их цену и количество.
        total_price (Decimal): Общая стоимость товаров в корзине.

    Возвращает:
        deliver_price (DeliveryPrice | None): Цена доставки, выбранная на основе данных, или None,
        если доставка не требуется.

    Примечание:
        При определении цены доставки учитывается, является ли заказ доставкой от продавца или
        в магазин, а также стоимость заказа и количество продавцов.
    """
    deliver_price = None
    if correct_valid_data["choice_delivery_type"] == "seller":
        deliver_price = DeliveryPrice.objects.get(name=DeliveryPrice.FREE_DELIVERY)
    elif correct_valid_data["choice_delivery_type"] == "store":
        if correct_valid_data["delivery"] == Delivery.SHOP_STANDARD:
            seller_ids = {product["seller_id"] for product in products_list.values()}
            if total_price < 2000 or len(seller_ids) > 1:
                deliver_price = DeliveryPrice.objects.get(name=DeliveryPrice.STANDARD_DELIVERY)
            else:
                deliver_price = DeliveryPrice.objects.get(name=DeliveryPrice.FREE_DELIVERY)
        elif correct_valid_data["delivery"] == Delivery.SHOP_EXPRESS:
            deliver_price = DeliveryPrice.objects.get(name=DeliveryPrice.EXPRESS_DELIVERY)
    return deliver_price


def get_order_products(products_list: dict[str, dict[str, int | bool]]) -> dict[str, dict[str, int | bool]]:
    """
    Фильтрует товары, которые могут быть заказаны, на основе значения 'to_order'.

    Эта функция принимает список товаров и фильтрует его, оставляя только те товары,
    для которых в поле 'to_order' установлено значение True.

    Параметры:
        products_list (dict): Словарь, где ключи — это идентификаторы товаров,
                              а значения содержат информацию о товаре, включая
                              поле 'to_order', которое указывает, был ли товар
                              отмечен в корзине для заказа.

    Возвращает:
        dict: Отфильтрованный словарь товаров, которые можно заказать.

    Примечание:
        Функция исключает товары с значением 'to_order' равным False.
    """
    products_correct_list = {key: value for key, value in products_list.items() if value["to_order"]}
    return products_correct_list


def create_errors_list(errors) -> list[tuple[int, str]]:
    """
    Преобразует ошибки в список кортежей с порядковым номером и сообщением ошибки.

    Функция принимает список ошибок и создает новый список, где каждый элемент
    — это кортеж, состоящий из порядкового номера и текста ошибки.

    Параметры:
        errors (dict_items): Список ошибок в формате dict_items, где каждый элемент
                             представляет собой пару (ключ, список ошибок).
                             Например: ('field_name', ['Error message']).

    Возвращает:
        list: Список кортежей, где каждый кортеж состоит из порядкового номера
              и текста ошибки.

    Пример:
        Вход:
            errors = dict_items([('city', ['Город — это обязательное поле для заполнения.'])])
        Выход:
            [(1, 'Город — это обязательное поле для заполнения.'), ...]
    """
    errors_data = list()
    for number, error in enumerate(errors, start=1):
        errors_data.append((number, *error[1]))
    return errors_data
