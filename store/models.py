from typing import Iterable, Optional
from django.conf import settings
from django.contrib import admin
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from uuid import uuid4


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
    slug = models.SlugField(null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(10)])
    inventory = models.PositiveIntegerField()
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, related_name='products')
    promotions = models.ManyToManyField(Promotion, blank=True)

    def __str__(self) -> str:
        return f'{self.title}'

    class Meta:
        ordering = ['title']


class Review(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews')
    date = models.DateField(auto_now=True)


class Customer(models.Model):
    BRONZE = 'B'
    SILVER = 'S'
    GOLDEN = 'G'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=255, validators=[
                             RegexValidator(regex='^(0|\+)[0-9]+')])
    membership = models.CharField(
        choices=[(BRONZE, 'Bronze'), (SILVER, 'Silver'), (GOLDEN, 'Golden')], default=SILVER, max_length=1)
    birth_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name

    class Meta:
        permissions = [
            ('view_history', 'Can view history')
        ]
        ordering = ['user__first_name', 'user__last_name']


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

    class Meta:
        permissions = [
            ('cancel_order', 'Can cancel order')
        ]


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
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='cart_items')
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = [('cart', 'product')]
