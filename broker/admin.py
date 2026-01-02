# broker/admin.py
from django.contrib import admin
from django.contrib.admin.exceptions import NotRegistered
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse, path
from django.utils.html import format_html
from django.db.models import Count
from django.template.response import TemplateResponse
from .admin_dashboard import admin_dashboard_view

from .models import (
    UserProfile, SocialLink, BusinessProfile, BusinessMember,
    Promotion, PromotionClaim, Transaction, Wallet,
    KYCVerification, BusinessDocument, Campaign, CampaignCollaborator,
    CampaignProduct, Listing, Conversation, Message, DraftOrder
)

User = get_user_model()

# Custom User Admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    max_num = 1
    fields = ('avatar', 'bio', 'website', 'location', 'is_verified')
    readonly_fields = ('created_at', 'updated_at')

class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('email', 'full_name', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'is_verified', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    date_hierarchy = 'date_joined'
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'second_name', 'last_name', 'phone', 'bio', 'avatar_url')
        }),
        (_('Role & Status'), {
            'fields': ('role', 'is_active', 'is_verified', 'is_email_verified', 'auth_provider'),
            'description': _('User role determines access and features available')
        }),
        (_('Premium Features'), {
            'fields': ('premium_until', 'points', 'referral_code'),
            'classes': ('collapse',),
            'description': _('Premium user features and settings')
        }),
        (_('Permissions'), {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role'),
        }),
    )
    
    def full_name(self, obj):
        """Display full name in list view"""
        return obj.get_full_name()
    full_name.short_description = 'Full Name'
    full_name.admin_order_field = 'first_name'
    
    def get_fieldsets(self, request, obj=None):
        """Customize fieldsets based on user role"""
        fieldsets = super().get_fieldsets(request, obj)
        
        # If editing existing user, show role-specific fields
        if obj:
            # Hide premium fields for non-premium users
            if obj.role != User.UserRole.PREMIUM:
                # Remove premium fields from fieldsets
                fieldsets = list(fieldsets)
                for i, fieldset in enumerate(fieldsets):
                    if fieldset[0] == _('Premium Features'):
                        # Keep it collapsed but visible
                        pass
        return fieldsets
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly based on context"""
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing user
            readonly.append('email')  # Don't allow email change
        return readonly
    
    def save_formset(self, request, form, formset, change):
        """
        Override to handle UserProfile inline properly.
        The signal creates a UserProfile automatically, so we need to update it instead of creating.
        """
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, UserProfile):
                # If profile already exists (created by signal), update it instead
                if instance.pk is None:
                    # Try to get existing profile
                    try:
                        existing_profile = UserProfile.objects.get(user=instance.user)
                        # Update existing profile with new data
                        for field in ['avatar', 'bio', 'website', 'location', 'is_verified']:
                            if hasattr(instance, field):
                                setattr(existing_profile, field, getattr(instance, field))
                        existing_profile.save()
                        continue
                    except UserProfile.DoesNotExist:
                        pass
                instance.save()
        formset.save_m2m()

# Broker Admin Classes
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'location', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'bio', 'location')
    list_filter = ('is_verified', 'created_at')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user',)
    list_per_page = 20
    show_full_result_count = False

@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'has_facebook', 'has_instagram', 'has_linkedin', 'updated_at')
    search_fields = ('user_profile__user__email', 'facebook_url', 'instagram_url', 'linkedin_url')
    list_filter = ('updated_at',)
    date_hierarchy = 'updated_at'
    raw_id_fields = ('user_profile',)
    list_per_page = 20
    show_full_result_count = False
    
    def has_facebook(self, obj):
        return bool(obj.facebook_url)
    has_facebook.boolean = True
    
    def has_instagram(self, obj):
        return bool(obj.instagram_url)
    has_instagram.boolean = True
    
    def has_linkedin(self, obj):
        return bool(obj.linkedin_url)
    has_linkedin.boolean = True

@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'business_type', 'industry', 'is_verified', 'created_at')
    list_filter = ('business_type', 'industry', 'is_verified', 'created_at')
    search_fields = ('business_name', 'user__email', 'description')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user',)
    list_per_page = 20
    show_full_result_count = False

@admin.register(BusinessMember)
class BusinessMemberAdmin(admin.ModelAdmin):
    list_display = ('business', 'user', 'role', 'joined_at')
    list_filter = ('role', 'joined_at')
    search_fields = ('business__business_name', 'user__email')
    date_hierarchy = 'joined_at'
    raw_id_fields = ('business', 'user')
    list_per_page = 20
    show_full_result_count = False

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'business', 'category', 'is_active', 'start_date', 'end_date')
    list_filter = ('category', 'is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'business__business_name')
    date_hierarchy = 'start_date'
    raw_id_fields = ('business',)
    list_per_page = 20
    show_full_result_count = False

@admin.register(PromotionClaim)
class PromotionClaimAdmin(admin.ModelAdmin):
    list_display = ('promotion', 'user', 'points', 'shared_count', 'claimed_at')
    list_filter = ('claimed_at',)
    search_fields = ('promotion__title', 'user__email')
    date_hierarchy = 'claimed_at'
    raw_id_fields = ('promotion', 'user')
    list_per_page = 20
    show_full_result_count = False

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'transaction_type', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('user__email', 'reference')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user',)
    list_per_page = 20
    show_full_result_count = False

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'points', 'updated_at')
    search_fields = ('user__email',)
    raw_id_fields = ('user',)
    readonly_fields = ('updated_at',)
    list_per_page = 20
    show_full_result_count = False

@admin.register(KYCVerification)
class KYCVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'status', 'created_at', 'verified_at')
    list_filter = ('document_type', 'status', 'created_at')
    search_fields = ('user__email', 'document_number')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user', 'verified_by')
    list_per_page = 20
    show_full_result_count = False

@admin.register(BusinessDocument)
class BusinessDocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'is_verified', 'created_at')
    list_filter = ('document_type', 'is_verified', 'created_at')
    search_fields = ('user__email', 'file_name')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user', 'verified_by')
    list_per_page = 20
    show_full_result_count = False

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'business', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('name', 'description', 'business__business_name')
    date_hierarchy = 'start_date'
    raw_id_fields = ('business', 'created_by')
    list_per_page = 20
    show_full_result_count = False

@admin.register(CampaignCollaborator)
class CampaignCollaboratorAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'user', 'role', 'status', 'joined_at')
    list_filter = ('role', 'status', 'joined_at')
    search_fields = ('campaign__name', 'user__email')
    date_hierarchy = 'joined_at'
    raw_id_fields = ('campaign', 'user')
    list_per_page = 20
    show_full_result_count = False

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'listing_type', 'price', 'status', 'user', 'created_at')
    list_filter = ('listing_type', 'status', 'category', 'created_at')
    search_fields = ('title', 'description', 'user__email', 'business__business_name')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user', 'business')
    list_per_page = 20
    show_full_result_count = False

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'buyer', 'seller', 'status', 'last_message_at')
    list_filter = ('status', 'last_message_at')
    search_fields = ('listing__title', 'buyer__email', 'seller__email')
    date_hierarchy = 'last_message_at'
    raw_id_fields = ('listing', 'buyer', 'seller')
    list_per_page = 20
    show_full_result_count = False

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'truncated_content', 'conversation', 'sender', 'message_type', 'is_read', 'created_at')
    list_filter = ('message_type', 'is_read', 'created_at')
    search_fields = ('content', 'sender__email')
    date_hierarchy = 'created_at'
    raw_id_fields = ('conversation', 'sender')
    list_per_page = 20
    show_full_result_count = False
    
    def truncated_content(self, obj):
        if not obj.content:
            return ""
        try:
            return str(obj.content)[:50] + ('...' if len(str(obj.content)) > 50 else '')
        except Exception:
            return "Content unavailable"
    truncated_content.short_description = 'Content'
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['pagination_required'] = True  # Ensure pagination is enabled
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(CampaignProduct)
class CampaignProductAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'listing', 'status', 'commission_rate', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('campaign__name', 'listing__title', 'notes')
    date_hierarchy = 'created_at'
    raw_id_fields = ('campaign', 'listing')
    list_per_page = 20
    show_full_result_count = False

@admin.register(DraftOrder)
class DraftOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation_link', 'listing', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('conversation__id', 'listing__title', 'buyer__email', 'seller__email')
    date_hierarchy = 'created_at'
    raw_id_fields = ('conversation', 'listing', 'buyer', 'seller')
    list_per_page = 20
    show_full_result_count = False

    def conversation_link(self, obj):
        if obj.conversation:
            url = reverse('admin:broker_conversation_change', args=[obj.conversation.id])
            return format_html('<a href="{}">{}</a>', url, obj.conversation.id)
    conversation_link.short_description = 'Conversation'
    conversation_link.admin_order_field = 'conversation'

# Unregister the default User admin and register our custom admin
# Only unregister if already registered (e.g., if it was auto-registered)
try:
    admin.site.unregister(User)
except NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)

# Override admin index to show custom dashboard
original_index = admin.site.index
def custom_index(request, extra_context=None):
    """Override admin index to show custom dashboard"""
    from .admin_dashboard import admin_dashboard_view
    return admin_dashboard_view(request)
admin.site.index = custom_index