from datetime import datetime

import stripe
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, Http404
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views import View
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from website import settings

from . import utils
from .utils import get_paid_order

stripe.api_key = settings.SECRET_KEY_STRIPE


class CreateCheckoutView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest, order_id: int) -> HttpResponse:
        order = utils.get_order_from_db(order_id=order_id)
        if order.user.pk == request.user.pk:
            correct_urls = utils.get_current_urls_for_payment_response(request)
            session = utils.checkout_process(order=order, redirect_urls=correct_urls)
            return redirect(session.url, code=303)
        return HttpResponseForbidden(_("У вас нету доступа к оплате данного заказа"))


class CreateCheckoutCurrentView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, order_id: int, seller_id: int) -> HttpResponse:
        order = utils.get_order_from_db(order_id=order_id, all_product=False)

        if order.user.pk == request.user.pk:
            total_price = utils.get_order_total_price(order, seller_id)
            correct_urls = utils.get_current_urls_for_payment_response(request)

            session = utils.checkout_process(
                order=order, redirect_urls=correct_urls, all_product=False, seller_id=seller_id, total_price=total_price
            )
            return redirect(session.url, code=303)
        return HttpResponseForbidden(_("У вас нету доступа к оплате данного заказа"))


class PaymentSuccessView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        seller_id = request.GET.get('seller_id', None)
        order_id = request.GET.get('order_id', None)
        total_price = request.GET.get('total_price', None)
        date = request.GET.get('date', None)
        delivery_price = request.GET.get('delivery_price', None)

        context = {
            'total_price': total_price,
            'all_order': True if seller_id is None else False,
            'date': date,
        }
        if not seller_id is None:
            order = get_paid_order(order_id, request.user.pk, seller_id)
            if not order:
                return HttpResponseForbidden(_("У вас нету доступа к оплате данного заказа"))
            context['order'] = order

        elif seller_id is None:
            order = get_paid_order(order_id, request.user.pk)
            if not order:
                return HttpResponseForbidden(_("У вас нету доступа к оплате данного заказа"))
            context['order'] = order
            context['delivery_price'] = delivery_price
        else:
            return HttpResponse(_('Ошибка данных при формировании страницы успешной оплаты'), status=502)
        return render(request, "payment/payment_success.html", context=context)


class PaymentCuncelView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        order_id = request.GET.get('order_id', None)
        context = {
            'order_id': order_id,
        }
        return render(request, "payment/payment_cancel.html", context=context)


class StripeWebhookAPIView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        payload = request.body
        signature = request.META.get("HTTP_STRIPE_SIGNATURE")
        try:
            event = stripe.Webhook.construct_event(payload, signature, settings.STRIPE_WEBHOOK_SECRET_KEY)
        except ValueError:
            raise ValidationError("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise ValidationError("Invalid signature")
        #
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            all_order = session["metadata"]["all_order"]
            all_order = int(all_order)
            if all_order == 1:
                utils.change_order_payment_status(session=session)
            elif all_order == 0:
                utils.change_certain_items_payment_status(session=session)

        return Response({"status": "success"}, status=200)
