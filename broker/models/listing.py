from django.db import models
from django.utils.translation import gettext_lazy as _
from .user import User
from .business import BusinessProfile

class Listing(models.Model):
    class ListingType(models.TextChoices):
        PRODUCT = 'PRODUCT', _('Product')
        SERVICE = 'SERVICE', _('Service')
        JOB = 'JOB', _('Job')
        EVENT = 'EVENT', _('Event')
        OTHER = 'OTHER', _('Other')

    class ListingStatus(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PUBLISHED = 'PUBLISHED', _('Published')
        ARCHIVED = 'ARCHIVED', _('Archived')
        SOLD = 'SOLD', _('Sold')
        EXPIRED = 'EXPIRED', _('Expired')

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'))
    listing_type = models.CharField(_('type'), max_length=20, choices=ListingType.choices)
    price = models.DecimalField(_('price'), max_digits=12, decimal_places=2)
    category = models.CharField(_('category'), max_length=100)
    tags = models.TextField(_('tags'), blank=True, null=True)
    is_negotiable = models.BooleanField(_('negotiable'), default=False)
    is_for_collaboration = models.BooleanField(_('for collaboration'), default=False)
    image_urls = models.JSONField(_('image URLs'), default=list, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings', null=True, blank=True)
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='listings', null=True, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    status = models.CharField(_('status'), max_length=20, choices=ListingStatus.choices, default=ListingStatus.DRAFT)
    quantity = models.PositiveIntegerField(_('quantity'), default=1)
    min_order = models.PositiveIntegerField(_('minimum order'), default=1)
    max_order = models.PositiveIntegerField(_('maximum order'), null=True, blank=True)
    lead_time = models.CharField(_('lead time'), max_length=100, blank=True, null=True)
    commission_rate = models.DecimalField(_('commission rate'), max_digits=5, decimal_places=2, null=True, blank=True)
    metadata = models.JSONField(_('metadata'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('listing')
        verbose_name_plural = _('listings')
        ordering = ['-created_at']

class CampaignProduct(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')

    campaign = models.ForeignKey('Campaign', on_delete=models.CASCADE, related_name='campaign_products')
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='campaign_products')
    commission_rate = models.DecimalField(_('commission rate'), max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(_('notes'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        unique_together = ('campaign', 'listing')
        verbose_name = _('campaign product')
        verbose_name_plural = _('campaign products')

    def __str__(self):
        return f"{self.campaign.name} - {self.listing.title}"
