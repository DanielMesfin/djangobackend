from django.db import models
from django.utils.translation import gettext_lazy as _
from .user import User

class KYCVerification(models.Model):
    class KYCStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')
        SUSPENDED = 'SUSPENDED', _('Suspended')
        DELETED = 'DELETED', _('Deleted')

    class DocumentType(models.TextChoices):
        PASSPORT = 'PASSPORT', _('Passport')
        NATIONAL_ID = 'NATIONAL_ID', _('National ID')
        DRIVING_LICENSE = 'DRIVING_LICENSE', _('Driving License')
        UTILITY_BILL = 'UTILITY_BILL', _('Utility Bill')
        BANK_STATEMENT = 'BANK_STATEMENT', _('Bank Statement')
        OTHER = 'OTHER', _('Other')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kyc_verifications')
    document_type = models.CharField(_('document type'), max_length=30, choices=DocumentType.choices)
    document_number = models.CharField(_('document number'), max_length=100)
    document_front = models.URLField(_('document front'))
    document_back = models.URLField(_('document back'), blank=True, null=True)
    selfie = models.URLField(_('selfie'), blank=True, null=True)
    status = models.CharField(_('status'), max_length=20, choices=KYCStatus.choices, default=KYCStatus.PENDING)
    rejection_reason = models.TextField(_('rejection reason'), blank=True, null=True)
    verified_at = models.DateTimeField(_('verified at'), blank=True, null=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_kyc_documents'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.get_document_type_display()} ({self.status})"

    class Meta:
        verbose_name = _('KYC verification')
        verbose_name_plural = _('KYC verifications')
        ordering = ['-created_at']

class BusinessDocument(models.Model):
    class DocumentType(models.TextChoices):
        CERTIFICATE_OF_INCORPORATION = 'CERTIFICATE_OF_INCORPORATION', _('Certificate of Incorporation')
        TAX_ID = 'TAX_ID', _('Tax ID')
        BANK_STATEMENT = 'BANK_STATEMENT', _('Bank Statement')
        ADDRESS_PROOF = 'ADDRESS_PROOF', _('Proof of Address')
        LICENSE = 'LICENSE', _('Business License')
        OTHER = 'OTHER', _('Other')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_documents')
    document_type = models.CharField(_('document type'), max_length=50, choices=DocumentType.choices)
    file_url = models.URLField(_('file URL'))
    file_name = models.CharField(_('file name'), max_length=255)
    file_size = models.PositiveIntegerField(_('file size in bytes'))
    mime_type = models.CharField(_('MIME type'), max_length=100)
    is_verified = models.BooleanField(_('verified'), default=False)
    verified_at = models.DateTimeField(_('verified at'), blank=True, null=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.get_document_type_display()}"

    class Meta:
        verbose_name = _('business document')
        verbose_name_plural = _('business documents')
        ordering = ['-created_at']
