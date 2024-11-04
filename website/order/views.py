from django.http import HttpRequest
from django.shortcuts import render


def order_create_view(request: HttpRequest):
    return render(request, "order/order.html")


def order_detail_view(request: HttpRequest):
    return render(request, "order/order-detail.html")
