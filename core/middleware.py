import time
from django.conf import settings
from django.utils.http import http_date


class MediaCacheControlMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_age = 60 * 60 * 24 * 30

    def __call__(self, request):
        response = self.get_response(request)

        media_url = getattr(settings, 'MEDIA_URL', None)
        if not media_url:
            return response

        if not media_url.startswith('/'):
            media_url = '/' + media_url

        path = request.path or ''
        if path.startswith(media_url):
            if 'Cache-Control' not in response:
                response['Cache-Control'] = f'public, max-age={self.max_age}'
            if 'Expires' not in response:
                response['Expires'] = http_date(time.time() + self.max_age)
        return response
