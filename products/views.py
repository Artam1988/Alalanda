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
    page = request.GET.get('page', 1)

    # Build the product filter query (no price filter)
    product_filters = Q()

    # Add search filter if provided
    if search_query:
        product_filters &= (
            Q(translations__name__icontains=search_query)
        )

    # Get current active language
    active_languages = get_active_language_choices()

    # Get all categories for the sidebar
    all_categories = Category.objects.prefetch_related('translations')

    if search_query:
        # If searching, show products, not categories
        products = Product.objects.filter(product_filters).prefetch_related('translations', 'category').distinct()
        paginator = Paginator(products, 12)  # Show 12 products per page
        try:
            products_page_obj = paginator.page(page)
        except PageNotAnInteger:
            products_page_obj = paginator.page(1)
        except EmptyPage:
            products_page_obj = paginator.page(paginator.num_pages)
        response = render(request, 'products/products_page.html', {
            'products': products_page_obj,
            'all_categories': all_categories,
            'paginator': paginator,
            'search_query': search_query,
            'categories': None,  # No categories in search mode
        })
        return response
    else:
        # First, get categories that have matching products (using a subquery)
        categories_with_products = Category.objects.filter(
            products__in=Product.objects.filter(product_filters)
        ).distinct()

        # Then prefetch the filtered products for each category
        filtered_categories = list(categories_with_products.prefetch_related(
            'translations',
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
        try:
            categories = paginator.page(page)
        except PageNotAnInteger:
            categories = paginator.page(1)
        except EmptyPage:
            categories = paginator.page(paginator.num_pages)
        response = render(request, 'products/products_page.html', {
            'categories': categories,
            'all_categories': all_categories,
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

