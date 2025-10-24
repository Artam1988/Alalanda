from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.static import serve
from django.http import HttpResponse
from core.views import about_page, home_page, contact_page, brands_page
import os


def robots_txt(request):
    for static_dir in settings.STATICFILES_DIRS:
        robots_path = os.path.join(static_dir, 'robots.txt')
        if os.path.exists(robots_path):
            with open(robots_path, 'r') as f:
                return HttpResponse(f.read(), content_type='text/plain')

    robots_path = os.path.join(settings.STATIC_ROOT, 'robots.txt')
    if os.path.exists(robots_path):
        with open(robots_path, 'r') as f:
            return HttpResponse(f.read(), content_type='text/plain')

    fallback_content = "User-agent: *\nDisallow: /admin/\n"
    return HttpResponse(fallback_content, content_type='text/plain')


urlpatterns = [
    path('', home_page, name='home'),  # Set home page as the default landing page
    path('admin/', admin.site.urls),
    path('products/', include('products.urls', namespace='products')),
    path('i18n/', include('django.conf.urls.i18n')),  # For language switcher
    path('about/', about_page, name='about'),
    path('contact/', contact_page, name='contact'),
    path('brands/', brands_page, name='brands'),
    path('robots.txt', robots_txt, name='robots_txt'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)