import logging
import traceback
from django.http import JsonResponse, HttpResponseServerError
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.conf import settings

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    """
    Centralized error handling middleware for the D&D Campaign Companion
    Provides consistent error responses and logging
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Process exceptions that occur during request processing
        """
        # Get user info for logging
        user_info = f"User: {request.user}" if request.user.is_authenticated else "Anonymous"
        
        # Log the exception with context
        logger.error(
            f"Exception in view: {exception.__class__.__name__}: {str(exception)}\n"
            f"URL: {request.get_full_path()}\n"
            f"{user_info}\n"
            f"Traceback: {traceback.format_exc()}"
        )

        # Handle different types of exceptions
        if isinstance(exception, PermissionDenied):
            return self._handle_permission_denied(request, exception)
        elif isinstance(exception, ValidationError):
            return self._handle_validation_error(request, exception)
        else:
            return self._handle_server_error(request, exception)

    def _handle_permission_denied(self, request, exception):
        """Handle 403 Permission Denied errors"""
        if request.headers.get('HX-Request'):
            # HTMX request - return partial response
            return JsonResponse({
                'error': 'Access denied',
                'message': 'You do not have permission to perform this action.',
                'type': 'permission_denied'
            }, status=403)
        
        # Regular request - show error page
        return render(request, '403.html', status=403)

    def _handle_validation_error(self, request, exception):
        """Handle validation errors with user-friendly messages"""
        error_message = str(exception)
        
        if request.headers.get('HX-Request'):
            # HTMX request - return error response
            return JsonResponse({
                'error': 'Validation error',
                'message': error_message,
                'type': 'validation_error'
            }, status=400)
        
        # Regular request - add message and show 400 page
        messages.error(request, f"Invalid data: {error_message}")
        return render(request, '400.html', status=400)

    def _handle_server_error(self, request, exception):
        """Handle 500 server errors"""
        # In production, don't expose internal error details
        if settings.DEBUG:
            error_details = str(exception)
        else:
            error_details = "An unexpected error occurred. Please try again later."
        
        if request.headers.get('HX-Request'):
            # HTMX request - return JSON error
            return JsonResponse({
                'error': 'Server error',
                'message': error_details,
                'type': 'server_error'
            }, status=500)
        
        # Regular request - show error page
        return render(request, '500.html', status=500)


class UserFriendlyErrorMiddleware:
    """
    Middleware to enhance error messages and provide better user experience
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add helpful headers for debugging in development
        if settings.DEBUG and hasattr(response, 'status_code'):
            if response.status_code >= 400:
                response['X-Debug-Error'] = f"Status: {response.status_code}"
                
        return response