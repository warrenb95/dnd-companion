"""
HTMX-specific views for dynamic content updates
"""
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.forms import modelformset_factory
from .models import Campaign, Encounter
from .forms import EncounterForm

@login_required
@require_http_methods(["POST"])
def add_encounter_form(request, campaign_id):
    """
    Add a new encounter form to the chapter creation form
    """
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    
    # Get the current form count from the request
    form_count = int(request.POST.get('form_count', 0))
    
    # Create a new empty encounter form
    encounter_form = EncounterForm(prefix=f'encounters-{form_count}')
    
    context = {
        'form': encounter_form,
        'form_index': form_count,
        'encounter_number': form_count + 1,
        'can_remove': True  # New forms can always be removed
    }
    
    html = render_to_string('chapters/components/_encounter_form.html', context, request=request)
    
    # Return the HTML with a header to update the total forms count
    response = HttpResponse(html)
    response['HX-Trigger'] = f'updateFormCount:{form_count + 1}'
    return response

@login_required
@require_http_methods(["DELETE"])
def remove_encounter_form(request, form_index):
    """
    Remove an encounter form from the chapter creation form
    """
    # Return empty content to remove the form
    response = HttpResponse('')
    response['HX-Trigger'] = f'formRemoved:{form_index}'
    return response

@login_required 
@require_http_methods(["GET"])
def get_empty_encounter_form(request, campaign_id):
    """
    Get an empty encounter form template for dynamic addition
    """
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    form_count = int(request.GET.get('count', 0))
    
    encounter_form = EncounterForm(prefix=f'encounters-{form_count}')
    
    context = {
        'form': encounter_form,
        'form_index': form_count,
        'encounter_number': form_count + 1,
        'can_remove': True
    }
    
    return render(request, 'chapters/components/_encounter_form.html', context)

@login_required
@require_http_methods(["POST"])
def dismiss_notification(request, notification_id):
    """
    Dismiss a notification (for HTMX-based notifications)
    """
    # Return empty content to remove the notification
    return HttpResponse('')

@login_required
@require_http_methods(["GET"])
def refresh_campaign_detail(request, campaign_id):
    """
    Refresh campaign detail content after successful operations
    """
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    
    # Check if this is a partial refresh request
    refresh_section = request.GET.get('section', 'full')
    
    if refresh_section == 'codm_list':
        # Just refresh the Co-DM list section
        context = {
            'campaign': campaign,
            'is_owner': True
        }
        return render(request, 'campaigns/components/_codm_list.html', context)
    else:
        # Full page refresh
        return render(request, 'campaigns/campaign_detail.html', {
            'campaign': campaign,
            'is_owner': True
        })