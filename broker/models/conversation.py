from django.db import models
from django.utils.translation import gettext_lazy as _
from .user import User
from .listing import Listing

class Conversation(models.Model):
    class ConversationStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', _('Active')
        ARCHIVED = 'ARCHIVED', _('Archived')
        BLOCKED = 'BLOCKED', _('Blocked')
        COMPLETED = 'COMPLETED', _('Completed')

    listing = models.ForeignKey(Listing, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_conversations')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_conversations')
    status = models.CharField(_('status'), max_length=20, choices=ConversationStatus.choices, default=ConversationStatus.ACTIVE)
    last_message_at = models.DateTimeField(_('last message at'), auto_now=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        unique_together = ('buyer', 'seller', 'listing')
        ordering = ['-last_message_at']
        verbose_name = _('conversation')
        verbose_name_plural = _('conversations')

    def __str__(self):
        return f"{self.buyer.email} - {self.seller.email} - {self.listing.title if self.listing else 'No Listing'}"

class Message(models.Model):
    class MessageType(models.TextChoices):
        TEXT = 'TEXT', _('Text')
        IMAGE = 'IMAGE', _('Image')
        FILE = 'FILE', _('File')
        SYSTEM = 'SYSTEM', _('System')
        ORDER = 'ORDER', _('Order')
        PAYMENT = 'PAYMENT', _('Payment')

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message_type = models.CharField(_('type'), max_length=20, choices=MessageType.choices, default=MessageType.TEXT)
    content = models.TextField(_('content'))
    is_read = models.BooleanField(_('read'), default=False)
    read_at = models.DateTimeField(_('read at'), null=True, blank=True)
    metadata = models.JSONField(_('metadata'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = _('message')
        verbose_name_plural = _('messages')

    def __str__(self):
        return f"{self.sender.email} - {self.get_message_type_display()} - {self.content[:50]}"

class DraftOrder(models.Model):
    class OrderStatus(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PENDING = 'PENDING', _('Pending')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        CANCELLED = 'CANCELLED', _('Cancelled')
        COMPLETED = 'COMPLETED', _('Completed')

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='draft_orders')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='draft_orders')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_draft_orders')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_draft_orders')
    quantity = models.PositiveIntegerField(_('quantity'), default=1)
    price = models.DecimalField(_('price'), max_digits=12, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(_('total amount'), max_digits=12, decimal_places=2)
    status = models.CharField(_('status'), max_length=20, choices=OrderStatus.choices, default=OrderStatus.DRAFT)
    shipping_info = models.TextField(_('shipping info'), blank=True, null=True)
    notes = models.TextField(_('notes'), blank=True, null=True)
    metadata = models.JSONField(_('metadata'), blank=True, null=True)
    expires_at = models.DateTimeField(_('expires at'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('draft order')
        verbose_name_plural = _('draft orders')

    def __str__(self):
        return f"Draft Order #{self.id} - {self.listing.title} - {self.get_status_display()}"
