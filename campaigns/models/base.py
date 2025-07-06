from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Campaign(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    generated_summary = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campaigns')

    def get_absolute_url(self):
        return reverse("campaigns:campaign_detail", args=[str(self.id)])

    def __str__(self):
        return str(self.title)