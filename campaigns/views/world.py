from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, ListView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy

from ..models import Campaign, Location, NPC, Enemy, Chapter, CharacterSummary
from ..forms import LocationForm, NPCForm, EnemyForm


class LocationCreateView(LoginRequiredMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = "locations/location_form.html"

    def dispatch(self, request, *args, **kwargs):
        # Secure campaign access by ownership
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['campaign'] = self.campaign
        return kwargs

    def form_valid(self, form):
        form.instance.campaign = self.campaign
        form.instance.owner = self.request.user
        messages.success(self.request, "Location created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class LocationUpdateView(LoginRequiredMixin, UpdateView):
    model = Location
    form_class = LocationForm
    template_name = "locations/location_form.html"
    pk_url_kwarg = 'location_id'

    def get_queryset(self):
        # Only allow access to locations owned via campaign
        campaign_id = self.kwargs['campaign_id']
        return Location.objects.select_related('campaign').filter(
            campaign__owner=self.request.user,
            campaign_id=campaign_id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['campaign'] = self.object.campaign
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Location updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class LocationDetailView(LoginRequiredMixin, DetailView):
    model = Location
    template_name = "locations/location_detail.html"
    pk_url_kwarg = 'location_id'
    context_object_name = 'location'

    def get_queryset(self):
        # Enforce ownership by checking related campaign
        campaign_id = self.kwargs['campaign_id']
        return Location.objects.select_related('campaign').filter(
            campaign__owner=self.request.user,
            campaign_id=campaign_id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context


class LocationDeleteView(LoginRequiredMixin, DeleteView):
    model = Location
    template_name = "locations/location_delete_confirmation.html"
    pk_url_kwarg = 'location_id'
    context_object_name = 'location'

    def get_queryset(self):
        # Enforce ownership by checking related campaign
        campaign_id = self.kwargs['campaign_id']
        return Location.objects.select_related('campaign').filter(
            campaign__owner=self.request.user,
            campaign_id=campaign_id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Location '{self.object.name}' deleted successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class NPCCreateView(LoginRequiredMixin, CreateView):
    model = NPC
    form_class = NPCForm
    template_name = "npcs/npc_form.html"

    def dispatch(self, request, *args, **kwargs):
        # Restrict access to only campaigns owned by the user
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=request.user),
            pk=self.kwargs["campaign_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['campaign'] = self.campaign
        return kwargs

    def form_valid(self, form):
        form.instance.campaign = self.campaign
        form.instance.owner = self.request.user
        messages.success(self.request, "NPC created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class NPCUpdateView(LoginRequiredMixin, UpdateView):
    model = NPC
    form_class = NPCForm
    template_name = "npcs/npc_form.html"
    pk_url_kwarg = 'npc_id'

    def get_queryset(self):
        # Enforce ownership by checking related campaign
        campaign_id = self.kwargs['campaign_id']
        return NPC.objects.select_related('campaign').filter(
            campaign__owner=self.request.user,
            campaign_id=campaign_id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['campaign'] = self.object.campaign
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "NPC updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class NPCDetailView(LoginRequiredMixin, DetailView):
    model = NPC
    template_name = "npcs/npc_detail.html"
    pk_url_kwarg = 'npc_id'
    context_object_name = 'npc'

    def get_queryset(self):
        # Enforce ownership by checking related campaign
        campaign_id = self.kwargs['campaign_id']
        return NPC.objects.select_related('campaign').filter(
            campaign__owner=self.request.user,
            campaign_id=campaign_id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context


class NPCDeleteView(LoginRequiredMixin, DeleteView):
    model = NPC
    template_name = "npcs/npc_delete_confirmation.html"
    pk_url_kwarg = 'npc_id'
    context_object_name = 'npc'

    def get_queryset(self):
        # Enforce ownership by checking related campaign
        campaign_id = self.kwargs['campaign_id']
        return NPC.objects.select_related('campaign').filter(
            campaign__owner=self.request.user,
            campaign_id=campaign_id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context

    def form_valid(self, form):
        messages.success(self.request, f"NPC '{self.object.name}' deleted successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


# Enemy CRUD Views

class EnemyCreateView(LoginRequiredMixin, CreateView):
    model = Enemy
    form_class = EnemyForm
    template_name = "enemies/enemy_form.html"

    def dispatch(self, request, *args, **kwargs):
        # Restrict access to only campaigns owned by the user
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=request.user),
            pk=self.kwargs["campaign_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['campaign'] = self.campaign
        return kwargs

    def form_valid(self, form):
        form.instance.campaign = self.campaign
        form.instance.owner = self.request.user
        messages.success(self.request, "Enemy created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class EnemyUpdateView(LoginRequiredMixin, UpdateView):
    model = Enemy
    form_class = EnemyForm
    template_name = "enemies/enemy_form.html"
    pk_url_kwarg = 'enemy_id'

    def get_queryset(self):
        # Enforce ownership by checking related campaign
        campaign_id = self.kwargs['campaign_id']
        return Enemy.objects.select_related('campaign').filter(
            campaign__owner=self.request.user,
            campaign_id=campaign_id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['campaign'] = self.object.campaign
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Enemy updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class EnemyDetailView(LoginRequiredMixin, DetailView):
    model = Enemy
    template_name = "enemies/enemy_detail.html"
    pk_url_kwarg = 'enemy_id'
    context_object_name = 'enemy'

    def get_queryset(self):
        # Enforce ownership by checking related campaign
        campaign_id = self.kwargs['campaign_id']
        return Enemy.objects.select_related('campaign').filter(
            campaign__owner=self.request.user,
            campaign_id=campaign_id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context


class EnemyDeleteView(LoginRequiredMixin, DeleteView):
    model = Enemy
    template_name = "enemies/enemy_delete_confirmation.html"
    pk_url_kwarg = 'enemy_id'
    context_object_name = 'enemy'

    def get_queryset(self):
        # Enforce ownership by checking related campaign
        campaign_id = self.kwargs['campaign_id']
        return Enemy.objects.select_related('campaign').filter(
            campaign__owner=self.request.user,
            campaign_id=campaign_id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Enemy '{self.object.name}' deleted successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class NPCToEnemyConvertView(LoginRequiredMixin, DetailView):
    """
    Convert an NPC to an Enemy for combat use
    """
    model = NPC
    template_name = "npcs/npc_to_enemy_convert.html"
    pk_url_kwarg = 'npc_id'
    context_object_name = 'npc'

    def get_queryset(self):
        # Enforce ownership by checking related campaign
        campaign_id = self.kwargs['campaign_id']
        return NPC.objects.select_related('campaign').filter(
            campaign__owner=self.request.user,
            campaign_id=campaign_id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        # Check if this NPC has already been converted
        context["existing_enemy"] = Enemy.objects.filter(source_npc=self.object).first()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Check if already converted
        existing_enemy = Enemy.objects.filter(source_npc=self.object).first()
        if existing_enemy:
            messages.warning(request, f"'{self.object.name}' has already been converted to an enemy.")
            return redirect('campaigns:enemy_detail', 
                          campaign_id=self.object.campaign.id, 
                          enemy_id=existing_enemy.id)
        
        # Create enemy from NPC
        try:
            enemy = Enemy.create_from_npc(self.object)
            enemy.save()
            messages.success(request, 
                           f"Successfully converted '{self.object.name}' to an enemy! "
                           f"You can now edit the enemy stats and add it to encounters.")
            return redirect('campaigns:enemy_detail', 
                          campaign_id=enemy.campaign.id, 
                          enemy_id=enemy.id)
        except Exception as e:
            messages.error(request, f"Error converting NPC to enemy: {str(e)}")
            return redirect('campaigns:npc_detail', 
                          campaign_id=self.object.campaign.id, 
                          npc_id=self.object.id)


# Chapter Resource List Views

class ChapterNPCListView(LoginRequiredMixin, ListView):
    model = NPC
    template_name = "chapters/resources/npc_list.html"
    context_object_name = 'npcs'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Secure campaign and chapter access by ownership
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        self.chapter = get_object_or_404(
            Chapter.objects.filter(campaign=self.campaign),
            pk=self.kwargs["chapter_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Return NPCs that are involved in this chapter
        return self.chapter.involved_npcs.all().select_related('campaign', 'location')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        context["chapter"] = self.chapter
        return context


# Campaign Resource List Views

class CampaignNPCListView(LoginRequiredMixin, ListView):
    model = NPC
    template_name = "campaigns/resources/npc_list.html"
    context_object_name = 'npcs'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Secure campaign access by ownership
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Return all NPCs for this campaign
        return NPC.objects.filter(campaign=self.campaign).select_related('campaign', 'location')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        return context


class CampaignLocationListView(LoginRequiredMixin, ListView):
    model = Location
    template_name = "campaigns/resources/location_list.html" 
    context_object_name = 'locations'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Secure campaign access by ownership
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Return all locations for this campaign
        return Location.objects.filter(campaign=self.campaign).select_related('campaign')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        return context


class CampaignCharacterListView(LoginRequiredMixin, ListView):
    model = CharacterSummary
    template_name = "campaigns/resources/character_list.html"
    context_object_name = 'characters'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Secure campaign access by ownership
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Return all characters for this campaign
        return CharacterSummary.objects.filter(campaign=self.campaign)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        return context


class CampaignEnemyListView(LoginRequiredMixin, ListView):
    model = Enemy
    template_name = "campaigns/resources/enemy_list.html"
    context_object_name = 'enemies'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Secure campaign access by ownership
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Return all enemies for this campaign
        return Enemy.objects.filter(campaign=self.campaign).select_related('campaign')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        return context


class ChapterLocationListView(LoginRequiredMixin, ListView):
    model = Location
    template_name = "chapters/resources/location_list.html" 
    context_object_name = 'locations'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Secure campaign and chapter access by ownership
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        self.chapter = get_object_or_404(
            Chapter.objects.filter(campaign=self.campaign),
            pk=self.kwargs["chapter_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Return locations that are involved in this chapter
        return self.chapter.involved_locations.all().select_related('campaign')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        context["chapter"] = self.chapter
        return context


# Campaign Resource List Views

class CampaignNPCListView(LoginRequiredMixin, ListView):
    model = NPC
    template_name = "campaigns/resources/npc_list.html"
    context_object_name = 'npcs'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Secure campaign access by ownership
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Return all NPCs for this campaign
        return NPC.objects.filter(campaign=self.campaign).select_related('campaign', 'location')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        return context


class CampaignLocationListView(LoginRequiredMixin, ListView):
    model = Location
    template_name = "campaigns/resources/location_list.html" 
    context_object_name = 'locations'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Secure campaign access by ownership
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Return all locations for this campaign
        return Location.objects.filter(campaign=self.campaign).select_related('campaign')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        return context


class CampaignCharacterListView(LoginRequiredMixin, ListView):
    model = CharacterSummary
    template_name = "campaigns/resources/character_list.html"
    context_object_name = 'characters'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Secure campaign access by ownership
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Return all characters for this campaign
        return CharacterSummary.objects.filter(campaign=self.campaign)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        return context


class CampaignEnemyListView(LoginRequiredMixin, ListView):
    model = Enemy
    template_name = "campaigns/resources/enemy_list.html"
    context_object_name = 'enemies'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Secure campaign access by ownership
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Return all enemies for this campaign
        return Enemy.objects.filter(campaign=self.campaign).select_related('campaign')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        return context


class ChapterCharacterListView(LoginRequiredMixin, ListView):
    model = CharacterSummary
    template_name = "chapters/resources/character_list.html"
    context_object_name = 'characters'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Secure campaign and chapter access by ownership
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        self.chapter = get_object_or_404(
            Chapter.objects.filter(campaign=self.campaign),
            pk=self.kwargs["chapter_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Return all characters for this campaign (characters aren't chapter-specific)
        return CharacterSummary.objects.filter(campaign=self.campaign)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        context["chapter"] = self.chapter
        return context


# Campaign Resource List Views

class CampaignNPCListView(LoginRequiredMixin, ListView):
    model = NPC
    template_name = "campaigns/resources/npc_list.html"
    context_object_name = 'npcs'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Secure campaign access by ownership
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Return all NPCs for this campaign
        return NPC.objects.filter(campaign=self.campaign).select_related('campaign', 'location')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        return context


class CampaignLocationListView(LoginRequiredMixin, ListView):
    model = Location
    template_name = "campaigns/resources/location_list.html" 
    context_object_name = 'locations'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Secure campaign access by ownership
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Return all locations for this campaign
        return Location.objects.filter(campaign=self.campaign).select_related('campaign')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        return context


class CampaignCharacterListView(LoginRequiredMixin, ListView):
    model = CharacterSummary
    template_name = "campaigns/resources/character_list.html"
    context_object_name = 'characters'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Secure campaign access by ownership
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Return all characters for this campaign
        return CharacterSummary.objects.filter(campaign=self.campaign)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        return context


class CampaignEnemyListView(LoginRequiredMixin, ListView):
    model = Enemy
    template_name = "campaigns/resources/enemy_list.html"
    context_object_name = 'enemies'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Secure campaign access by ownership
        self.campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Return all enemies for this campaign
        return Enemy.objects.filter(campaign=self.campaign).select_related('campaign')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        return context


class NPCPopupView(LoginRequiredMixin, DetailView):
    model = NPC
    template_name = "npcs/npc_modal.html"
    context_object_name = "npc"
    pk_url_kwarg = 'npc_id'

    def get_queryset(self):
        # Restrict to NPCs in the specified campaign owned by the user
        campaign_id = self.kwargs['campaign_id']
        return NPC.objects.select_related('campaign').filter(
            campaign__owner=self.request.user,
            campaign_id=campaign_id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context


class EnemyPopupView(LoginRequiredMixin, DetailView):
    model = Enemy
    template_name = "enemies/enemy_modal.html"
    context_object_name = "enemy"
    pk_url_kwarg = 'enemy_id'

    def get_queryset(self):
        # Restrict to enemies in the specified campaign owned by the user
        campaign_id = self.kwargs['campaign_id']
        return Enemy.objects.filter(
            campaign__owner=self.request.user,
            campaign_id=campaign_id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context