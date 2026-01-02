from django.db import models
from django.utils.translation import gettext_lazy as _
from .user import User

class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        DEPOSIT = 'DEPOSIT', _('Deposit')
        WITHDRAWAL = 'WITHDRAWAL', _('Withdrawal')
        PREMIUM_SUBSCRIPTION = 'PREMIUM_SUBSCRIPTION', _('Premium Subscription')
        PROMOTION_BOOST = 'PROMOTION_BOOST', _('Promotion Boost')

    class TransactionStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')
        REFUNDED = 'REFUNDED', _('Refunded')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    transaction_type = models.CharField(_('type'), max_length=30, choices=TransactionType.choices)
    status = models.CharField(_('status'), max_length=20, choices=TransactionStatus.choices, default=TransactionStatus.PENDING)
    description = models.TextField(_('description'), blank=True, null=True)
    reference = models.CharField(_('reference'), max_length=100, blank=True, null=True)
    metadata = models.JSONField(_('metadata'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} ({self.status})"

    class Meta:
        verbose_name = _('transaction')
        verbose_name_plural = _('transactions')
        ordering = ['-created_at']

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(_('balance'), max_digits=12, decimal_places=2, default=0)
    points = models.PositiveIntegerField(_('points'), default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s Wallet"

    class Meta:
        verbose_name = _('wallet')
        verbose_name_plural = _('wallets')
