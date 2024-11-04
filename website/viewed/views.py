from django.db import transaction
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.models import Product

from .models import Viewed
from .serializers import ViewedSerializer


class ViewedListActionsView(APIView):
    serializer_class = ViewedSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=[_("views")],
        summary="Есть ли товар в списке просмотренных",
        description="Проверяет есть ли указанный товар в списке просмотренных"
        " и возвращает true если есть, иначе - false.",
    )
    def get(self, request: Request, product_id: int) -> Response:
        exists = Viewed.objects.filter(
            user=request.user, product_id=product_id
        ).exists()
        return Response({"exists": exists}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=[_("views")],
        summary="Добавление/обновление товара в просмотренных",
        description="Добавляет или обновляет товар в списке просмотренных текущим пользователем."
        " Если товар еще не существует в списке, то увеличивается его количество просмотров.",
    )
    def post(self, request: Request, product_id: int) -> Response:
        with transaction.atomic():
            new_view, created = Viewed.objects.update_or_create(
                user=request.user, product_id=product_id
            )

            if created:
                product = Product.objects.select_for_update().get(id=product_id)
                product.views += 1
                product.save()

        serialized = ViewedSerializer(new_view)
        return Response(
            {"viewed": serialized.data},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        tags=[_("views")],
        summary="Удаление товара из просмотренных",
        description="Удаляет товар из списка просмотренных пользователем, "
        "возвращает логическое значение результата операции.",
    )
    def delete(self, request: Request, product_id: int) -> Response:
        deleted_rows, deleted_dict = Viewed.objects.filter(
            user=request.user, product_id=product_id
        ).delete()
        return Response({"deleted": deleted_rows != 0}, status=status.HTTP_200_OK)


class ViewedListView(APIView):
    serializer_class = ViewedSerializer

    @extend_schema(
        tags=[_("views")],
        summary="Список просмотренных товаров",
        description="Возварщает список просмотренных текущим пользователем товаров (по умолчанию 20)",
    )
    def get(self, request: Request):
        limit = request.query_params.get("limit", 20)
        viewed_products = Viewed.objects.filter(user=request.user)[:limit].all()
        serialized = ViewedSerializer(viewed_products, many=True)
        return Response(
            {"viewed products": serialized.data},
            status=status.HTTP_200_OK,
        )


class ViewsCountView(APIView):
    serializer_class = ViewedSerializer

    @extend_schema(
        tags=[_("views")],
        summary="Количество просмотров товара",
        description="Возвращает количество просмотров указанного товара.",
    )
    def get(self, request: Request, product_id: int) -> Response:
        product = Product.objects.only("views").filter(id=product_id).first()
        return Response(
            {"product id": product_id, "views count": product.views},
            status=status.HTTP_200_OK,
        )
