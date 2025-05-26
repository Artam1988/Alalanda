from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from products.models import Product, Category
from .models import ContactMessage, EmploymentApplication

# Create your views here.
def about_page(request):
    """View for the about page"""
    return render(request, 'about.html')

def home_page(request):
    """View for the home page"""
    
    # Get all featured products first
    featured_products = Product.objects.filter(is_featured=True)
    
    # Get the current language
    current_language = request.LANGUAGE_CODE
    
    # Get products with translations in the current language
    # We're using prefetch_related to optimize the query and ensure all translations are loaded
    featured_products = featured_products.prefetch_related('translations')
    
    # Create a list to store products with translations in the current language
    translated_products = []
    
    # Manually check each product for a translation in the current language
    for product in featured_products:
        if product.has_translation(current_language):
            translated_products.append(product)
    
    context = {
        'featured_products': translated_products,
        'featured_count': len(translated_products)  # Add count for JavaScript
    }
    return render(request, 'home.html', context)

def contact_page(request):
    """View for the contact page"""
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'contact':
            # Handle contact form submission
            try:
                contact = ContactMessage(
                    name=request.POST.get('name'),
                    email=request.POST.get('email'),
                    phone=request.POST.get('phone', ''),
                    subject=request.POST.get('subject'),
                    message=request.POST.get('message')
                )
                contact.save()
                messages.success(request, _('Your message has been sent successfully. We will get back to you soon.'))
                return redirect('contact')
            except Exception as e:
                messages.error(request, _('There was an error sending your message. Please try again.'))
        
        elif form_type == 'employment':
            # Handle employment application submission
            try:
                if 'resume' in request.FILES:
                    application = EmploymentApplication(
                        name=request.POST.get('name'),
                        email=request.POST.get('email'),
                        phone=request.POST.get('phone'),
                        position=request.POST.get('position'),
                        experience=request.POST.get('experience'),
                        resume=request.FILES['resume'],
                        cover_letter=request.POST.get('cover_letter', '')
                    )
                    application.save()
                    messages.success(request, _('Your application has been submitted successfully. We will review it and contact you if there is a match.'))
                    return redirect('contact')
                else:
                    messages.error(request, _('Please upload your resume.'))
            except Exception as e:
                messages.error(request, _('There was an error submitting your application. Please try again.'))
    
    return render(request, 'contact.html')

def brands_page(request):
    """View for the brands page"""
    # Get all categories to potentially link to product pages
    categories = Category.objects.all().prefetch_related('translations')
    
    # Create a list to store categories with translations in the current language
    translated_categories = []
    current_language = request.LANGUAGE_CODE
    
    # Manually check each category for a translation in the current language
    for category in categories:
        if hasattr(category, 'has_translation') and category.has_translation(current_language):
            translated_categories.append(category)
    
    context = {
        'categories': translated_categories
    }
    return render(request, 'brands.html', context)
