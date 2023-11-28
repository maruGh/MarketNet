from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import ValidationError

from store.models import CartItem, Customer


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_for_new_user(sender, instance, **kwargs):
    if kwargs['created']:
        Customer.objects.create(user=instance)


# @receiver(pre_save, sender=CartItem)
# def validate_quantity_amount_for_cart_item(sender, instance: CartItem, **kwargs):
#     cart_item = instance

#     if cart_item.quantity > cart_item.product.inventory:
#         raise ValidationError(
#             'Invalid quantity because quantity is greater than existing quantity')
