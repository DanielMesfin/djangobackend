"""
Role-based admin configuration for the Django admin interface.
This file contains custom admin classes and configurations for all models.
"""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import SimpleListFilter

User = get_user_model()

# Custom admin site with role-based access
class RoleBasedAdminSite(admin.AdminSite):
    site_header = 'Admin Dashboard'
    site_title = 'Admin Portal'
    index_title = 'Welcome to Admin Dashboard'
    
    def has_permission(self, request):
        """Only staff users can access the admin site"""
        return request.user.is_active and request.user.is_staff

# Create custom admin site instance
admin_site = RoleBasedAdminSite(name='admin')

# Custom filters
class UserRoleFilter(SimpleListFilter):
    """Filter users by their role"""
    title = _('Role')
    parameter_name = 'role'

    def lookups(self, request, model_admin):
        return (
            ('admin', _('Admin')),
            ('business_owner', _('Business Owner')),
            ('influencer', _('Influencer')),
            ('client', _('Client')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'admin':
            return queryset.filter(is_superuser=True)
        elif self.value() == 'business_owner':
            return queryset.filter(business_memberships__role='OWNER').distinct()
        elif self.value() == 'influencer':
            return queryset.filter(role='INFLUENCER')
        elif self.value() == 'client':
            return queryset.filter(
                is_superuser=False,
                is_staff=False,
                role='CLIENT'
            )
        return queryset

# Custom User Admin
@admin.register(User, site=admin_site)
class CustomUserAdmin(BaseUserAdmin):
    """Custom User admin with role-based fields and filtering"""
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = (UserRoleFilter, 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'role')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # For non-superusers, only show their own profile
            return qs.filter(pk=request.user.pk)
        return qs

# Import and register other models
from .models import (
    UserProfile, BusinessProfile, BusinessMember,
    Campaign, CampaignCollaborator, CampaignProduct, Promotion,
    PromotionClaim, Transaction, Wallet, KYCVerification,
    BusinessDocument, Listing, Conversation, Message
)

# Inline Admin Classes
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    max_num = 1
    fields = ('avatar', 'bio', 'website', 'location', 'is_verified')
    readonly_fields = ('created_at', 'updated_at')

class BusinessMemberInline(admin.TabularInline):
    model = BusinessMember
    extra = 1
    raw_id_fields = ('user',)

class CampaignCollaboratorInline(admin.TabularInline):
    model = CampaignCollaborator
    extra = 1
    raw_id_fields = ('user',)

class CampaignProductInline(admin.TabularInline):
    model = CampaignProduct
    extra = 1
    raw_id_fields = ('product',)

# Model Admin Classes
@admin.register(UserProfile, site=admin_site)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'location', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'bio', 'location')
    raw_id_fields = ('user',)

@admin.register(BusinessProfile, site=admin_site)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'business_type', 'industry', 'is_verified', 'created_at')
    list_filter = ('business_type', 'industry', 'is_verified', 'created_at')
    search_fields = ('business_name', 'user__email', 'description')
    inlines = [BusinessMemberInline]
    raw_id_fields = ('user',)

@admin.register(Campaign, site=admin_site)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'business', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('name', 'description', 'business__business_name')
    inlines = [CampaignCollaboratorInline, CampaignProductInline]
    raw_id_fields = ('business',)
    filter_horizontal = ('products',)

@admin.register(Promotion, site=admin_site)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'business', 'category', 'is_active', 'claimed_by_button', 'start_date', 'end_date')
    list_filter = ('category', 'is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'business__business_name')
    raw_id_fields = ('business',)

    def claimed_by_button(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        count = obj.claims.count()
        url = f"{reverse('admin:broker_promotionclaim_changelist')}?promotion__id__exact={obj.id}"
        return format_html('<a class="button" href="{}">View claimants ({})</a>', url, count)
    claimed_by_button.short_description = 'Claimed By'

@admin.register(PromotionClaim, site=admin_site)
class PromotionClaimAdmin(admin.ModelAdmin):
    # Show claimant next to timestamp for quicker scanning
    list_display = ('user', 'claimed_at', 'promotion', 'points', 'shared_count')
    list_filter = ('claimed_at',)
    search_fields = ('promotion__title', 'user__email')
    raw_id_fields = ('promotion', 'user')

# Register remaining models with default configuration
@admin.register(Transaction, site=admin_site)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'transaction_type', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('user__email', 'reference')
    raw_id_fields = ('user',)

@admin.register(Wallet, site=admin_site)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'points', 'updated_at')
    search_fields = ('user__email',)
    raw_id_fields = ('user',)

@admin.register(KYCVerification, site=admin_site)
class KYCVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'status', 'created_at', 'verified_at')
    list_filter = ('document_type', 'status', 'created_at')
    search_fields = ('user__email', 'document_number')
    raw_id_fields = ('user', 'verified_by')

@admin.register(Listing, site=admin_site)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'is_active', 'created_at')
    list_filter = ('status', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'user__email')
    raw_id_fields = ('user', 'products')
    filter_horizontal = ('products',)

@admin.register(Conversation, site=admin_site)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_at', 'updated_at')
    search_fields = ('participants__email', 'subject')
    filter_horizontal = ('participants',)

@admin.register(Message, site=admin_site)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'conversation', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__email', 'content')
    raw_id_fields = ('sender', 'conversation')



# Update the default admin site
admin.site = admin_site
