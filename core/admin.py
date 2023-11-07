from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUseAdmin
from django.contrib.contenttypes.admin import GenericTabularInline
from store.admin import ProductAdmin
from store.models import Product
from tags.models import TaggedItem

from core.models import User


@admin.register(User)
class UserAdmin(BaseUseAdmin):
    search_fields = ['first_name', 'last_name', 'username', 'email']
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", 'email', "password1", "password2"),
            },
        ),
    )


class TaggedItemInline(GenericTabularInline):
    model = TaggedItem
    extra = 0
    min_num = 1
    autocomplete_fields = ['tag']


class CustomProductAdmin(ProductAdmin):
    inlines = [TaggedItemInline]


admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)
