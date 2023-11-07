from typing import Any, List, Optional, Tuple
from django.contrib import admin
from django.db.models.query import QuerySet
from django.db.models import F, Count
from django.http.request import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from .models import *


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    low = 'low'
    ok = 'ok'

    def lookups(self, request: Any, model_admin: Any) -> List[Tuple[Any, str]]:
        return [
            (self.low, 'Low'),
            (self.ok, 'Ok')
        ]

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() == self.low:
            return queryset.filter(inventory__lt=10)
        elif self.value() == self.ok:
            return queryset.filter(inventory__gte=10)
        return queryset


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    empty_value_display = '-empty-'
    # exclude = ['featured_product']
    list_display = ['id', 'title', 'get_products_count', 'featured_product']
    list_select_related = ['featured_product']
    search_fields = ['title']

    @admin.display(ordering='products_count')
    def get_products_count(self, collection: Collection):
        url = reverse('admin:store_product_changelist') + '?' + \
            'collection__id=' + str(collection.id)
        return format_html(f'<a href={url}>{collection.products_count}<a/>')

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(products_count=Count('products'))


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    actions = ['clear_inventory']
    autocomplete_fields = ['collection']
    list_filter = ['last_update', 'collection', InventoryFilter]
    filter_horizontal = ['promotions']
    list_display = ['id', 'title', 'unit_price', 'inventory',
                    'last_update', 'collection', 'inventory_status']
    list_editable = ['unit_price']
    list_per_page = 10
    list_select_related = ['collection']
    prepopulated_fields = {'slug': ['title'], 'description': ['title']}
    search_fields = ['title']
    # readonly_fields = ['']

    @admin.display(ordering='inventory')
    def inventory_status(self, product: Product):
        if product.inventory < 10:
            return 'Low'
        return 'Ok'

    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset: QuerySet):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request, f'{updated_count} products were successfully updated. ')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user']
    list_display = ['id', 'get_full_name', 'membership', 'orders_count']
    list_editable = ['membership']
    list_select_related = ['user']
    list_per_page = 10
    search_fields = ['user__first_name__istartswith',
                     'user__last_name__istartswith']

    @admin.display(ordering='user__first_name')
    def get_full_name(self, customer: Customer):
        return f'{customer.user.first_name} {customer.user.last_name}'
    get_full_name.short_description = 'Full name'

    @admin.display(ordering='orders_count')
    def orders_count(self, customer: Customer):
        url = reverse('admin:store_order_changelist') + \
            '?'+'customer_id='+str(customer.id)
        return format_html(f'<a href={url}>{customer.orders_count}</a>')

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(orders_count=Count('orders'))


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    extra = 0
    min_num = 1
    model = OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    actions = ['do_complete', 'do_pending']
    inlines = [OrderItemInline]
    list_display = ['id', 'payment_status',
                    'customer', 'items_count', 'placed_at']
    list_per_page = 10
    autocomplete_fields = ['customer']

    def items_count(self, order):
        url = reverse('admin:store_orderitem_changelist') + \
            '?'+'order_id='+str(order.id)
        return format_html(f'<a href={url}>{order.items_count}</a>')

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(items_count=Count('order_items'))

    @admin.action(description='Complete selected orders')
    def do_complete(self, request, queryset: QuerySet):
        counted_update = queryset.update(payment_status='C')
        self.message_user(
            request, f'{counted_update} orders were successfully updated')

    @admin.action(description='Pending selected orders')
    def do_pending(self, request, queryset):
        counted_update = queryset.update(payment_status='P')
        self.message_user(request, f'{counted_update} orders updated')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'unit_price']
    list_per_page = 10
    list_select_related = ['product', 'order']
    list_editable = ['unit_price']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart_id', 'product', 'quantity']
    autocomplete_fields = ['product']
