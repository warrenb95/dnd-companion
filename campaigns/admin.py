from django.contrib import admin
from .models import Campaign, Chapter, NPC, Location, SessionNote

admin.site.register(Campaign)
admin.site.register(Chapter)
admin.site.register(NPC)
admin.site.register(Location)
admin.site.register(SessionNote)
