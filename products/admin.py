from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ('id', 'name')
    search_fields = ('translations__name',)
    list_filter = ('id',)
    ordering = ('id',)
    list_per_page = 10
    list_display_links = ('id', 'name')
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
    )

@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = ('id', 'name', 'category', 'price','is_featured')
    search_fields = ('translations__name', 'category__translations__name') 
    list_filter = ('category',)
    ordering = ('id',)
    list_per_page = 10
    list_display_links = ('id', 'name')
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'image', 'price', 'is_featured')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('description',)
        }),
    )