from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product

@receiver(post_save, sender=Product)
def clear_cache_on_save(sender, instance, **kwargs):
    cache.clear()

@receiver(post_delete, sender=Product)
def clear_cache_on_delete(sender, instance, **kwargs):
    cache.clear()
