from django.views.generic import DetailView, CreateView, UpdateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from ..models import Campaign, CharacterSummary
from ..forms import CharacterSummaryForm


class CharacterDetailView(DetailView):
    model = CharacterSummary
    template_name = "characters/details.html"
    context_object_name = "character"
    pk_url_kwarg = 'character_id'

    def get_queryset(self):
        # Restrict to characters in the specified campaign owned by the user
        campaign_id = self.kwargs['campaign_id']
        return CharacterSummary.objects.select_related('campaign').filter(
            campaign__owner=self.request.user,
            campaign_id=campaign_id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context


class CreateCharacterView(CreateView):
    model = CharacterSummary
    form_class = CharacterSummaryForm
    template_name = "characters/character_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        context["campaign"] = campaign
        return context

    def form_valid(self, form):
        campaign = get_object_or_404(
            Campaign.objects.filter(owner=self.request.user),
            pk=self.kwargs["campaign_id"]
        )
        form.instance.campaign = campaign
        form.instance.owner = self.request.user

        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class UpdateCharacterView(LoginRequiredMixin, UpdateView):
    model = CharacterSummary
    form_class = CharacterSummaryForm
    template_name = "characters/character_form.html"
    pk_url_kwarg = 'character_id'

    def get_queryset(self):
        # Restrict updates to only characters owned by this user via the campaign
        campaign_id = self.kwargs['campaign_id']
        return CharacterSummary.objects.select_related('campaign').filter(
            campaign__owner=self.request.user,
            campaign_id=campaign_id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context

    def form_valid(self, form):
        messages.success(self.request, "Character updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()