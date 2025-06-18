from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch, Count
from django.views.decorators.cache import cache_page
from django.utils.cache import get_cache_key, learn_cache_key, patch_response_headers
from django.core.cache import cache
from parler.utils import get_active_language_choices
from .models import Category, Product

def products_page(request):
    # Get search parameters
    search_query = request.GET.get('search', '')
    
    # Build the product filter query (no price filter)
    product_filters = Q()
    
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
    
    # Render the response
    response = render(request, 'products/products_page.html', {
        'categories': categories,
        'all_categories': all_categories,  # Pass all categories for the sidebar
        'paginator': paginator,
        'search_query': search_query,
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

