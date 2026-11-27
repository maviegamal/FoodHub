from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from core.views import index

urlpatterns = [
    path("", index, name="index"),
    path("api/", include("accounts.urls")),
    path("api/", include("menu.urls")),
    path("api/", include("orders.urls")),
]

# Local only: serve uploaded food images.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)