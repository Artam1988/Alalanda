from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.translation import gettext_lazy as _
from products.models import Product
from .models import Cart, CartItem, Order, OrderItem
import uuid

def _get_or_create_cart(request):
    """Helper function to get or create a cart based on session"""
    if not request.session.session_key:
        request.session.create()
    
    session_id = request.session.session_key
    cart = Cart.objects.filter(session_id=session_id).first()
    
    if not cart:
        cart = Cart.objects.create(session_id=session_id)
    
    return cart

def cart_detail(request):
    """Display the cart contents"""
    cart = _get_or_create_cart(request)
    cart_items = cart.items.all().select_related('product')
    
    return render(request, 'orders/cart_detail.html', {
        'cart': cart,
        'cart_items': cart_items
    })

@require_POST
def add_to_cart(request, product_id):
    """Add a product to the cart"""
    product = get_object_or_404(Product, id=product_id)
    cart = _get_or_create_cart(request)
    
    # Check if the product is already in the cart
    cart_item = cart.items.filter(product=product).first()
    
    if cart_item:
        # Update quantity if product already in cart
        cart_item.quantity += 1
        cart_item.save()
    else:
        # Create new cart item
        CartItem.objects.create(cart=cart, product=product, quantity=1)
    
    
    
    # Check if it's an AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': float(cart.total),  # Convert to float for JSON serialization
            'cart_count': cart.items.count()
        })
    
    # For non-AJAX requests, set a session variable to trigger SweetAlert
    request.session['show_cart_alert'] = {
        'title': str(_('Success!')),  # Convert to string to avoid JSON serialization issues
        'product_name': product.safe_translation_getter('name', any_language=True),
        'product_price': str(product.price)
    }
    
    # Redirect back to the product page or referrer
    return redirect(request.META.get('HTTP_REFERER', 'products:products_page'))

@require_POST
def update_cart(request, cart_item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart = cart_item.cart
    
    # Ensure this cart belongs to the current session
    if cart.session_id != request.session.session_key:
        messages.error(request, _('You do not have permission to modify this cart.'))
        return redirect('orders:cart_detail')
    
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    except ValueError:
        messages.error(request, _('Invalid quantity.'))
    
    return redirect('orders:cart_detail')

@require_POST
def remove_from_cart(request, cart_item_id):
    """Remove an item from the cart"""
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart = cart_item.cart
    
    # Ensure this cart belongs to the current session
    if cart.session_id != request.session.session_key:
        messages.error(request, _('You do not have permission to modify this cart.'))
        return redirect('orders:cart_detail')
    
    cart_item.delete()
    messages.success(request, _('Item removed from cart.'))
    
    return redirect('orders:cart_detail')

def clear_cart(request):
    cart = _get_or_create_cart(request)
    
    # Check if the cart belongs to the current user
    
    
    # Delete all items in the cart
    cart.items.all().delete()
    messages.success(request, _('Your cart has been cleared.'))
    return redirect('orders:cart_detail')

def checkout(request):
    """Display checkout form"""
    cart = _get_or_create_cart(request)
    cart_items = cart.items.all().select_related('product')
    
    # Check if cart is empty
    if not cart_items.exists():
        messages.warning(request, _('Your cart is empty. Please add some products before checkout.'))
        return redirect('orders:cart_detail')
    
    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'cart_items': cart_items
    })

@require_POST
def place_order(request):
    """Process the order form and create an order"""
    cart = _get_or_create_cart(request)
    cart_items = cart.items.all().select_related('product')
    
    # Check if cart is empty
    if not cart_items.exists():
        messages.warning(request, _('Your cart is empty. Please add some products before checkout.'))
        return redirect('orders:cart_detail')
    
    # Create the order
    order = Order(
        first_name=request.POST.get('first_name', ''),
        last_name=request.POST.get('last_name', ''),
        email=request.POST.get('email', ''),
        phone=request.POST.get('phone', ''),
        address=request.POST.get('address', ''),
        city=request.POST.get('city', ''),
        postal_code=request.POST.get('postal_code', ''),
        total_amount=cart.total
    )
    order.save()
    
    # Create order items from cart items
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            product_name=cart_item.product.safe_translation_getter('name', any_language=True),
            product_price=cart_item.product.price,
            quantity=cart_item.quantity
        )
    
    # Clear the cart
    cart_items.delete()
    
    # Redirect to order confirmation page
    return redirect('orders:order_confirmation', order_id=order.id)

def order_confirmation(request, order_id):
    """Display order confirmation page"""
    order = get_object_or_404(Order, id=order_id)
    
    return render(request, 'orders/order_confirmation.html', {
        'order': order
    })
