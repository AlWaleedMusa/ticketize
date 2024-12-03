from django.contrib import admin
from django.urls import path, include
from debug_toolbar import urls as debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # django allauth
    path("accounts/", include("allauth.urls")),
    # reload browser
    path("__reload__/", include("django_browser_reload.urls")),
    # apps
    path("", include("events.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]

# Add debug toolbar urls
if settings.DEBUG:
    urlpatterns += [path("__debug__/", include(debug_toolbar_urls))]
