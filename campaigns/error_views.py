from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden
import logging

logger = logging.getLogger(__name__)

def custom_404_view(request, exception=None):
    """
    Custom 404 error view with D&D theming
    """
    logger.warning(f"404 error for URL: {request.get_full_path()} - User: {request.user}")
    return HttpResponseNotFound(render(request, '404.html'))

def custom_500_view(request):
    """
    Custom 500 error view with D&D theming
    """
    logger.error(f"500 error for URL: {request.get_full_path()} - User: {request.user}")
    return HttpResponseServerError(render(request, '500.html'))

def custom_403_view(request, exception=None):
    """
    Custom 403 error view with D&D theming
    """
    logger.warning(f"403 error for URL: {request.get_full_path()} - User: {request.user}")
    return HttpResponseForbidden(render(request, '403.html'))

def custom_400_view(request, exception=None):
    """
    Custom 400 error view with D&D theming (Bad Request)
    """
    logger.warning(f"400 error for URL: {request.get_full_path()} - User: {request.user}")
    return render(request, '400.html', status=400)