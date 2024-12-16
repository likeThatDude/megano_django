import stripe
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views import View
from payment.tasks import send_html_email
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from website import settings

from . import utils
from .utils import get_paid_order

"""
Views для работы с процессом оплаты через Stripe.

Данные классы реализуют создание сессии оплаты, обработку успешной или
отмененной оплаты, а также обработку Stripe Webhook событий.  

Классы:

- CreateCheckoutView: Создает сессию оплаты для всех товаров в заказе.
- CreateCheckoutCurrentView: Создает сессию оплаты для конкретного продавца в заказе.
- PaymentSuccessView: Отображает страницу успешной оплаты с деталями заказа.
- PaymentCancelView: Отображает страницу отмены оплаты.
- StripeWebhookAPIView: Обрабатывает события Webhook от Stripe.

Общее:
    Все представления, кроме StripeWebhookAPIView, требуют аутентификации пользователя.
"""

stripe.api_key = settings.SECRET_KEY_STRIPE


class CreateCheckoutView(LoginRequiredMixin, View):
    """
    Создание Stripe Checkout сессии для всех товаров в заказе.

    Обрабатывает GET-запросы для создания сессии Stripe Checkout и перенаправления
    пользователя на страницу оплаты.

    Параметры:
        - request (HttpRequest): HTTP-запрос с информацией о текущем пользователе.
        - order_id (int): Идентификатор заказа, передаваемый в запросе.

    Возвращает:
        - HttpResponseRedirect: Перенаправляет пользователя на URL Stripe Checkout.
        - HttpResponseForbidden: Возвращает ошибку доступа, если заказ не принадлежит текущему пользователю.
    """

    def get(self, request: HttpRequest, order_id: int) -> HttpResponse:
        order = utils.get_order_from_db(order_id=order_id)
        if order.user.pk == request.user.pk:
            correct_urls = utils.get_current_urls_for_payment_response(request)
            session = utils.checkout_process(order=order, redirect_urls=correct_urls, user_login=request.user.login)
            return redirect(session.url, code=303)
        return HttpResponseForbidden(_("You do not have access to payment for this order"))


class CreateCheckoutCurrentView(LoginRequiredMixin, View):
    """
    Создание Stripe Checkout сессии для товаров конкретного продавца в заказе.

    Обрабатывает GET-запросы для создания сессии Stripe Checkout с учетом продавца
    и стоимости его товаров.

    Параметры:
        - request (HttpRequest): HTTP-запрос с информацией о текущем пользователе.
        - order_id (int): Идентификатор заказа.
        - seller_id (int): Идентификатор продавца, товары которого оплачиваются.

    Возвращает:
        - HttpResponseRedirect: Перенаправляет пользователя на URL Stripe Checkout.
        - HttpResponseForbidden: Возвращает ошибку доступа, если заказ не принадлежит текущему пользователю.
    """

    def get(self, request: HttpRequest, order_id: int, seller_id: int) -> HttpResponse:
        order = utils.get_order_from_db(order_id=order_id, all_product=False)
        if order.user.pk == request.user.pk:
            total_price = utils.get_order_total_price(order, seller_id)
            correct_urls = utils.get_current_urls_for_payment_response(request)

            session = utils.checkout_process(
                order=order,
                redirect_urls=correct_urls,
                all_product=False,
                seller_id=seller_id,
                total_price=total_price,
            )
            return redirect(session.url, code=303)
        return HttpResponseForbidden(_("You do not have access to payment for this order"))


class PaymentSuccessView(LoginRequiredMixin, View):
    """
    Отображение страницы успешной оплаты.

    Обрабатывает GET-запросы для отображения страницы успешной оплаты с деталями
    заказа или отдельных товаров.

    Параметры:
        - request (HttpRequest): HTTP-запрос с параметрами успешной оплаты.
            - order_id (str): Идентификатор заказа.
            - seller_id (str): Идентификатор продавца (опционально).
            - total_price (str): Общая сумма оплаты.
            - date (str): Дата оплаты.
            - delivery_price (str): Стоимость доставки (опционально).

    Возвращает:
        - HttpResponse: HTML-страница с деталями успешной оплаты.
        - HttpResponseForbidden: Возвращает ошибку доступа, если данные оплаты некорректны.
        - HttpResponse: Страница с ошибкой 502, если параметры запроса некорректны.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        seller_id = request.GET.get("seller_id", None)
        order_id = request.GET.get("order_id", None)
        total_price = request.GET.get("total_price", None)
        date = request.GET.get("date", None)
        delivery_price = request.GET.get("delivery_price", None)

        context = {
            "total_price": total_price,
            "all_order": True if seller_id is None else False,
            "date": date,
        }
        if not seller_id is None:
            order = get_paid_order(order_id, request.user.pk, seller_id)
            if not order:
                return HttpResponseForbidden(_("You do not have access to payment for this order"))
            context["order"] = order

        elif seller_id is None:
            order = get_paid_order(order_id, request.user.pk)
            if not order:
                return HttpResponseForbidden(_("You do not have access to payment for this order"))
            context["order"] = order
            context["delivery_price"] = delivery_price
        else:
            return HttpResponse(_("Data error when forming the successful payment page"), status=502)
        return render(request, "payment/payment_success.html", context=context)


class PaymentCuncelView(LoginRequiredMixin, View):
    """
    Отображение страницы отмены оплаты.

    Обрабатывает GET-запросы для отображения страницы, информирующей пользователя об отмене оплаты.

    Параметры:
        - request (HttpRequest): HTTP-запрос с информацией об отмене.
            - order_id (str): Идентификатор заказа.

    Возвращает:
        - HttpResponse: HTML-страница с информацией об отмене оплаты.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        order_id = request.GET.get("order_id", None)
        context = {
            "order_id": order_id,
        }
        return render(request, "payment/payment_cancel.html", context=context)


class StripeWebhookAPIView(APIView):
    """
    Обработка событий Stripe Webhook.

    Этот класс обрабатывает события от Stripe, такие как завершение оплаты или
    частичная оплата. Используется для обновления статуса заказа или отдельных товаров.

    Параметры:
        - request (HttpRequest): HTTP-запрос с телом Webhook события и заголовками.
        - *args: Неименованные аргументы.
        - **kwargs: Именованные аргументы.

    Исключения:
        - ValidationError: Выбрасывается при ошибках валидации данных Webhook (невалидный payload или подпись).

    Возвращает:
        - Response: JSON-ответ с подтверждением успешной обработки Webhook.
    """

    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        payload = request.body
        print(payload)
        signature = request.META.get("HTTP_STRIPE_SIGNATURE")
        try:
            event = stripe.Webhook.construct_event(payload, signature, settings.STRIPE_WEBHOOK_SECRET_KEY)
        except ValueError:
            raise ValidationError("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise ValidationError("Invalid signature")

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            user_login = session["metadata"]["user_login"]
            all_order = session["metadata"]["all_order"]
            all_order = int(all_order)
            if all_order == 1:
                utils.change_order_payment_status(session=session)
            elif all_order == 0:
                utils.change_certain_items_payment_status(session=session)
            from payment.tasks import send_html_email

            send_html_email.delay(user_login, session["customer_details"]["email"])
        return Response({"status": "success"}, status=200)
