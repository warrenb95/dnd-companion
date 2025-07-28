"""
Utility functions for consistent error handling across the D&D Campaign Companion
"""
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import render
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)

def handle_form_errors(request, form, template_name=None, context=None):
    """
    Handle form validation errors consistently
    
    Args:
        request: The Django request object
        form: The form with errors
        template_name: Template to render for non-HTMX requests
        context: Additional context for template rendering
    
    Returns:
        JsonResponse for HTMX requests, rendered template for regular requests
    """
    errors = []
    
    # Collect all form errors
    for field, field_errors in form.errors.items():
        if field == '__all__':
            errors.extend(field_errors)
        else:
            field_label = form.fields.get(field, {}).get('label', field.replace('_', ' ').title())
            for error in field_errors:
                errors.append(f"{field_label}: {error}")
    
    error_message = "; ".join(errors) if errors else "Please correct the errors below."
    
    if request.headers.get('HX-Request'):
        # HTMX request - return JSON error
        return JsonResponse({
            'error': 'Validation error',
            'message': error_message,
            'type': 'validation_error',
            'field_errors': dict(form.errors)
        }, status=400)
    else:
        # Regular request - add message and re-render form
        messages.error(request, error_message)
        if template_name:
            ctx = context or {}
            ctx['form'] = form
            return render(request, template_name, ctx, status=400)
        return None

def handle_permission_error(request, message="You do not have permission to perform this action."):
    """
    Handle permission denied errors consistently
    
    Args:
        request: The Django request object
        message: Custom error message
    
    Returns:
        JsonResponse for HTMX requests, rendered 403 template for regular requests
    """
    logger.warning(f"Permission denied: {message} - User: {request.user} - URL: {request.get_full_path()}")
    
    if request.headers.get('HX-Request'):
        return JsonResponse({
            'error': 'Permission denied',
            'message': message,
            'type': 'permission_denied'
        }, status=403)
    else:
        messages.error(request, message)
        return render(request, '403.html', status=403)

def handle_not_found_error(request, message="The requested item was not found."):
    """
    Handle not found errors consistently
    
    Args:
        request: The Django request object
        message: Custom error message
    
    Returns:
        JsonResponse for HTMX requests, rendered 404 template for regular requests
    """
    logger.warning(f"Not found: {message} - User: {request.user} - URL: {request.get_full_path()}")
    
    if request.headers.get('HX-Request'):
        return JsonResponse({
            'error': 'Not found',
            'message': message,
            'type': 'not_found'
        }, status=404)
    else:
        messages.error(request, message)
        return render(request, '404.html', status=404)

def handle_server_error(request, exception=None, message="An unexpected error occurred."):
    """
    Handle server errors consistently
    
    Args:
        request: The Django request object
        exception: The exception that occurred (optional)
        message: Custom error message
    
    Returns:
        JsonResponse for HTMX requests, rendered 500 template for regular requests
    """
    if exception:
        logger.error(f"Server error: {message} - Exception: {str(exception)} - User: {request.user} - URL: {request.get_full_path()}")
    else:
        logger.error(f"Server error: {message} - User: {request.user} - URL: {request.get_full_path()}")
    
    if request.headers.get('HX-Request'):
        return JsonResponse({
            'error': 'Server error',
            'message': message,
            'type': 'server_error'
        }, status=500)
    else:
        messages.error(request, message)
        return render(request, '500.html', status=500)

def success_response(request, message, redirect_url=None, template_name=None, context=None):
    """
    Handle successful operations consistently
    
    Args:
        request: The Django request object
        message: Success message
        redirect_url: URL to redirect to (optional)
        template_name: Template to render (optional)
        context: Template context (optional)
    
    Returns:
        JsonResponse for HTMX requests with appropriate response
    """
    if request.headers.get('HX-Request'):
        response_data = {
            'success': True,
            'message': message,
            'type': 'success'
        }
        
        if redirect_url:
            response_data['redirect'] = redirect_url
        elif template_name:
            ctx = context or {}
            response_data['html'] = render_to_string(template_name, ctx, request=request)
        
        return JsonResponse(response_data)
    else:
        messages.success(request, message)
        return None

def add_error_context(context, error_type=None, error_message=None):
    """
    Add error context to template context
    
    Args:
        context: Existing template context dict
        error_type: Type of error ('validation', 'permission', 'not_found', 'server')
        error_message: Error message to display
    
    Returns:
        Updated context dict
    """
    if error_type or error_message:
        context['error'] = {
            'type': error_type,
            'message': error_message
        }
    return context