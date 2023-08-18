from django.db import models
from django.core.validators import RegexValidator


class Promotion(models.Model):
    description = models.TextField()
    discount = models.FloatField()


class Collection(models.Model):
    title = models.CharField(max_length=255)


class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    slug = models.SlugField(default="-")
    price = models.DecimalField(max_digits=6, decimal_places=4)
    inventory = models.PositiveIntegerField()
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, related_name='products')
    promotions = models.ManyToManyField(Promotion)


class Customer(models.Model):
    BRONZE = 'B'
    SILVER = 'S'
    GOLDEN = 'G'

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=255)
    phone = models.CharField(max_length=255, validators=[
                             RegexValidator(regex='^(0|\+)[0-9]+')])
    membership = models.CharField(
        choices=[(BRONZE, 'Bronze'), (SILVER, 'Silver'), (GOLDEN, 'Golden')], max_length=1)
    birth_date = models.DateField(auto_now_add=True)


class Order(models.Model):
    PENDING = 'P'
    COMPLETE = 'C'
    FAIL = 'F'
    payment_status = models.CharField(choices=[(
        PENDING, 'Pending'), (COMPLETE, 'Complete'), (FAIL, 'F')], default=PENDING, max_length=1)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name='order_items')
    unit_price = models.DecimalField(max_digits=6, decimal_places=4)
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='order_items')


class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='cart_items')
    quantity = models.PositiveIntegerField()
