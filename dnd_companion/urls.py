"""
URL configuration for dnd_companion project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache

from dnd_companion import settings

@csrf_exempt
@never_cache
def health_check(request):
    return HttpResponse("OK", content_type="text/plain")

urlpatterns = [
    path("health", health_check, name="health"),  # Remove trailing slash
    path("health/", health_check, name="health_slash"),  # Keep both versions
    path("admin/", admin.site.urls),
    path("", include("campaigns.urls", namespace="campaigns")),
]

# Serve media files in development and production
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

