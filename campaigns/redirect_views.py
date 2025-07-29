"""
Redirect views for old URL patterns to maintain compatibility
"""
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Campaign, Chapter, Encounter, Location, NPC, CharacterSummary, SessionNote


@login_required
def redirect_chapter_detail(request, pk):
    """Redirect old chapter detail URLs to new hierarchical format"""
    chapter = get_object_or_404(Chapter, pk=pk, campaign__owner=request.user)
    return redirect('campaigns:chapter_detail', 
                   campaign_id=chapter.campaign.id, 
                   chapter_id=chapter.id)


@login_required  
def redirect_chapter_edit(request, pk):
    """Redirect old chapter edit URLs to new hierarchical format"""
    chapter = get_object_or_404(Chapter, pk=pk, campaign__owner=request.user)
    return redirect('campaigns:chapter_edit',
                   campaign_id=chapter.campaign.id,
                   chapter_id=chapter.id)


@login_required
def redirect_chapter_delete(request, pk):
    """Redirect old chapter delete URLs to new hierarchical format"""
    chapter = get_object_or_404(Chapter, pk=pk, campaign__owner=request.user)
    return redirect('campaigns:chapter_delete',
                   campaign_id=chapter.campaign.id,
                   chapter_id=chapter.id)


@login_required
def redirect_location_edit(request, pk):
    """Redirect old location edit URLs to new hierarchical format"""
    location = get_object_or_404(Location, pk=pk, campaign__owner=request.user)
    return redirect('campaigns:location_edit',
                   campaign_id=location.campaign.id,
                   location_id=location.id)


@login_required
def redirect_npc_edit(request, pk):
    """Redirect old NPC edit URLs to new hierarchical format"""
    npc = get_object_or_404(NPC, pk=pk, campaign__owner=request.user)
    return redirect('campaigns:npc_edit',
                   campaign_id=npc.campaign.id,
                   npc_id=npc.id)


@login_required
def redirect_character_view(request, pk):
    """Redirect old character view URLs to new hierarchical format"""
    character = get_object_or_404(CharacterSummary, pk=pk, campaign__owner=request.user)
    return redirect('campaigns:view_character',
                   campaign_id=character.campaign.id,
                   character_id=character.id)


@login_required
def redirect_character_edit(request, pk):
    """Redirect old character edit URLs to new hierarchical format"""
    character = get_object_or_404(CharacterSummary, pk=pk, campaign__owner=request.user)
    return redirect('campaigns:update_character',
                   campaign_id=character.campaign.id,
                   character_id=character.id)