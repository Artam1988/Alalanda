from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update/<int:cart_item_id>/', views.update_cart, name='update_cart'),
    path('remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
]
