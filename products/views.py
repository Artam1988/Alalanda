from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Min, Max, Prefetch, Count
from django.views.decorators.cache import cache_page
from django.utils.cache import get_cache_key, learn_cache_key, patch_response_headers
from django.core.cache import cache
from parler.utils import get_active_language_choices
from .models import Category, Product

def products_page(request):
    # Get price range in a single query
    price_range = Product.objects.aggregate(min_price=Min('price'), max_price=Max('price'))
    min_price = price_range['min_price'] or 0
    max_price = price_range['max_price'] or 1000
    
    # Get search parameters
    search_query = request.GET.get('search', '')
    min_price_filter = request.GET.get('min_price', min_price)
    max_price_filter = request.GET.get('max_price', max_price)
    
    # Try to convert price filters to float, use defaults if conversion fails
    try:
        min_price_filter = float(min_price_filter)
    except (ValueError, TypeError):
        min_price_filter = min_price
        
    try:
        max_price_filter = float(max_price_filter)
    except (ValueError, TypeError):
        max_price_filter = max_price
    
    # Build the product filter query
    product_filters = Q(price__gte=min_price_filter, price__lte=max_price_filter)
    
    # Add search filter if provided
    if search_query:
        product_filters &= (
            Q(translations__name__icontains=search_query) | 
            Q(translations__description__icontains=search_query)
        )
    
    # Get current active language
    active_languages = get_active_language_choices()
    
    # First, get categories that have matching products (using a subquery)
    categories_with_products = Category.objects.filter(
        products__in=Product.objects.filter(product_filters)
    ).distinct()
    
    # Get all categories for the sidebar
    all_categories = Category.objects.prefetch_related('translations')
    
    # Then prefetch the filtered products for each category
    filtered_categories = list(categories_with_products.prefetch_related(
        # Prefetch translations for categories
        'translations',
        # Prefetch only the filtered products
        Prefetch(
            'products',
            queryset=Product.objects.filter(product_filters)
                                  .prefetch_related('translations')
                                  .distinct(),
            to_attr='filtered_products'
        )
    ))
    
    # Set up pagination - show 3 categories per page
    paginator = Paginator(filtered_categories, 3)
    page = request.GET.get('page', 1)
    
    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        categories = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        categories = paginator.page(paginator.num_pages)
    
    # Format prices to remove trailing zeros
    min_price_formatted = '{:.2f}'.format(min_price).rstrip('0').rstrip('.') if min_price % 1 == 0 else '{:.2f}'.format(min_price)
    max_price_formatted = '{:.2f}'.format(max_price).rstrip('0').rstrip('.') if max_price % 1 == 0 else '{:.2f}'.format(max_price)
    
    # Render the response
    response = render(request, 'products/products_page.html', {
        'categories': categories,
        'all_categories': all_categories,  # Pass all categories for the sidebar
        'paginator': paginator,
        'search_query': search_query,
        'min_price': min_price_formatted,
        'max_price': max_price_formatted,
        'min_price_filter': min_price_filter,
        'max_price_filter': max_price_filter
    })
    
    return response

def product_list(request, category_id):
    # Get category with translations and prefetch its products in a single query
    category = get_object_or_404(
        Category.objects.prefetch_related(
            'translations',
            Prefetch(
                'products',
                queryset=Product.objects.prefetch_related('translations')
            )
        ), 
        id=category_id
    )
    
    # Get all categories for the sidebar with counts to optimize sidebar rendering
    all_categories = Category.objects.prefetch_related('translations').annotate(product_count=Count('products'))
    
    # Render the response
    response = render(request, 'products/category_products.html', {
        'category': category,
        'products': category.products.all(),  # Use the prefetched products
        'all_categories': all_categories  # Pass all categories for the sidebar
    })
    
    return response
