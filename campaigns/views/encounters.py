from django.views.generic import CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.utils import timezone

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
        encounter = None

        if content:
            encounter = get_object_or_404(
                Encounter.objects.select_related('chapter__campaign').filter(
                    chapter__campaign__owner=request.user,
                    chapter__campaign_id=campaign_id,
                    chapter_id=chapter_id
                ),
                pk=encounter_id
            )
            SessionNote.objects.create(encounter=encounter, content=content, owner=request.user)

        # Re-render the updated notes list as HTML
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
        
        # Re-render the updated notes list as HTML
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
        
        encounter = note.encounter
        note.delete()
        messages.success(request, "Note deleted successfully.")
        
        # Re-render the updated notes list as HTML
        return render(request, "encounters/components/_notes_list.html", {"enc": encounter})


class EncounterNotesCompressView(LoginRequiredMixin, View):
    """
    Combine multiple session notes for an encounter into a single organized note.
    This deletes the original notes and replaces them with one combined note.
    """
    
    def post(self, request, campaign_id, chapter_id, encounter_id):
        try:
            with transaction.atomic():
                # Get the encounter and verify ownership
                encounter = get_object_or_404(
                    Encounter.objects.select_related('chapter__campaign').filter(
                        chapter__campaign__owner=request.user,
                        chapter__campaign_id=campaign_id,
                        chapter_id=chapter_id
                    ),
                    pk=encounter_id
                )
                
                # Get all session notes for this encounter, ordered by date
                notes = encounter.session_notes.all().order_by('date', 'id')
                
                if notes.count() < 2:
                    messages.warning(request, "Need at least 2 notes to compress.")
                    return render(request, "encounters/components/_notes_list.html", {"enc": encounter})
                
                # Extract content from all notes
                note_dates = [note.date for note in notes]
                
                # Create compressed content by concatenating all notes with clear separators
                compressed_parts = []
                for i, note in enumerate(notes, 1):
                    content = note.content.strip()
                    
                    # Check if this note is already a combined note (contains session note headers)
                    if content.startswith("## Session Note #") or "## Session Note #" in content:
                        # This is already a combined note, just add its content without new headers
                        compressed_parts.append(content)
                    else:
                        # This is a regular note, add a header
                        date_str = note.date.strftime("%B %d, %Y")
                        compressed_parts.append(f"## Session Note #{i} - {date_str}\n\n{content}")
                
                compressed_content = "\n\n---\n\n".join(compressed_parts)
                
                if not compressed_content:
                    messages.error(request, "No content found in notes to compress.")
                    return render(request, "encounters/components/_notes_list.html", {"enc": encounter})
                
                # Store the count before creating new note
                deleted_count = notes.count()
                
                # Get the IDs of notes to delete before creating the new one
                notes_to_delete_ids = list(notes.values_list('id', flat=True))
                
                # Create the new compressed note
                # Use the earliest date from the original notes
                earliest_date = min(note_dates)
                
                compressed_note = SessionNote.objects.create(
                    encounter=encounter,
                    content=compressed_content,
                    date=earliest_date,
                    owner=request.user,
                    summary=""  # The compressed content IS the summary
                )
                
                # Delete only the original notes (not the new combined one)
                SessionNote.objects.filter(id__in=notes_to_delete_ids).delete()
                
                messages.success(
                    request, 
                    f"Successfully combined {deleted_count} notes into 1 organized note."
                )
                
        except Exception as e:
            messages.error(request, f"Error compressing notes: {str(e)}")
        
        # Re-render the updated notes list  
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