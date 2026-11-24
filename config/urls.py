from pathlib import Path
import json
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def route_manifest(request):
    manifest = Path(settings.BASE_DIR) / "public" / "manus-routes.json"
    return JsonResponse(json.loads(manifest.read_text(encoding="utf-8")))


urlpatterns = [
    path("admin/", admin.site.urls),
    path("manus-routes.json", route_manifest, name="route_manifest"),
    path("", include("social.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
