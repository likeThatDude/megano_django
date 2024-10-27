from itertools import product

from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, DetailView, DeleteView, CreateView

from catalog.models import Product
from . import utils
from .models import Comparison
from .utils import create_categorization


class ComparisonView(TemplateView):
    template_name = 'comparison/comparison.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            comparison_products = utils.get_products_with_auth_user(user)
            data = create_categorization(comparison_products[1])
            context['comparison_products'] = data
            context['correct_spec'] = comparison_products[0]
        else:
            comparison_products = utils.get_products_with_unauth_user(self.request)
            data = create_categorization(comparison_products[1], False)
            context['comparison_products'] = data
            context['correct_spec'] = comparison_products[0]
        return context


class ComparisonDeleteView(DeleteView):
    model = Comparison
    success_url = reverse_lazy('comparison:comparison_page')

    def post(self, request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            self.object = self.get_object()
            self.object.delete()
            return HttpResponseRedirect(self.get_success_url())
        else:
            product_session_id = request.session.get('products_ids', [])
            if product_session_id:
                product_session_id.remove(str(kwargs['pk']))
            request.session['products_ids'] = product_session_id
        return HttpResponseRedirect(reverse_lazy('comparison:comparison_page'))


class ComparisonAddView(View):

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            product_id = request.POST.get('product')
            product = get_object_or_404(Product, pk=product_id)
            Comparison.objects.create(user=request.user, product=product)

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            product_id = request.POST.get('product')
            product_session_id = request.session.get('products_ids', [])

            if product_id not in product_session_id:
                product_session_id.append(product_id)

            request.session['products_ids'] = product_session_id
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
