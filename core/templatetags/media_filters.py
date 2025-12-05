import os
from urllib.parse import urlparse

from django import template
from django.conf import settings

register = template.Library()


def _candidate_variant(path: str, new_ext: str) -> str:
    base, _ = os.path.splitext(path)
    return base + new_ext


def _fs_exists_for_media(url_path: str) -> bool:

    media_url = settings.MEDIA_URL
    if not media_url:
        return False
    if not media_url.startswith('/'):
        media_url = '/' + media_url
    if not url_path.startswith('/'):
        url_path = '/' + url_path
    if not url_path.startswith(media_url):
        return False
    rel = url_path[len(media_url):].lstrip('/')
    fs_path = os.path.join(settings.MEDIA_ROOT, rel)
    return os.path.exists(fs_path)


@register.filter(name="webp_or_original")
def webp_or_original(url: str) -> str:

    if not url:
        return url
    try:
        parsed = urlparse(url)
        path = parsed.path if parsed.scheme in ("http", "https") else url
        media_url = settings.MEDIA_URL
        if not media_url:
            return url
        if not media_url.startswith('/'):
            media_url = '/' + media_url
        if not path.startswith('/'):
            path = '/' + path
        if not path.startswith(media_url):
            return url

        for ext in ('.avif', '.webp'):
            candidate_path = _candidate_variant(path, ext)
            rel = candidate_path[len(media_url):].lstrip('/')
            fs_path = os.path.join(settings.MEDIA_ROOT, rel)
            if os.path.exists(fs_path):
                if parsed.scheme in ("http", "https"):
                    return f"{parsed.scheme}://{parsed.netloc}{candidate_path}"
                return candidate_path
        return url
    except Exception:
        return url
