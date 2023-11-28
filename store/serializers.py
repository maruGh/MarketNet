from django.db import IntegrityError
from django.db.transaction import atomic
from decimal import Decimal
from rest_framework import serializers
from rest_framework.response import Response
from .models import Cart, CartItem, Collection, Customer, Order, OrderItem, Product, ProductImage, Review
from store.signals import order_update


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']
        read_only_fields = ['products_count']
    products_count = serializers.IntegerField(read_only=True)

    # products_count = SerializerMethodField(method_name='get_count_product')

    # def get_count_product(self, collection: Collection):
    #     return collection.products.count()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product_id', 'image']

    def save(self, **kwargs):
        self.instance = ProductImage.objects.create(
            product_id=self.context['product_id'], **self.validated_data)
        return self.instance


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'unit_price',
                  'slug', 'inventory', 'price_with_tax', 'last_update', 'collection', 'images']
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


class CreateCartItemSerializer(serializers.ModelSerializer):
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

        is_valid_quantity = Product.objects.get(
            pk=product_id).id > attrs['quantity']

        if not is_valid_quantity:
            raise serializers.ValidationError(
                'The quantity is beyond the limit')

        return attrs


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']
    total_price = serializers.SerializerMethodField('get_total_price')

    def get_total_price(self, item: CartItem):
        return item.quantity * item.product.unit_price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cart', many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']
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


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'quantity', 'unit_price', 'product']
    product = SimpleProductSerializer()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='order_items', many=True)

    class Meta:
        model = Order
        fields = ['id', 'payment_status',
                  'placed_at', 'customer_id', 'items']


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id):
            raise serializers.ValidationError(
                f'No such cart with the given id')
        if not CartItem.objects.filter(cart_id=cart_id):
            raise serializers.ValidationError(
                f'cart is empty')
        return cart_id

    def save(self, **kwargs):
        customer = Customer.objects.get(user_id=self.context['user_id'])

        with atomic():
            order = Order.objects.create(customer=customer)
            cart_item = CartItem.objects.select_related('product').filter(
                cart_id=self.validated_data['cart_id'])

            order_items = [
                OrderItem(
                    order=order, product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.unit_price
                )
                for item in cart_item
            ]
            OrderItem.objects.bulk_create(order_items)

            Cart.objects.get(id=self.validated_data['cart_id']).delete()

            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']

    def update(self, instance, validated_data):
        order_update.send_robust(self.__class__, instance=instance)
        return super().update(instance, validated_data)
