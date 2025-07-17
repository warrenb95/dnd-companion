from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Q


class CampaignCollaborator(models.Model):
    PERMISSION_CHOICES = [
        ('owner', 'Owner'),
        ('co_dm', 'Co-DM'),
    ]
    
    campaign = models.ForeignKey(
        'Campaign', 
        on_delete=models.CASCADE, 
        related_name='collaborators'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='campaign_collaborations'
    )
    permission_level = models.CharField(
        max_length=10,
        choices=PERMISSION_CHOICES,
        default='co_dm'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['campaign', 'user']
        verbose_name = 'Campaign Collaborator'
        verbose_name_plural = 'Campaign Collaborators'
    
    def __str__(self):
        return f"{self.user.username} - {self.campaign.title} ({self.get_permission_level_display()})"


class Campaign(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    generated_summary = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campaigns')

    def get_absolute_url(self):
        return reverse("campaigns:campaign_detail", args=[str(self.id)])

    def can_edit(self, user):
        """Check if a user can edit this campaign (owner or co-DM)"""
        if self.owner == user:
            return True
        return self.collaborators.filter(user=user, permission_level='co_dm').exists()
    
    def get_all_dms(self):
        """Get all users who can edit this campaign (owner + co-DMs)"""
        co_dm_users = User.objects.filter(
            campaign_collaborations__campaign=self,
            campaign_collaborations__permission_level='co_dm'
        )
        return User.objects.filter(
            Q(pk=self.owner.pk) | Q(pk__in=co_dm_users)
        ).distinct()
    
    def get_co_dms(self):
        """Get all co-DMs for this campaign"""
        return User.objects.filter(
            campaign_collaborations__campaign=self,
            campaign_collaborations__permission_level='co_dm'
        )
    
    def add_co_dm(self, user):
        """Add a user as a co-DM"""
        if user == self.owner:
            return False, "Cannot add owner as co-DM"
        
        collaborator, created = CampaignCollaborator.objects.get_or_create(
            campaign=self,
            user=user,
            defaults={'permission_level': 'co_dm'}
        )
        
        if not created:
            return False, "User is already a co-DM"
        
        return True, "Co-DM added successfully"
    
    def remove_co_dm(self, user):
        """Remove a user as a co-DM"""
        try:
            collaborator = CampaignCollaborator.objects.get(
                campaign=self,
                user=user,
                permission_level='co_dm'
            )
            collaborator.delete()
            return True, "Co-DM removed successfully"
        except CampaignCollaborator.DoesNotExist:
            return False, "User is not a co-DM"

    def __str__(self):
        return str(self.title)