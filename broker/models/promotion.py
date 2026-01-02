from django.db import models
from django.utils.translation import gettext_lazy as _
from .business import BusinessProfile
from .user import User

class Promotion(models.Model):
    class PromotionCategory(models.TextChoices):
        FOOD = 'FOOD', _('Food')
        FASHION = 'FASHION', _('Fashion')
        ELECTRONICS = 'ELECTRONICS', _('Electronics')
        BEAUTY = 'BEAUTY', _('Beauty')
        HOME = 'HOME', _('Home')
        SPORTS = 'SPORTS', _('Sports')
        TRAVEL = 'TRAVEL', _('Travel')
        OTHER = 'OTHER', _('Other')

    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='promotions')
    title = models.CharField(_('title'), max_length=100)
    description = models.TextField(_('description'), blank=True, null=True)
    image_url = models.URLField(_('image URL'), blank=True, null=True)
    start_date = models.DateTimeField(_('start date'))
    end_date = models.DateTimeField(_('end date'))
    is_active = models.BooleanField(_('active'), default=True)
    max_claims = models.PositiveIntegerField(_('maximum claims'))
    current_claims = models.PositiveIntegerField(_('current claims'), default=0)
    points_cost = models.PositiveIntegerField(_('points cost'))
    category = models.CharField(_('category'), max_length=20, choices=PromotionCategory.choices)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.business.business_name}"

    class Meta:
        verbose_name = _('promotion')
        verbose_name_plural = _('promotions')
        ordering = ['-created_at']

class PromotionClaim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='promotion_claims')
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='claims')
    shared_count = models.PositiveIntegerField(_('shared count'), default=0)
    points = models.IntegerField(_('points'), default=0)
    claimed_at = models.DateTimeField(_('claimed at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        unique_together = ('user', 'promotion')
        verbose_name = _('promotion claim')
        verbose_name_plural = _('promotion claims')

    def __str__(self):
        return f"{self.user.email} - {self.promotion.title}"
