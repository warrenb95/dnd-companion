from django.db import models
from django.contrib.auth.models import User

from .base import Campaign


class Location(models.Model):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="locations"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    region = models.CharField(max_length=200, blank=True)
    tags = models.CharField(max_length=200, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations')

    def __str__(self):
        return str(self.name)


class NPC(models.Model):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="npcs"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    role = models.CharField(max_length=100, blank=True)
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("alive", "Alive"),
            ("dead", "Dead"),
            ("missing", "Missing"),
            ("unknown", "Unknown"),
        ],
        default="alive",
    )
    tags = models.CharField(max_length=200, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='npcs')

    def __str__(self):
        return str(self.name)