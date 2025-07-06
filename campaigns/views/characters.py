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


class CreateCharacterView(CreateView):
    model = CharacterSummary
    form_class = CharacterSummaryForm
    template_name = "characters//character_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campaign = get_object_or_404(Campaign, pk=self.kwargs["campaign_id"])
        context["campaign"] = campaign
        return context

    def form_valid(self, form):
        campaign = get_object_or_404(Campaign, pk=self.kwargs["campaign_id"])
        form.instance.campaign = campaign

        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class UpdateCharacterView(LoginRequiredMixin, UpdateView):
    model = CharacterSummary
    form_class = CharacterSummaryForm
    template_name = "characters/character_form.html"

    def get_queryset(self):
        # Restrict updates to only characters owned by this user via the campaign
        return CharacterSummary.objects.select_related('campaign').filter(campaign__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context

    def form_valid(self, form):
        messages.success(self.request, "Character updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()