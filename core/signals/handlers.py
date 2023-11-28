from django.dispatch import receiver
from store.signals import order_update


@receiver(order_update)
def on_update_order(sender, instance, **kwargs):
    print(instance.customer)
