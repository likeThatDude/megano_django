from django.db.models import Q, Prefetch
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views.generic import DetailView, TemplateView
from . import models
from .models import Product, Seller, Storage, Review, Category, Specification
from .forms import ReviewForm


def catalog_view(request: HttpRequest):
    return render(request, "catalog/catalog.html")


class CategoryDetailView(DetailView):
    pass


class ProductDetailView(DetailView):
    template_name = 'catalog/product_detail.html'
    model = Product
    context_object_name = 'product'

    def get_queryset(self):
        pk = self.kwargs.get('pk')

        return (Product.objects
                .select_related('category')
                .prefetch_related(
            Prefetch(
                'images',
            ),
            Prefetch(
                'review',
                queryset=Review.objects.only('user', 'text', 'created_at').order_by('-created_at'),
            ),
            Prefetch(
                'storage',
                queryset=Storage.objects.select_related('seller').only('seller', 'price')
                .order_by('price')
            ),
            Prefetch(
                'specifications',
                queryset=Specification.objects.select_related('name').only('value', 'name__name')
                .order_by('name__name')
            )
        ).filter(pk=pk))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['storages'] = self.object.storage.all()
        context['reviews_data'] = self.object.review.all()
        return context

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        product = self.get_product(pk)
        reviews = Review.objects.filter(product=product)
        form = ReviewForm()
        context = {
            'product': product,
            'reviews': reviews,
            'form': form,
        }
        return render(request, self.template_name, context)

    def post(self, request, product_id):
        if request.user.is_authenticated:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = self.get_product(product_id)
                review.user = request.user
                review.save()
                return redirect('product_detail', product_id=product_id)

        else:
            form = ReviewForm()
            form.add_error(None, "Вы должны быть авторизованы для добавления отзыва.")

        product = self.get_product(product_id)
        reviews = Review.objects.filter(product=product)
        context = {
            'product': product,
            'reviews': reviews,
            'form': form,
        }
        return render(request, self.template_name, context)

    def get_product(self, product_id):
        from .models import Product
        return Product.objects.get(id=product_id)

    # class ProductDetailView(TemplateView):
    #     template_name = 'catalog/product_detail.html'
