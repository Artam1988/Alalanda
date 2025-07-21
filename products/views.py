from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
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
            Q(translations__name__icontains=search_query)
        )

    # Get current active language
    active_languages = get_active_language_choices()

    # Get all categories for the sidebar, with Pickles And Olives and Jam on top
    top_names = ["Pickles And Olives", "Jam", "POULTRY", "OTHER", "MEAT"]
    top_categories = list(Category.objects.prefetch_related('translations').filter(translations__name__in=top_names).distinct())
    other_categories = Category.objects.prefetch_related('translations').exclude(translations__name__in=top_names)
    all_categories = top_categories + list(other_categories)

    if search_query:
        # If searching, show products, not categories
        products = Product.objects.filter(product_filters).prefetch_related('translations', 'category').distinct()
        response = render(request, 'products/products_page.html', {
            'products': products,
            'all_categories': all_categories,
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
        filtered_top = list(categories_with_products.filter(translations__name__in=top_names).prefetch_related(
            'translations',
            Prefetch(
                'products',
                queryset=Product.objects.filter(product_filters)
                                      .prefetch_related('translations')
                                      .distinct(),
                to_attr='filtered_products'
            )
        ))
        filtered_others = list(categories_with_products.exclude(translations__name__in=top_names).prefetch_related(
            'translations',
            Prefetch(
                'products',
                queryset=Product.objects.filter(product_filters)
                                      .prefetch_related('translations')
                                      .distinct(),
                to_attr='filtered_products'
            )
        ))
        filtered_categories = filtered_top + filtered_others

        response = render(request, 'products/products_page.html', {
            'categories': filtered_categories,
            'all_categories': all_categories,
            'search_query': search_query,
        })
        return response

def product_list(request, category_id):
    # Get search query
    search_query = request.GET.get('search', '')

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

    # Filter products by search query if provided
    products_qs = category.products.all()
    if search_query:
        products_qs = products_qs.filter(translations__name__icontains=search_query)

    # Get all categories for the sidebar with counts to optimize sidebar rendering
    all_categories = Category.objects.prefetch_related('translations').annotate(product_count=Count('products'))

    # Render the response without pagination
    response = render(request, 'products/category_products.html', {
        'category': category,
        'products': products_qs,  # All products, not paginated
        'all_categories': all_categories,  # Pass all categories for the sidebar
        'search_query': search_query,
    })
    return response

