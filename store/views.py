from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import status

from .filters import ProductFilter
from .models import Collection, Product, Review
from .pagination import DefaultPagination
from .serializers import CollectionSerializer, ProductSerializer, ReviewSerializer


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.prefetch_related(
        'products').annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializer

    def destroy(self, request, *args, **kwargs):
        collection = get_object_or_404(Collection, pk=kwargs['pk'])
        if collection.products.count() > 0:
            return Response({'error': 'it have products'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related(
        'collection').prefetch_related('promotions').all()
    serializer_class = ProductSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ProductFilter
    # ordering_fields = ['collection__title']
    search_fields = ['title', 'description']
    pagination_class = DefaultPagination

    def destroy(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs['pk'])

        if product.order_items.count() > 0:
            return Response({'error': 'This product is associated with orderitem'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.select_related('product').filter(product_id=self.kwargs['product_pk']).all()

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
