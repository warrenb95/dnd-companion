from django.contrib import admin
from .models import Campaign, Chapter, NPC, Encounter, Location, SessionNote, CharacterSummary

admin.site.register(Campaign)
admin.site.register(Chapter)
admin.site.register(Encounter)
admin.site.register(NPC)
admin.site.register(Location)
admin.site.register(SessionNote)
admin.site.register(CharacterSummary)
