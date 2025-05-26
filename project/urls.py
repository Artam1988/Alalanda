from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from core.views import about_page, home_page, contact_page, brands_page

urlpatterns = [
    path('', home_page, name='home'),  # Set home page as the default landing page
    path('admin/', admin.site.urls),
    path('products/', include('products.urls', namespace='products')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('i18n/', include('django.conf.urls.i18n')),  # For language switcher
    path('about/', about_page, name='about'),
    path('contact/', contact_page, name='contact'),
    path('brands/', brands_page, name='brands'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)