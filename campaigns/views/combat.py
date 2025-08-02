from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from ..models import Campaign, Chapter, Encounter, CombatSession, CombatParticipant, Enemy, CharacterSummary
from ..forms.combat import CombatSessionForm


class CombatSessionCreateView(LoginRequiredMixin, CreateView):
    model = CombatSession
    form_class = CombatSessionForm
    template_name = 'combat/combat_session_create.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.campaign = get_object_or_404(Campaign, id=kwargs['campaign_id'], owner=request.user)
        self.chapter = get_object_or_404(Chapter, id=kwargs['chapter_id'], campaign=self.campaign)
        self.encounter = get_object_or_404(Encounter, id=kwargs['encounter_id'], chapter=self.chapter)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = self.campaign
        context['chapter'] = self.chapter
        context['encounter'] = self.encounter
        context['available_enemies'] = self.encounter.enemies.all()
        context['available_characters'] = self.campaign.characters.all()
        return context
    
    def form_valid(self, form):
        form.instance.encounter = self.encounter
        form.instance.owner = self.request.user
        
        # Set default name if not provided
        if not form.instance.name:
            form.instance.name = f"{self.encounter.title} Combat"
        
        response = super().form_valid(form)
        
        # Create combat participants from encounter enemies
        for enemy in self.encounter.enemies.all():
            CombatParticipant.objects.create(
                combat_session=self.object,
                participant_type='enemy',
                enemy=enemy,
                name=enemy.name,
                current_hp=enemy.hit_points,
                max_hp=enemy.hit_points
            )
        
        # Create combat participants from campaign characters
        for character in self.campaign.characters.all():
            CombatParticipant.objects.create(
                combat_session=self.object,
                participant_type='player',
                character=character,
                name=character.character_name,
                current_hp=character.current_hit_points or 20,  # Default if not set
                max_hp=character.current_hit_points or 20
            )
        
        messages.success(self.request, f"Combat session '{self.object.name}' created successfully!")
        return response
    
    def get_success_url(self):
        return reverse('campaigns:combat_session_detail', kwargs={
            'campaign_id': self.campaign.id,
            'chapter_id': self.chapter.id,
            'encounter_id': self.encounter.id,
            'session_id': self.object.id
        })


class CombatSessionDetailView(LoginRequiredMixin, DetailView):
    model = CombatSession
    template_name = 'combat/combat_session_detail.html'
    context_object_name = 'combat_session'
    pk_url_kwarg = 'session_id'
    
    def dispatch(self, request, *args, **kwargs):
        self.campaign = get_object_or_404(Campaign, id=kwargs['campaign_id'], owner=request.user)
        self.chapter = get_object_or_404(Chapter, id=kwargs['chapter_id'], campaign=self.campaign)
        self.encounter = get_object_or_404(Encounter, id=kwargs['encounter_id'], chapter=self.chapter)
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return CombatSession.objects.filter(
            encounter=self.encounter,
            owner=self.request.user
        ).prefetch_related('participants__enemy', 'participants__character')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = self.campaign
        context['chapter'] = self.chapter
        context['encounter'] = self.encounter
        
        # Get participants organized by type and initiative order
        participants = self.object.participants.all().order_by('initiative_order')
        context['participants'] = participants
        context['active_participants'] = participants.filter(is_active=True)
        context['current_participant'] = self.object.get_current_participant()
        
        # Combat actions for this round
        context['current_round_actions'] = self.object.actions.filter(
            round_number=self.object.current_round
        ).order_by('timestamp')
        
        return context


class CombatSessionUpdateView(LoginRequiredMixin, UpdateView):
    model = CombatSession
    form_class = CombatSessionForm
    template_name = 'combat/combat_session_edit.html'
    pk_url_kwarg = 'session_id'
    
    def dispatch(self, request, *args, **kwargs):
        self.campaign = get_object_or_404(Campaign, id=kwargs['campaign_id'], owner=request.user)
        self.chapter = get_object_or_404(Chapter, id=kwargs['chapter_id'], campaign=self.campaign)
        self.encounter = get_object_or_404(Encounter, id=kwargs['encounter_id'], chapter=self.chapter)
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return CombatSession.objects.filter(encounter=self.encounter, owner=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = self.campaign
        context['chapter'] = self.chapter
        context['encounter'] = self.encounter
        return context
    
    def get_success_url(self):
        messages.success(self.request, "Combat session updated successfully!")
        return reverse('campaigns:combat_session_detail', kwargs={
            'campaign_id': self.campaign.id,
            'chapter_id': self.chapter.id,
            'encounter_id': self.encounter.id,
            'session_id': self.object.id
        })


class CombatSessionDeleteView(LoginRequiredMixin, DeleteView):
    model = CombatSession
    template_name = 'combat/combat_session_delete.html'
    pk_url_kwarg = 'session_id'
    
    def dispatch(self, request, *args, **kwargs):
        self.campaign = get_object_or_404(Campaign, id=kwargs['campaign_id'], owner=request.user)
        self.chapter = get_object_or_404(Chapter, id=kwargs['chapter_id'], campaign=self.campaign)
        self.encounter = get_object_or_404(Encounter, id=kwargs['encounter_id'], chapter=self.chapter)
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return CombatSession.objects.filter(encounter=self.encounter, owner=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = self.campaign
        context['chapter'] = self.chapter
        context['encounter'] = self.encounter
        return context
    
    def get_success_url(self):
        messages.success(self.request, "Combat session deleted successfully!")
        return reverse('campaigns:chapter_detail', kwargs={
            'campaign_id': self.campaign.id,
            'chapter_id': self.chapter.id
        })


# HTMX/Ajax endpoints for combat actions
@require_POST
@csrf_exempt
def start_combat(request, campaign_id, chapter_id, encounter_id, session_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=403)
    
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    chapter = get_object_or_404(Chapter, id=chapter_id, campaign=campaign)
    encounter = get_object_or_404(Encounter, id=encounter_id, chapter=chapter)
    combat_session = get_object_or_404(CombatSession, id=session_id, encounter=encounter, owner=request.user)
    
    if combat_session.status == 'setup':
        combat_session.start_combat()
        return JsonResponse({'status': 'success', 'message': 'Combat started!'})
    
    return JsonResponse({'error': 'Combat is not in setup phase'}, status=400)


@require_POST
@csrf_exempt
def roll_initiative(request, campaign_id, chapter_id, encounter_id, session_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=403)
    
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    chapter = get_object_or_404(Chapter, id=chapter_id, campaign=campaign)
    encounter = get_object_or_404(Encounter, id=encounter_id, chapter=chapter)
    combat_session = get_object_or_404(CombatSession, id=session_id, encounter=encounter, owner=request.user)
    
    combat_session.roll_initiative()
    return JsonResponse({'status': 'success', 'message': 'Initiative rolled!'})


@require_POST
@csrf_exempt
def next_turn(request, campaign_id, chapter_id, encounter_id, session_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=403)
    
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    chapter = get_object_or_404(Chapter, id=chapter_id, campaign=campaign)
    encounter = get_object_or_404(Encounter, id=encounter_id, chapter=chapter)
    combat_session = get_object_or_404(CombatSession, id=session_id, encounter=encounter, owner=request.user)
    
    combat_session.next_turn()
    current_participant = combat_session.get_current_participant()
    
    return JsonResponse({
        'status': 'success',
        'current_round': combat_session.current_round,
        'current_turn': combat_session.current_turn,
        'current_participant': current_participant.name if current_participant else None
    })


@require_POST
@csrf_exempt
def end_combat(request, campaign_id, chapter_id, encounter_id, session_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=403)
    
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    chapter = get_object_or_404(Chapter, id=chapter_id, campaign=campaign)
    encounter = get_object_or_404(Encounter, id=encounter_id, chapter=chapter)
    combat_session = get_object_or_404(CombatSession, id=session_id, encounter=encounter, owner=request.user)
    
    combat_session.end_combat()
    return JsonResponse({'status': 'success', 'message': 'Combat ended!'})