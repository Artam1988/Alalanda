from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'session_id', 'created_at', 'updated_at', 'total']
    inlines = [CartItemInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ['subtotal']
    
    def get_readonly_fields(self, request, obj=None):
        # If this is an existing Order, make fields readonly
        if obj and obj.pk:
            return ['product_name', 'product_price', 'quantity', 'subtotal']
        # For new orders, only make subtotal readonly
        return ['subtotal']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'phone', 'status', 'created_at', 'total_amount']
    list_filter = ['status', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['total_amount']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Customer Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Shipping Information', {
            'fields': ('address', 'city', 'postal_code')
        }),
        ('Order Information', {
            'fields': ('status', 'total_amount')
        }),
    )
    def save_model(self, request, obj, form, change):
        # Save the Order instance to generate a primary key
        super().save_model(request, obj, form, change)

        # Calculate total_amount based on related OrderItems
        if obj.pk:  # Ensure the object has a primary key
            # Use a safer method to calculate total that handles empty queryset
            items = obj.items.all()
            if items.exists():
                obj.total_amount = sum(item.subtotal for item in items)
                obj.save(update_fields=['total_amount'])  # Only update this field

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product_name', 'product_price', 'quantity', 'subtotal']
    list_filter = ['order__status']
    search_fields = ['order__first_name', 'order__last_name', 'product_name']
    readonly_fields = ['product_name', 'product_price', 'subtotal']
    fieldsets = (
        ('Order Information', {
            'fields': ('order',)
        }),
        ('Product Information', {
            'fields': ('product_name', 'product_price', 'quantity')
        }),
        ('Subtotal', {
            'fields': ('subtotal',)
        }),
    )
