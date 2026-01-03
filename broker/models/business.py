from django.db import models
from django.utils.translation import gettext_lazy as _
from .user import User

class BusinessProfile(models.Model):
    class BusinessType(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', _('Individual')
        SMALL_BUSINESS = 'SMALL_BUSINESS', _('Small Business')
        ENTERPRISE = 'ENTERPRISE', _('Enterprise')
        GOVERNMENT = 'GOVERNMENT', _('Government')

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='business_profile')
    business_name = models.CharField(_('business name'), max_length=100)
    description = models.TextField(_('description'), blank=True, null=True)
    industry = models.CharField(_('industry'), max_length=100)
    location = models.CharField(_('location'), max_length=100, blank=True, null=True)
    website = models.URLField(_('website'), blank=True, null=True)
    logo_url = models.URLField(_('logo URL'), blank=True, null=True)
    business_type = models.CharField(_('business type'), max_length=20, choices=BusinessType.choices, default=BusinessType.INDIVIDUAL)
    is_verified = models.BooleanField(_('verified'), default=False)
    collaboration_types = models.JSONField(_('collaboration types'), blank=True, null=True)
    goals = models.TextField(_('goals'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return self.business_name

    class Meta:
        verbose_name = _('business')
        verbose_name_plural = _('businesses')

class BusinessMember(models.Model):
    class Role(models.TextChoices):
        OWNER = 'OWNER', _('Owner')
        ADMIN = 'ADMIN', _('Admin')
        MANAGER = 'MANAGER', _('Manager')
        MEMBER = 'MEMBER', _('Member')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_memberships')
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(_('role'), max_length=20, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(_('joined at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        unique_together = ('user', 'business')
        verbose_name = _('business member')
        verbose_name_plural = _('business members')

    def __str__(self):
        return f"{self.user.email} - {self.get_role_display()} at {self.business.business_name}"
