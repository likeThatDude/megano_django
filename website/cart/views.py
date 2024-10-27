from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView

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
        # При необходимости удалить/закоментировать
        test_product = Product.objects.first()
        test_price = Price.objects.get(product=test_product.pk)
        cart.add(test_product, test_price, quantity=2)

        info_cart = [info_product for info_product in cart]
        context['info_cart'] = info_cart
        return context


class AddProductInCart(FormView):
    """
    Добавление продукта в корзину и возвращает на предыдущую страницу с которой был запрос
    """
    form_class = None

    def get(self, request, *args, **kwargs):
        """Метод для добавления товара в корзину"""
        pass

    def post(self, request, *args, **kwargs):
        """Метод для изменения количества товаров в корзине"""
        pass
