from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Prefetch, Count
from django.views.decorators.cache import cache_page
from django.utils.cache import get_cache_key, learn_cache_key, patch_response_headers
from django.core.cache import cache
from parler.utils import get_active_language_choices
from .models import Category, Product
from django.core.paginator import Paginator
from django.utils.translation import get_language

def products_page(request):
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)
    
    product_filters = Q()
    if search_query:
        product_filters &= Q(translations__name__icontains=search_query)

    top_names = ["Pickles And Olives", "Jam", "OTHER", "POULTRY", "MEAT"]
    
    current_language = get_language()
    
    all_categories = list(
        Category.objects
        .prefetch_related(
            Prefetch(
                'translations',
                queryset=Category._parler_meta.root_model.objects.filter(
                    language_code=current_language
                )
            )
        )
        .all()
    )
    
    top_cats = []
    other_cats = []
    for cat in all_categories:
        name = cat.safe_translation_getter('name', default='')
        if name in top_names:
            top_cats.append((top_names.index(name), cat))
        else:
            other_cats.append(cat)
    
    top_cats.sort(key=lambda x: x[0])
    all_categories_sorted = [c for _, c in top_cats] + other_cats

    if search_query:
        products_qs = (
            Product.objects
            .filter(product_filters)
            .select_related('category')
            .prefetch_related(
                Prefetch(
                    'translations',
                    queryset=Product._parler_meta.root_model.objects.filter(
                        language_code=current_language
                    )
                ),
                Prefetch(
                    'category__translations',
                    queryset=Category._parler_meta.root_model.objects.filter(
                        language_code=current_language
                    )
                )
            )
            .distinct()
        )
        
        paginator = Paginator(products_qs, 24)
        products_page = paginator.get_page(page_number)
        
        return render(request, 'products/products_page.html', {
            'products': products_page,
            'all_categories': all_categories_sorted,
            'search_query': search_query,
            'categories': None,
        })
    else:
        # Category view mode - use all_categories_sorted for both sidebar and main content
        return render(request, 'products/products_page.html', {
            'categories': all_categories_sorted,
            'all_categories': all_categories_sorted,
            'search_query': search_query,
        })

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


    # Custom ordering for LEGUMES category
    legumes_priority_names = [
        "Beans in Tomato Sauce",
        "Hummus",
        "Fava beans",
        "Red Beans"
    ]
    Oils_and_Sauces_priority_names = [
        "Tomato Paste",
        "Pure sunflower oil",
        "Hot Red Pepper Sauce",
        "Natural Olive Oil First Pressing",
        "Cold Red Pepper Sauce",
    ]
    products_qs = category.products.all()
    if search_query:
        products_qs = products_qs.filter(translations__name__icontains=search_query)

    # If category is LEGUMES, order products as requested
    category_name = category.safe_translation_getter('name', default='')
    if category_name.upper() == "LEGUMES":
        # Annotate each product with a priority value
        from django.db.models import Case, When, IntegerField
        whens = [When(translations__name=name, then=pos) for pos, name in enumerate(legumes_priority_names)]
        # Get the prioritized products
        prioritized_qs = products_qs.filter(translations__name__in=legumes_priority_names)
        prioritized_qs = prioritized_qs.annotate(
            priority=Case(*whens, default=len(legumes_priority_names), output_field=IntegerField())
        ).order_by('priority', 'id').distinct()
        # Get the rest of the products, excluding the prioritized ones
        rest_qs = products_qs.exclude(translations__name__in=legumes_priority_names)
        products_qs = list(prioritized_qs) + list(rest_qs)
    if category_name.upper() == "OILS AND SAUCES":
        # Annotate each product with a priority value   
        from django.db.models import Case, When, IntegerField
        whens = [When(translations__name=name, then=pos) for pos, name in enumerate(Oils_and_Sauces_priority_names)]
        # Get the prioritized products
        prioritized_qs = products_qs.filter(translations__name__in=Oils_and_Sauces_priority_names)
        prioritized_qs = prioritized_qs.annotate(
            priority=Case(*whens, default=len(Oils_and_Sauces_priority_names), output_field=IntegerField())
        ).order_by('priority', 'id').distinct()
        # Get the rest of the products, excluding the prioritized ones
        rest_qs = products_qs.exclude(translations__name__in=Oils_and_Sauces_priority_names)
        products_qs = list(prioritized_qs) + list(rest_qs)
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

