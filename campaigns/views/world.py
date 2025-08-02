from django.views.generic import CreateView, UpdateView, DetailView, DeleteView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy

from ..models import Campaign, Location, NPC
from ..forms import LocationForm, NPCForm


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