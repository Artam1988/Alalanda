from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.products_page, name='products_page'),
    path('category/<int:category_id>/', views.product_list, name='category_products'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
]
