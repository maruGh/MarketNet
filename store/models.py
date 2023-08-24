from typing import Iterable, Optional
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Promotion(models.Model):
    description = models.TextField()
    discount = models.FloatField()


class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='collections')

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']


class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(default="-")
    unit_price = models.DecimalField(
        max_digits=6, decimal_places=4, validators=[MinValueValidator(10)])
    inventory = models.PositiveIntegerField()
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, related_name='products')
    promotions = models.ManyToManyField(Promotion, blank=True)

    def __str__(self) -> str:
        return f'{self.title}'

    class Meta:
        ordering = ['title']


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

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        ordering = ['first_name', 'last_name']


class Order(models.Model):
    PENDING = 'P'
    COMPLETE = 'C'
    FAIL = 'F'
    payment_status = models.CharField(choices=[(
        PENDING, 'Pending'), (COMPLETE, 'Complete'), (FAIL, 'Failed')], default=PENDING, max_length=1)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='orders')
    placed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.payment_status


class OrderItem(models.Model):
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name='order_items')
    unit_price = models.DecimalField(max_digits=6, decimal_places=4)
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='order_items')

    def __str__(self) -> str:
        return self.product.title


class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='cart_items')
    quantity = models.PositiveIntegerField()
