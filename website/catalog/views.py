from django.db.models import Q, Prefetch
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views.generic import DetailView, TemplateView
from . import models
from .models import Product, Seller, Storage, Review, Category, Specification
# from .forms import ReviewForm
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from .models import Product, Review
# from .serializers import ProductSerializer, ReviewSerializer, ReviewFormSerializer


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
