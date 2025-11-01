"""
HTMX-specific views for dynamic content updates
"""
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.forms import modelformset_factory
from .models import Campaign, Encounter, Chapter, NPC, Enemy, Location, SessionSchedule, PlayerAvailability
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


@login_required
@require_http_methods(["GET"])
def chapter_npc_selection(request, campaign_id, chapter_id):
    """
    Get available NPCs for selection to add to a chapter
    """
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    chapter = get_object_or_404(Chapter, id=chapter_id, campaign=campaign)
    
    # Get all NPCs in the campaign that are not already in this chapter
    available_npcs = campaign.npcs.exclude(chapters=chapter)
    
    context = {
        'campaign': campaign,
        'chapter': chapter,
        'available_npcs': available_npcs
    }
    
    return render(request, 'chapters/components/_npc_selection.html', context)


@login_required
@require_http_methods(["POST"])
def chapter_add_npc(request, campaign_id, chapter_id):
    """
    Add an NPC to a chapter
    """
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    chapter = get_object_or_404(Chapter, id=chapter_id, campaign=campaign)
    
    npc_id = request.POST.get('npc_id')
    if npc_id:
        npc = get_object_or_404(NPC, id=npc_id, campaign=campaign)
        chapter.involved_npcs.add(npc)
    
    # Return the updated NPCs section
    context = {
        'chapter': chapter
    }
    
    return render(request, 'chapters/components/_npcs_section.html', context)


@login_required
@require_http_methods(["POST"])
def chapter_remove_npc(request, campaign_id, chapter_id):
    """
    Remove an NPC from a chapter
    """
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    chapter = get_object_or_404(Chapter, id=chapter_id, campaign=campaign)
    
    npc_id = request.POST.get('npc_id')
    if npc_id:
        npc = get_object_or_404(NPC, id=npc_id, campaign=campaign)
        chapter.involved_npcs.remove(npc)
    
    # Return the updated NPCs section
    context = {
        'chapter': chapter
    }
    
    return render(request, 'chapters/components/_npcs_section.html', context)


@login_required
@require_http_methods(["GET"])
def chapter_location_selection(request, campaign_id, chapter_id):
    """
    Get available locations for selection to add to a chapter
    """
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    chapter = get_object_or_404(Chapter, id=chapter_id, campaign=campaign)
    
    # Get all locations in the campaign that are not already in this chapter
    available_locations = campaign.locations.exclude(chapters=chapter)
    
    context = {
        'campaign': campaign,
        'chapter': chapter,
        'available_locations': available_locations
    }
    
    return render(request, 'chapters/components/_location_selection.html', context)


@login_required
@require_http_methods(["POST"])
def chapter_add_location(request, campaign_id, chapter_id):
    """
    Add a location to a chapter
    """
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    chapter = get_object_or_404(Chapter, id=chapter_id, campaign=campaign)
    
    location_id = request.POST.get('location_id')
    if location_id:
        location = get_object_or_404(Location, id=location_id, campaign=campaign)
        chapter.involved_locations.add(location)
    
    # Return the updated locations section
    context = {
        'chapter': chapter
    }
    
    return render(request, 'chapters/components/_locations_section.html', context)


@login_required
@require_http_methods(["GET"])
def encounter_enemy_selection(request, campaign_id, encounter_id):
    """
    Get available enemies for selection to add to an encounter
    """
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    encounter = get_object_or_404(Encounter, id=encounter_id, chapter__campaign=campaign)
    
    # Get all enemies in the campaign that are not already in this encounter
    available_enemies = campaign.enemies.exclude(encounters=encounter)
    
    context = {
        'campaign': campaign,
        'encounter': encounter,
        'available_enemies': available_enemies
    }
    
    return render(request, 'encounters/components/_enemy_selection.html', context)


@login_required
@require_http_methods(["POST"])
def encounter_add_enemy(request, campaign_id, encounter_id):
    """
    Add an enemy to an encounter
    """
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    encounter = get_object_or_404(Encounter, id=encounter_id, chapter__campaign=campaign)
    
    enemy_id = request.POST.get('enemy_id')
    if enemy_id:
        enemy = get_object_or_404(Enemy, id=enemy_id, campaign=campaign)
        encounter.enemies.add(enemy)
    
    # Return the updated enemies section
    context = {
        'encounter': encounter
    }
    
    return render(request, 'encounters/components/_enemies_section.html', context)


@login_required
@require_http_methods(["POST"])
def encounter_remove_enemy(request, campaign_id, encounter_id):
    """
    Remove an enemy from an encounter
    """
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    encounter = get_object_or_404(Encounter, id=encounter_id, chapter__campaign=campaign)
    
    enemy_id = request.POST.get('enemy_id')
    if enemy_id:
        enemy = get_object_or_404(Enemy, id=enemy_id, campaign=campaign)
        encounter.enemies.remove(enemy)
    
    # Return the updated enemies section
    context = {
        'encounter': encounter
    }
    
    return render(request, 'encounters/components/_enemies_section.html', context)


@login_required
@require_http_methods(["POST"])
def chapter_remove_location(request, campaign_id, chapter_id):
    """
    Remove a location from a chapter
    """
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    chapter = get_object_or_404(Chapter, id=chapter_id, campaign=campaign)
    
    location_id = request.POST.get('location_id')
    if location_id:
        location = get_object_or_404(Location, id=location_id, campaign=campaign)
        chapter.involved_locations.remove(location)
    
    # Return the updated locations section
    context = {
        'chapter': chapter
    }
    
    return render(request, 'chapters/components/_locations_section.html', context)


@login_required
@require_http_methods(["GET"])
def chapter_enemy_selection(request, campaign_id, chapter_id):
    """
    Get available enemies for selection to add to a chapter
    """
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    chapter = get_object_or_404(Chapter, id=chapter_id, campaign=campaign)
    
    # Get all enemies in the campaign that are not already in this chapter
    available_enemies = campaign.enemies.exclude(chapters=chapter)
    
    context = {
        'campaign': campaign,
        'chapter': chapter,
        'available_enemies': available_enemies
    }
    
    return render(request, 'chapters/components/_enemy_selection.html', context)


@login_required
@require_http_methods(["POST"])
def chapter_add_enemy(request, campaign_id, chapter_id):
    """
    Add an enemy to a chapter
    """
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    chapter = get_object_or_404(Chapter, id=chapter_id, campaign=campaign)
    
    enemy_id = request.POST.get('enemy_id')
    if enemy_id:
        enemy = get_object_or_404(Enemy, id=enemy_id, campaign=campaign)
        chapter.involved_enemies.add(enemy)
    
    # Return the updated enemies section
    context = {
        'chapter': chapter
    }
    
    return render(request, 'chapters/components/_enemies_section.html', context)


@login_required
@require_http_methods(["POST"])
def chapter_remove_enemy(request, campaign_id, chapter_id):
    """
    Remove an enemy from a chapter
    """
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    chapter = get_object_or_404(Chapter, id=chapter_id, campaign=campaign)
    
    enemy_id = request.POST.get('enemy_id')
    if enemy_id:
        enemy = get_object_or_404(Enemy, id=enemy_id, campaign=campaign)
        chapter.involved_enemies.remove(enemy)
    
    # Return the updated enemies section
    context = {
        'chapter': chapter
    }
    
    return render(request, 'chapters/components/_enemies_section.html', context)


@login_required
@require_http_methods(["GET"])
def encounter_enemy_selection(request, campaign_id, encounter_id):
    """
    Get available enemies for selection to add to an encounter
    """
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    encounter = get_object_or_404(Encounter, id=encounter_id, chapter__campaign=campaign)
    
    # Get all enemies in the campaign that are not already in this encounter
    available_enemies = campaign.enemies.exclude(encounters=encounter)
    
    context = {
        'campaign': campaign,
        'encounter': encounter,
        'available_enemies': available_enemies
    }
    
    return render(request, 'encounters/components/_enemy_selection.html', context)


@login_required
@require_http_methods(["POST"])
def encounter_add_enemy(request, campaign_id, encounter_id):
    """
    Add an enemy to an encounter
    """
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    encounter = get_object_or_404(Encounter, id=encounter_id, chapter__campaign=campaign)
    
    enemy_id = request.POST.get('enemy_id')
    if enemy_id:
        enemy = get_object_or_404(Enemy, id=enemy_id, campaign=campaign)
        encounter.enemies.add(enemy)
    
    # Return the updated enemies section
    context = {
        'encounter': encounter
    }
    
    return render(request, 'encounters/components/_enemies_section.html', context)


@login_required
@require_http_methods(["POST"])
def encounter_remove_enemy(request, campaign_id, encounter_id):
    """
    Remove an enemy from an encounter
    """
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    encounter = get_object_or_404(Encounter, id=encounter_id, chapter__campaign=campaign)
    
    enemy_id = request.POST.get('enemy_id')
    if enemy_id:
        enemy = get_object_or_404(Enemy, id=enemy_id, campaign=campaign)
        encounter.enemies.remove(enemy)
    
    # Return the updated enemies section
    context = {
        'encounter': encounter
    }
    
    return render(request, 'encounters/components/_enemies_section.html', context)

# Session Scheduling HTMX Views (Public - No login required)

@require_http_methods(["POST"])
def toggle_time_slot(request, token):
    """
    Toggle a time slot selection for player availability (HTMX endpoint)
    """
    schedule = get_object_or_404(SessionSchedule, shareable_token=token)
    
    # Ensure the schedule is still collecting responses
    if schedule.status != "collecting":
        return HttpResponse('<span class="text-danger">This poll is closed.</span>')
    
    date = request.POST.get('date')
    time_slot = request.POST.get('time_slot')
    email = request.POST.get('email', '').strip()
    player_name = request.POST.get('player_name', '').strip()

    # Basic validation
    if not email or not date or not time_slot:
        # Return the button with error state instead of replacing it
        context = {
            'time_slot': time_slot,
            'date_str': date,
            'selected': False,
            'token': token,
            'email': email,
            'player_name': player_name,
            'show_error': True,
            'error_message': 'Please enter your email first'
        }
        return render(request, 'sessions/components/_time_slot_button.html', context)
    
    # Get or create player availability
    availability, created = PlayerAvailability.objects.get_or_create(
        session_schedule=schedule,
        email=email,
        defaults={'player_name': player_name if player_name else 'Anonymous'}
    )
    
    # Update player name if provided and record exists
    if not created and player_name:
        availability.player_name = player_name
        availability.save()
    
    # Toggle the time slot
    date_availability = availability.get_availability_for_date(date)
    is_selected = time_slot in date_availability
    
    if is_selected:
        date_availability.remove(time_slot)
    else:
        date_availability.append(time_slot)
    
    availability.set_availability_for_date(date, date_availability)
    availability.save()
    
    # Return updated button HTML
    context = {
        'time_slot': time_slot,
        'date_str': date,  # Fixed: use date_str to match template
        'selected': not is_selected,  # Toggled state
        'token': token,
        'email': email,
        'player_name': player_name
    }

    return render(request, 'sessions/components/_time_slot_button.html', context)


@require_http_methods(["POST"])
def save_player_info(request, token):
    """
    Save/update player info (triggered on blur of name/email fields)
    """
    schedule = get_object_or_404(SessionSchedule, shareable_token=token)
    
    email = request.POST.get('email', '').strip()
    player_name = request.POST.get('player_name', '').strip()
    character_name = request.POST.get('character_name', '').strip()
    
    if not email:
        return HttpResponse('')  # Empty response if no email
    
    # Get or create player availability
    availability, created = PlayerAvailability.objects.get_or_create(
        session_schedule=schedule,
        email=email,
        defaults={
            'player_name': player_name if player_name else 'Anonymous',
            'character_name': character_name
        }
    )
    
    # Update if exists
    if not created:
        if player_name:
            availability.player_name = player_name
        if character_name is not None:  # Allow clearing character name
            availability.character_name = character_name
        availability.save()
    
    # Return success indicator (could be a small checkmark or empty)
    return HttpResponse('')


@require_http_methods(["POST"])
def submit_player_availability(request, token):
    """
    Final submission of player availability
    """
    schedule = get_object_or_404(SessionSchedule, shareable_token=token)
    
    email = request.POST.get('email', '').strip()
    player_name = request.POST.get('player_name', '').strip()
    character_name = request.POST.get('character_name', '').strip()
    
    if not email or not player_name:
        context = {
            'error': 'Please provide your name and email address.'
        }
        return render(request, 'sessions/components/_availability_error.html', context)
    
    # Get the availability record
    try:
        availability = PlayerAvailability.objects.get(
            session_schedule=schedule,
            email=email
        )
        
        # Update final info
        availability.player_name = player_name
        availability.character_name = character_name
        availability.save()
        
        # Return success message
        context = {
            'player_name': availability.player_name,
            'schedule': schedule
        }
        return render(request, 'sessions/components/_availability_success_message.html', context)
    
    except PlayerAvailability.DoesNotExist:
        context = {
            'error': 'No availability data found. Please select at least one time slot.'
        }
        return render(request, 'sessions/components/_availability_error.html', context)
