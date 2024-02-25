from django.dispatch import receiver
from store.signals import order_update, trash_object


@receiver(order_update)
def on_update_order(sender, instance, **kwargs):
    print(instance.customer)


@receiver(trash_object)
def take_deleted_obj(sender, item, **kwargs):
    print(item)
