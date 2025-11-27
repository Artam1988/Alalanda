from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Prefetch, Count, Case, When, IntegerField
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.core.paginator import Paginator
from django.utils.translation import get_language
from .models import Category, Product


@cache_page(60 * 15)
def products_page(request):
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)

    product_filters = Q()
    if search_query:
        product_filters &= Q(translations__name__icontains=search_query)

    top_names = [
        "PICKLES & OLIVES", "JAM", "OILS & SAUCES", "CANNED VEGETABLES & FRUITS",
        "MEAT", "POULTRY", "SEAFOOD", "DAIRY DERIVATIVES & EGGS",
        "FROZEN FOOD READY TO COOK", "SORTED FRUITS & VEGETABLES", "LEGUMES",
        "PASTA & RICE", "BAKING & PASTRY SUPPLIES", "SPICES", "NUTS",
        "DRIED FRUITS", "DRINKS", "OTHER PRODUCTS"
    ]

    current_language = get_language()

    all_categories = list(
        Category.objects.prefetch_related(
            Prefetch(
                'translations',
                queryset=Category._parler_meta.root_model.objects.filter(
                    language_code__in=[current_language, 'en']
                )
            )
        ).all()
    )

    top_cats = []
    other_cats = []
    for cat in all_categories:
        name_en = cat.safe_translation_getter('name', language_code='en', default='')
        if name_en in top_names:
            top_cats.append((top_names.index(name_en), cat))
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
        products_page_obj = paginator.get_page(page_number)

        return render(request, 'products/products_page.html', {
            'products': products_page_obj,
            'all_categories': all_categories_sorted,
            'search_query': search_query,
            'categories': None,
        })

    return render(request, 'products/products_page.html', {
        'categories': all_categories_sorted,
        'all_categories': all_categories_sorted,
        'search_query': search_query,
    })


@cache_page(60 * 15)
def product_list(request, category_id):
    search_query = request.GET.get('search', '')

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

    legumes_priority_names = [
        "Beans in Tomato Sauce", "Hummus", "Fava Beans", "Red Beans"
    ]
    oils_sauces_priority_names = [
        "Tomato Paste", "Pure Sunflower Oil 100%", "Spicy Red Pepper Sauce",
        "Extra Virgin Natural Olive Oil", "Chilled Red Pepper Sauce","Natural Pomegranate Molasses", "Butter", "Ghee"
    ]

    pickles_olives_lesss_priority_names = [
            "Garlic in Vinegar",
            "Pickled Cucumbers",
            "Greek Mixed Pickles",
            "Pickled Peppers",
            "Pickled Turnip",
            "Olives Stuffed with Pepper"
        ]

    products_qs = category.products.all()

    if search_query:
        products_qs = products_qs.filter(translations__name__icontains=search_query)

    category_name = category.safe_translation_getter('name', default='')

    if category_name.upper() == "LEGUMES":
        whens = [When(translations__name=name, then=pos) for pos, name in enumerate(legumes_priority_names)]
        prioritized_qs = products_qs.filter(translations__name__in=legumes_priority_names)
        prioritized_qs = prioritized_qs.annotate(
            priority=Case(*whens, default=len(legumes_priority_names), output_field=IntegerField())
        ).order_by('priority', 'id').distinct()
        rest_qs = products_qs.exclude(translations__name__in=legumes_priority_names)
        products_qs = list(prioritized_qs) + list(rest_qs)

    if category_name.upper() == "OILS & SAUCES":
        whens = [When(translations__name=name, then=pos) for pos, name in enumerate(oils_sauces_priority_names)]
        prioritized_qs = products_qs.filter(translations__name__in=oils_sauces_priority_names)
        prioritized_qs = prioritized_qs.annotate(
            priority=Case(*whens, default=len(oils_sauces_priority_names), output_field=IntegerField())
        ).order_by('priority', 'id').distinct()
        rest_qs = products_qs.exclude(translations__name__in=oils_sauces_priority_names)
        products_qs = list(prioritized_qs) + list(rest_qs)
    
    if category_name.upper() == "PICKLES & OLIVES":
        non_less_priority_qs = products_qs.exclude(translations__name__in=pickles_olives_lesss_priority_names)
        whens = [When(translations__name=name, then=pos) for pos, name in enumerate(pickles_olives_lesss_priority_names)]
        less_priority_qs = products_qs.filter(translations__name__in=pickles_olives_lesss_priority_names)
        less_priority_qs = less_priority_qs.annotate(
            priority=Case(*whens, default=len(pickles_olives_lesss_priority_names), output_field=IntegerField())
        ).order_by('priority', 'id').distinct()
        products_qs = list(non_less_priority_qs) + list(less_priority_qs)

    top_names = [
        "PICKLES & OLIVES", "JAM", "OILS & SAUCES", "CANNED VEGETABLES & FRUITS",
        "MEAT", "POULTRY", "SEAFOOD", "DAIRY DERIVATIVES & EGGS",
        "FROZEN FOOD READY TO COOK", "SORTED FRUITS & VEGETABLES", "LEGUMES",
        "PASTA & RICE", "BAKING & PASTRY SUPPLIES", "SPICES", "NUTS",
        "DRIED FRUITS", "DRINKS", "OTHER PRODUCTS"
    ]

    current_language = get_language()

    all_categories_qs = Category.objects.prefetch_related(
        Prefetch(
            'translations',
            queryset=Category._parler_meta.root_model.objects.filter(
                language_code__in=[current_language, 'en']
            )
        )
    ).annotate(product_count=Count('products'))

    all_categories = list(all_categories_qs)

    top_cats = []
    other_cats = []
    for cat in all_categories:
        name_en = cat.safe_translation_getter('name', language_code='en', default='')
        if name_en in top_names:
            top_cats.append((top_names.index(name_en), cat))
        else:
            other_cats.append(cat)

    top_cats.sort(key=lambda x: x[0])
    all_categories = [c for _, c in top_cats] + other_cats

    return render(request, 'products/category_products.html', {
        'category': category,
        'products': products_qs,
        'all_categories': all_categories,
        'search_query': search_query,
    })