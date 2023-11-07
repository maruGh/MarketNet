from decimal import Decimal
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from .models import Cart, CartItem, Collection, Customer, Product, Review


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']
        read_only_fields = ['products_count']
    products_count = serializers.IntegerField(read_only=True)

    # products_count = SerializerMethodField(method_name='get_count_product')

    # def get_count_product(self, collection: Collection):
    #     return collection.products.count()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'unit_price',
                  'slug', 'inventory', 'price_with_tax', 'last_update', 'collection']
        read_only_fields = ['price_with_tax', 'last_update']

    collection = serializers.HyperlinkedRelatedField(
        queryset=Collection.objects.all(),
        view_name='collections-detail'
        # read_only=True
    )

    price_with_tax = serializers.SerializerMethodField(method_name='get_tax')

    def get_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'name', 'description', 'date']
        read_only_fields = ['product']

    def create(self, validated_data):
        return Review.objects.create(product_id=self.context['product_id'], **validated_data)


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ['product_id', 'quantity']

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(
                cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item

        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=self.context['cart_id'], **self.validated_data)

        return self.instance

    def validate(self, attrs):
        product_id = attrs['product_id']
        if not Product.objects.filter(pk=product_id).exists():
            raise serializers.ValidationError(
                'There is no product with this id')
        return super().validate(attrs)


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CartItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    product = CartItemProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']
    total_price = serializers.SerializerMethodField('get_total_price')

    def get_total_price(self, item: CartItem):
        return item.quantity * item.product.unit_price


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'cart_items', 'total_price']
        read_only_fields = ['id']

    total_price = serializers.SerializerMethodField(
        method_name='get_total_price')

    def get_total_price(self, cart):
        return sum([i.product.unit_price * i.quantity for i in cart.cart_items.all()])


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    birth_date = serializers.DateField()

    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'membership', 'phone', 'birth_date']
        read_only_fields = ['id']

    def create(self, validated_data):
        try:
            return Customer.objects.create(user_id=self.context.get('user_id'), **validated_data)
        except IntegrityError:
            raise serializers.ValidationError('already exist')
