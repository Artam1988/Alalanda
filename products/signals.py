from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django_redis import get_redis_connection
from .models import Product, Category

@receiver([post_save, post_delete], sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    """Clear product-related caches when a product is saved or deleted"""
    # Clear specific product cache
    cache.delete(f"product_detail:{instance.id}:en")
    cache.delete(f"product_detail:{instance.id}:ar")
    
    # Clear category cache for this product's category
    cache.delete(f"product_list:{instance.category_id}:en")
    cache.delete(f"product_list:{instance.category_id}:ar")
    
    # Clear products page cache with pattern matching in Redis
    redis_conn = get_redis_connection("default")
    for key in redis_conn.scan_iter("*products_page*"):
        redis_conn.delete(key)

@receiver([post_save, post_delete], sender=Category)
def invalidate_category_cache(sender, instance, **kwargs):
    """Clear category-related caches when a category is saved or deleted"""
    # Clear category cache
    cache.delete(f"product_list:{instance.id}:en")
    cache.delete(f"product_list:{instance.id}:ar")
    
    # Clear products page cache with pattern matching in Redis
    redis_conn = get_redis_connection("default")
    for key in redis_conn.scan_iter("*products_page*"):
        redis_conn.delete(key)
