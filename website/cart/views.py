from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView, View

from catalog.models import Product, Price
from .cart import Cart


class DetailCart(TemplateView):
    """
    Отображение содержания корзины
    """
    template_name = 'cart/cart_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)

        # Эта часть кода нужна для проверки работоспособности вьюхи
        # test_product = Product.objects.first()
        # test_price = Price.objects.get(product=test_product.pk)
        # cart.add(test_product, test_price)
        # При необходимости удалить/закоментировать

        info_cart = [info_product for info_product in cart]
        context['info_cart'] = info_cart
        return context


class AddProductInCart(View):
    """
    Добавление продукта в корзину и возвращает на предыдущую страницу с которой был запрос
    """

    def get(self, product_id: int, price_id: int, quantity: int = 1, update_quantity: bool = False):
        cart = Cart(self.request)
        added_product = Product.objects.get(pk=product_id)
        added_price = Price.objects.get(pk=price_id)
        cart.add(added_product, added_price, quantity, update_quantity)


class UpdateQuantityProductInCart(View):
    """

    """
    def get(self, product_id: int, price_id: int, quantity: int):
        cart = Cart(self.request)
        updated_product = Product.objects.get(pk=product_id)
        price_updated_product = Price.objects.get(pk=price_id)
        cart.add(updated_product, price_updated_product, quantity=quantity, update_quantity=True)


class DeleteProductInCart(View):
    """

    """

    def get(self, product_id: int):
        cart = Cart(self.request)
        deleted_product = Product.objects.get(pk=product_id)
        cart.remove(deleted_product)
