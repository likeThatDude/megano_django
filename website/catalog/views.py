from django.db.models import Q, Prefetch
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views.generic import DetailView, TemplateView
from . import models
from .models import Product, Seller, Price, Review, Category, Specification
from .forms import ReviewForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Product, Review
from .serializers import ProductSerializer, ReviewSerializer, ReviewFormSerializer


def catalog_view(request: HttpRequest):
    return render(request, "catalog/catalog.html")


class CategoryDetailView(DetailView):
    pass


class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            product_serializer = ProductSerializer(product)

            reviews = Review.objects.filter(product=product)
            review_serializer = ReviewSerializer(reviews, many=True)

            return Response({
                'product': product_serializer.data,
                'reviews': review_serializer.data
            }, status=status.HTTP_200_OK)

        except Product.DoesNotExist:
            return Response({'error': 'Продукт не найден'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Продукт не найден'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.is_authenticated:
            serializer = ReviewFormSerializer(data=request.data)
            if serializer.is_valid():
                review = serializer.save(product=product, user=request.user)
                return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'Чтобы добавить отзыв, вам необходимо войти в систему.'}, status=status.HTTP_403_FORBIDDEN)

    # class ProductDetailView(TemplateView):
    #     template_name = 'catalog/product_detail.html'
