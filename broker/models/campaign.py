from django.db import models
from django.utils.translation import gettext_lazy as _
from .user import User
from .business import BusinessProfile

class Campaign(models.Model):
    class CampaignStatus(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        ACTIVE = 'ACTIVE', _('Active')
        PAUSED = 'PAUSED', _('Paused')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')

    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True, null=True)
    start_date = models.DateTimeField(_('start date'))
    end_date = models.DateTimeField(_('end date'))
    status = models.CharField(_('status'), max_length=20, choices=CampaignStatus.choices, default=CampaignStatus.DRAFT)
    budget = models.DecimalField(_('budget'), max_digits=12, decimal_places=2, null=True, blank=True)
    target_audience = models.TextField(_('target audience'), blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_campaigns')
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='campaigns', null=True, blank=True)
    is_public = models.BooleanField(_('public'), default=False)
    metadata = models.JSONField(_('metadata'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('campaign')
        verbose_name_plural = _('campaigns')
        ordering = ['-created_at']

class CampaignCollaborator(models.Model):
    class CollaboratorRole(models.TextChoices):
        OWNER = 'OWNER', _('Owner')
        MANAGER = 'MANAGER', _('Manager')
        CONTRIBUTOR = 'CONTRIBUTOR', _('Contributor')

    class CollaboratorStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        ACCEPTED = 'ACCEPTED', _('Accepted')
        REJECTED = 'REJECTED', _('Rejected')
        REMOVED = 'REMOVED', _('Removed')

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='collaborators')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campaign_collaborations')
    role = models.CharField(_('role'), max_length=20, choices=CollaboratorRole.choices)
    status = models.CharField(_('status'), max_length=20, choices=CollaboratorStatus.choices, default=CollaboratorStatus.PENDING)
    joined_at = models.DateTimeField(_('joined at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        unique_together = ('campaign', 'user')
        verbose_name = _('campaign collaborator')
        verbose_name_plural = _('campaign collaborators')

    def __str__(self):
        return f"{self.user.email} - {self.get_role_display()} in {self.campaign.name}"
