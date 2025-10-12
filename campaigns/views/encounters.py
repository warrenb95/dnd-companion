from django.views.generic import CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import date

from ..models import Chapter, Encounter, SessionNote, CharacterSummary
from ..forms import EncounterForm


class EncounterCreateView(LoginRequiredMixin, CreateView):
    model = Encounter
    form_class = EncounterForm
    template_name = "encounters/encounter_form.html"

    def dispatch(self, request, *args, **kwargs):
        # Fetch and cache the chapter object, ensuring user ownership and correct campaign
        campaign_id = self.kwargs["campaign_id"]
        chapter_id = self.kwargs["chapter_id"]
        self.chapter = get_object_or_404(
            Chapter.objects.select_related('campaign').filter(
                campaign__owner=request.user,
                campaign_id=campaign_id
            ),
            pk=chapter_id
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chapter"] = self.chapter
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['campaign'] = self.chapter.campaign
        return kwargs

    def form_valid(self, form):
        # Auto-assign the encounter to the correct chapter and owner
        form.instance.chapter = self.chapter
        form.instance.owner = self.request.user
        
        # Auto-increment the order field (find highest order in chapter + 1)
        last_encounter = self.chapter.encounters.order_by("-order").first()
        form.instance.order = (last_encounter.order + 1) if last_encounter else 1
        
        messages.success(self.request, f"Encounter '{form.instance.title}' created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect back to chapter detail view after success
        return self.chapter.get_absolute_url()


class EncounterUpdateView(LoginRequiredMixin, UpdateView):
    model = Encounter
    form_class = EncounterForm
    template_name = "encounters/encounter_form.html"
    pk_url_kwarg = 'encounter_id'

    def get_queryset(self):
        # Only allow editing encounters if the user owns the parent campaign
        campaign_id = self.kwargs['campaign_id']
        chapter_id = self.kwargs['chapter_id']
        return Encounter.objects.select_related('chapter__campaign').filter(
            chapter__campaign__owner=self.request.user,
            chapter__campaign_id=campaign_id,
            chapter_id=chapter_id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chapter"] = self.object.chapter
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['campaign'] = self.object.chapter.campaign
        return kwargs

    def form_valid(self, form):
        import logging
        logger = logging.getLogger(__name__)
        
        # Log form submission details
        logger.info(f"Processing encounter form submission - User: {self.request.user.id}, "
                   f"Encounter: {form.instance.id}, Title: {form.instance.title}")
        
        # Check if map_reference was changed
        if 'map_reference' in form.changed_data:
            map_reference = form.cleaned_data.get('map_reference')
            if map_reference:
                logger.info(f"Map reference updated: {map_reference}")
            else:
                logger.info("Map reference field was cleared")
        else:
            logger.info("No map reference changes detected")
        
        try:
            result = super().form_valid(form)
            logger.info(f"Encounter saved successfully - ID: {form.instance.id}")
            
            # Log final map_reference details if it exists
            if form.instance.map_reference:
                logger.info(f"Final map reference: {form.instance.map_reference}")
            
            messages.success(self.request, f"Encounter '{form.instance.title}' updated successfully.")
            return result
        except Exception as e:
            logger.error(f"Error saving encounter - ID: {form.instance.id}, Error: {str(e)}")
            messages.error(self.request, f"Error saving encounter: {str(e)}")
            raise

    def get_success_url(self):
        # Redirect back to chapter detail view after success
        return self.object.chapter.get_absolute_url()


class EncounterDeleteView(LoginRequiredMixin, DeleteView):
    model = Encounter
    template_name = "encounters/encounter_delete_confirmation.html"
    pk_url_kwarg = 'encounter_id'

    def get_queryset(self):
        # Ensure only the encounter owner can delete (via campaign ownership)
        campaign_id = self.kwargs['campaign_id']
        chapter_id = self.kwargs['chapter_id']
        return Encounter.objects.select_related('chapter__campaign').filter(
            chapter__campaign__owner=self.request.user,
            chapter__campaign_id=campaign_id,
            chapter_id=chapter_id
        )

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(request, f"Encounter '{self.object.title}' deleted successfully.")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.chapter.get_absolute_url()


class EncounterNoteFormView(View):
    def get(self, request, campaign_id, chapter_id, encounter_id):
        encounter = get_object_or_404(
            Encounter.objects.select_related('chapter__campaign').filter(
                chapter__campaign__owner=request.user,
                chapter__campaign_id=campaign_id,
                chapter_id=chapter_id
            ),
            pk=encounter_id
        )
        return render(request, "encounters/components/_note_form.html", {"encounter": encounter})


class EncounterNoteCreateView(View):
    def post(self, request, campaign_id, chapter_id, encounter_id):
        content = request.POST.get("content")
        note_date = request.POST.get("date")
        encounter = None

        if content:
            encounter = get_object_or_404(
                Encounter.objects.select_related('chapter__campaign').prefetch_related('session_notes').filter(
                    chapter__campaign__owner=request.user,
                    chapter__campaign_id=campaign_id,
                    chapter_id=chapter_id
                ),
                pk=encounter_id
            )

            # Create note with date if provided, otherwise use today
            if note_date:
                SessionNote.objects.create(
                    encounter=encounter,
                    content=content,
                    date=note_date,
                    owner=request.user
                )
            else:
                SessionNote.objects.create(
                    encounter=encounter,
                    content=content,
                    owner=request.user
                )

            messages.success(request, "Session note added successfully.")

        # Check if this is from the play page modal (return play notes component)
        # or from chapter detail (return chapter notes list)
        hx_target = request.headers.get('HX-Target', '')
        if 'play-notes' in hx_target:
            # Return the play notes component
            # Modal will be closed by htmx:afterSwap event listener
            return render(request, "encounters/components/_play_notes.html", {"encounter": encounter})
        else:
            # Return the chapter detail notes list
            return render(request, "encounters/components/_notes_list.html", {"enc": encounter})


class EncounterNoteEditView(LoginRequiredMixin, View):
    def get(self, request, campaign_id, chapter_id, encounter_id, note_id):
        note = get_object_or_404(
            SessionNote.objects.select_related('encounter__chapter__campaign').filter(
                encounter__chapter__campaign__owner=request.user,
                encounter__chapter__campaign_id=campaign_id,
                encounter__chapter_id=chapter_id,
                encounter_id=encounter_id
            ),
            pk=note_id
        )

        # Check if this is from the play page modal (modal-content target)
        hx_target = request.headers.get('HX-Target', '')
        if 'modal-content' in hx_target:
            # Return the modal edit template
            return render(request, "encounters/components/_note_edit_modal.html", {"note": note})
        else:
            # Return the inline edit form for chapter detail page
            return render(request, "encounters/components/_note_edit_form.html", {"note": note})


class EncounterNoteUpdateView(LoginRequiredMixin, View):
    def post(self, request, campaign_id, chapter_id, encounter_id, note_id):
        note = get_object_or_404(
            SessionNote.objects.select_related('encounter__chapter__campaign').filter(
                encounter__chapter__campaign__owner=request.user,
                encounter__chapter__campaign_id=campaign_id,
                encounter__chapter_id=chapter_id,
                encounter_id=encounter_id
            ),
            pk=note_id
        )

        content = request.POST.get("content")
        date = request.POST.get("date")

        if content and date:
            note.content = content
            note.date = date
            note.save()
            messages.success(request, "Note updated successfully.")

        # Check if this is from the play page modal
        hx_target = request.headers.get('HX-Target', '')
        if 'play-notes' in hx_target:
            # Return the play notes component
            # Modal will be closed by htmx:afterSwap event listener
            return render(request, "encounters/components/_play_notes.html", {"encounter": note.encounter})
        else:
            # Return the chapter detail notes list
            return render(request, "encounters/components/_notes_list.html", {"enc": note.encounter})


class EncounterNoteDeleteView(LoginRequiredMixin, View):
    def delete(self, request, campaign_id, chapter_id, encounter_id, note_id):
        note = get_object_or_404(
            SessionNote.objects.select_related('encounter__chapter__campaign').filter(
                encounter__chapter__campaign__owner=request.user,
                encounter__chapter__campaign_id=campaign_id,
                encounter__chapter_id=chapter_id,
                encounter_id=encounter_id
            ),
            pk=note_id
        )

        encounter_id = note.encounter.id
        note.delete()
        messages.success(request, "Note deleted successfully.")

        # Re-query the encounter to get fresh session_notes data
        encounter = get_object_or_404(
            Encounter.objects.select_related('chapter__campaign').prefetch_related('session_notes').filter(
                chapter__campaign__owner=request.user,
                chapter__campaign_id=campaign_id,
                chapter_id=chapter_id
            ),
            pk=encounter_id
        )

        # Check if this is from the play page
        hx_target = request.headers.get('HX-Target', '')
        if 'play-notes' in hx_target:
            # Return the play notes component
            return render(request, "encounters/components/_play_notes.html", {"encounter": encounter})
        else:
            # Return the chapter detail notes list
            return render(request, "encounters/components/_notes_list.html", {"enc": encounter})


class EncounterPlayView(LoginRequiredMixin, View):
    """
    Comprehensive DM interface for playing an encounter.
    Provides encounter details, player stats, NPCs, enemies, and location info.
    """
    
    def get(self, request, campaign_id, chapter_id, encounter_id):
        # Get the encounter and verify ownership
        encounter = get_object_or_404(
            Encounter.objects.select_related('chapter__campaign', 'location').prefetch_related(
                'npcs', 'enemies', 'chapter__campaign__characters'
            ).filter(
                chapter__campaign__owner=request.user,
                chapter__campaign_id=campaign_id,
                chapter_id=chapter_id
            ),
            pk=encounter_id
        )
        
        # Get campaign characters for the sidebar
        characters = encounter.chapter.campaign.characters.all().order_by('character_name')
        
        # Get NPCs involved in this encounter or chapter
        encounter_npcs = encounter.npcs.all()
        chapter_npcs = encounter.chapter.involved_npcs.all()
        all_npcs = (encounter_npcs | chapter_npcs).distinct().order_by('name')
        
        # Get enemies involved in this encounter or chapter
        encounter_enemies = encounter.enemies.all()
        chapter_enemies = encounter.chapter.involved_enemies.all()
        all_enemies = (encounter_enemies | chapter_enemies).distinct().order_by('name')
        
        context = {
            'encounter': encounter,
            'campaign': encounter.chapter.campaign,
            'chapter': encounter.chapter,
            'characters': characters,
            'npcs': all_npcs,
            'enemies': all_enemies,
            'location': encounter.location,
        }

        return render(request, 'encounters/play_encounter.html', context)


class EncounterNoteModalView(LoginRequiredMixin, View):
    """
    Returns a modal form for adding session notes during encounter play.
    Used with HTMX to open the modal without navigation.
    """

    def get(self, request, campaign_id, chapter_id, encounter_id):
        # Get the encounter and verify ownership
        encounter = get_object_or_404(
            Encounter.objects.select_related('chapter__campaign').filter(
                chapter__campaign__owner=request.user,
                chapter__campaign_id=campaign_id,
                chapter_id=chapter_id
            ),
            pk=encounter_id
        )

        context = {
            'encounter': encounter,
            'today': date.today(),
        }

        return render(request, 'encounters/components/_note_modal.html', context)
