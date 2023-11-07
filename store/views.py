from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import status

from .permissions import IsAdminOrReadOnly, IsMyCustomerProfileOrReadOnly, ViewCustomerHistoryPermission
from .filters import ProductFilter
from .models import Cart, CartItem, Collection, Customer, Product, Review
from .pagination import DefaultPagination
from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CollectionSerializer, CustomerSerializer, ProductSerializer, ReviewSerializer, UpdateCartItemSerializer


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.prefetch_related(
        'products').annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializer

    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        collection = get_object_or_404(Collection, pk=kwargs['pk'])
        if collection.products.count() > 0:
            return Response({'error': 'it have products'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related(
        'collection').prefetch_related('promotions').all()
    serializer_class = ProductSerializer

    permission_classes = [IsAdminOrReadOnly]

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


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('cart_items__product').all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    pagination_class = DefaultPagination
    http_method_names = ['get', 'patch', 'post', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.select_related('product', 'cart').filter(cart_id=self.kwargs['cart_pk'])

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.select_related('product').filter(product_id=self.kwargs['product_pk']).all()

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.select_related('user').all()
    serializer_class = CustomerSerializer

    permission_classes = [IsAdminOrReadOnly]

    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):
        return Response('Ok')

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsMyCustomerProfileOrReadOnly, IsAuthenticated])
    def me(self, request):
        [customer, is_create] = Customer.objects.get_or_create(
            user_id=request.user.id)

        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}
