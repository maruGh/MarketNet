from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from store.admin import ProductAdmin
from store.models import Product
from tags.models import TaggedItem


class TaggedItemInline(GenericTabularInline):
    model = TaggedItem
    extra = 0
    min_num = 1
    autocomplete_fields = ['tag']


class CustomProductAdmin(ProductAdmin):
    inlines = [TaggedItemInline]


admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)
