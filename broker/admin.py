# broker/admin.py
from django.contrib import admin
from django.contrib.admin.exceptions import NotRegistered
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, Permission
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
    CampaignProduct, Listing, Conversation, Message
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

class WalletInline(admin.StackedInline):
    model = Wallet
    can_delete = False
    verbose_name_plural = 'Wallet'
    fk_name = 'user'
    max_num = 1
    fields = ('balance', 'points')
    readonly_fields = ('created_at', 'updated_at')

class KYCVerificationInline(admin.TabularInline):
    model = KYCVerification
    extra = 0
    fk_name = 'user'
    fields = ('document_type', 'status', 'document_number', 'verified_by', 'verified_at', 'created_at')
    readonly_fields = ('created_at', 'verified_at')
    raw_id_fields = ('verified_by',)

class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, WalletInline, KYCVerificationInline)
    list_display = ('email', 'full_name', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'is_verified', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    date_hierarchy = 'date_joined'
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')
    
    fieldsets = (
        (_('Basic Info'), {
            'fields': ('email', 'password', 'first_name', 'second_name', 'last_name', 'phone')
        }),
        (_('Details'), {
            'fields': ('bio', 'avatar_url')
        }),
        (_('Role & Status'), {
            'fields': ('role', 'is_active', 'is_verified', 'is_email_verified', 'auth_provider'),
            'description': _('User role determines access and features available')
        }),
        (_('Permissions'), {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Premium'), {
            'fields': ('premium_until', 'points', 'referral_code')
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
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
# UserProfile is now managed as inline in User
# Removed separate admin registration to simplify UI

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

# Business Document Inline - Tabular for better table view
class BusinessDocumentInline(admin.TabularInline):
    model = BusinessDocument
    extra = 0
    fields = ('document_type', 'file_name', 'is_verified', 'verified_by', 'verified_at', 'created_at')
    readonly_fields = ('verified_at', 'created_at')
    raw_id_fields = ('verified_by',)
    can_delete = True
    verbose_name_plural = 'Business Documents'
    classes = ('collapse',)
    fk_name = 'business'

# Business Member Inline - Tabular for better table view
class BusinessMemberInline(admin.TabularInline):
    model = BusinessMember
    extra = 0
    fields = ('user', 'role', 'joined_at')
    readonly_fields = ('joined_at',)
    raw_id_fields = ('user',)
    verbose_name_plural = 'Team Members'

@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user_email', 'business_type', 'industry', 'is_verified', 'doc_count', 'member_count', 'created_at')
    list_filter = ('business_type', 'industry', 'is_verified', 'created_at')
    search_fields = ('business_name', 'user__email', 'description', 'industry')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user',)
    list_per_page = 25
    list_display_links = ('business_name',)
    inlines = [BusinessMemberInline, BusinessDocumentInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'business_name', 'business_type', 'industry')
        }),
        ('Details', {
            'fields': ('description', 'location', 'website', 'logo_url'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_verified', 'collaboration_types', 'goals')
        }),
    )
    show_full_result_count = False
    
    def user_email(self, obj):
        return obj.user.email if obj.user else '-'
    user_email.short_description = 'Owner Email'
    user_email.admin_order_field = 'user__email'
    
    def doc_count(self, obj):
        # Prefer documents linked directly to the business, fallback to user uploads
        count = obj.documents.count() if hasattr(obj, 'documents') else 0
        if count == 0 and obj.user:
            count = obj.user.uploaded_documents.count()
        return format_html('<span style="color: {};">{}</span>', 
                         'green' if count > 0 else 'gray', count)
    doc_count.short_description = 'Documents'
    doc_count.admin_order_field = 'user__uploaded_documents__count'
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'
    member_count.admin_order_field = 'members__count'

# BusinessMember is now managed as inline in BusinessProfile
# Removed separate admin registration to simplify UI

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'business_name', 'category', 'is_active', 'claims_info', 'claimed_by_button', 'start_date', 'end_date')
    list_filter = ('category', 'is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'business__business_name')
    date_hierarchy = 'start_date'
    raw_id_fields = ('business',)
    list_per_page = 25
    list_display_links = ('title',)
    readonly_fields = ('created_at', 'updated_at')
    show_full_result_count = False
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('business', 'title', 'category', 'description')
        }),
        ('Promotion Details', {
            'fields': ('image_url', 'start_date', 'end_date', 'is_active', 'max_claims', 'current_claims', 'points_cost')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def business_name(self, obj):
        return obj.business.business_name if obj.business else '-'
    business_name.short_description = 'Business'
    business_name.admin_order_field = 'business__business_name'
    
    def claims_info(self, obj):
        return format_html('{}/{}', obj.current_claims, obj.max_claims)
    claims_info.short_description = 'Claims'

    def claimed_by_button(self, obj):
        count = obj.claims.count()
        url = f"{reverse('admin:broker_promotionclaim_changelist')}?promotion__id__exact={obj.id}"
        return format_html('<a class="button" href="{}">View claimants ({})</a>', url, count)
    claimed_by_button.short_description = 'Claimed By'

@admin.register(PromotionClaim)
class PromotionClaimAdmin(admin.ModelAdmin):
    # Show claimant next to timestamp for quicker scanning
    list_display = ('user_email', 'claimed_at', 'promotion_title', 'points', 'shared_count')
    list_filter = ('claimed_at',)
    search_fields = ('promotion__title', 'user__email')
    date_hierarchy = 'claimed_at'
    raw_id_fields = ('promotion', 'user')
    list_per_page = 25
    list_display_links = ('promotion_title',)
    readonly_fields = ('claimed_at', 'updated_at')
    show_full_result_count = False
    
    def promotion_title(self, obj):
        return obj.promotion.title if obj.promotion else '-'
    promotion_title.short_description = 'Promotion'
    promotion_title.admin_order_field = 'promotion__title'
    
    def user_email(self, obj):
        return obj.user.email if obj.user else '-'
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_email', 'amount', 'transaction_type', 'status', 'description_short', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('user__email', 'reference', 'description')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user',)
    list_per_page = 25
    list_display_links = ('id',)
    readonly_fields = ('created_at', 'updated_at')
    show_full_result_count = False
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('user', 'amount', 'transaction_type', 'status')
        }),
        ('Additional Info', {
            'fields': ('description', 'reference', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email if obj.user else '-'
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def description_short(self, obj):
        if obj.description:
            return obj.description[:50] + ('...' if len(obj.description) > 50 else '')
        return '-'
    description_short.short_description = 'Description'

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'balance', 'points', 'formatted_balance', 'updated_at')
    search_fields = ('user__email',)
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    list_display_links = ('user_email',)
    show_full_result_count = False
    
    fieldsets = (
        ('Wallet Info', {
            'fields': ('user', 'balance', 'points')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email if obj.user else '-'
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def formatted_balance(self, obj):
        return format_html('<strong>${:,.2f}</strong>', float(obj.balance or 0))
    formatted_balance.short_description = 'Balance'
    formatted_balance.admin_order_field = 'balance'

@admin.register(KYCVerification)
class KYCVerificationAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'document_type', 'status_badge', 'document_number', 'verified_by_email', 'created_at', 'verified_at')
    list_filter = ('document_type', 'status', 'created_at', 'verified_at')
    search_fields = ('user__email', 'document_number')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user', 'verified_by')
    list_per_page = 25
    list_display_links = ('user_email',)
    readonly_fields = ('created_at', 'updated_at', 'verified_at')
    show_full_result_count = False
    
    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Document Details', {
            'fields': ('document_type', 'document_number', 'document_front', 'document_back', 'selfie')
        }),
        ('Verification', {
            'fields': ('status', 'rejection_reason', 'verified_by', 'verified_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email if obj.user else '-'
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def verified_by_email(self, obj):
        return obj.verified_by.email if obj.verified_by else '-'
    verified_by_email.short_description = 'Verified By'
    verified_by_email.admin_order_field = 'verified_by__email'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': 'orange',
            'APPROVED': 'green',
            'REJECTED': 'red',
            'SUSPENDED': 'gray',
            'DELETED': 'black'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

# BusinessDocument is now managed as inline in BusinessProfile
# Removed separate admin registration to simplify UI

# Campaign Collaborator Inline
class CampaignCollaboratorInline(admin.TabularInline):
    model = CampaignCollaborator
    extra = 0
    fields = ('user', 'role', 'status', 'joined_at')
    readonly_fields = ('joined_at',)
    raw_id_fields = ('user',)
    verbose_name_plural = 'Collaborators'

# Campaign Product Inline
class CampaignProductInline(admin.TabularInline):
    model = CampaignProduct
    extra = 0
    fields = ('listing', 'status', 'commission_rate')
    raw_id_fields = ('listing',)
    verbose_name_plural = 'Products'

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'business_name', 'status', 'budget', 'collab_count', 'product_count', 'start_date', 'end_date')
    list_filter = ('status', 'start_date', 'end_date', 'is_public')
    search_fields = ('name', 'description', 'business__business_name')
    date_hierarchy = 'start_date'
    raw_id_fields = ('business', 'created_by')
    list_per_page = 25
    list_display_links = ('name',)
    inlines = [CampaignCollaboratorInline, CampaignProductInline]
    readonly_fields = ('created_at', 'updated_at')
    show_full_result_count = False
    
    fieldsets = (
        ('Campaign Info', {
            'fields': ('name', 'description', 'business', 'created_by', 'status')
        }),
        ('Dates & Budget', {
            'fields': ('start_date', 'end_date', 'budget', 'is_public')
        }),
        ('Target Audience', {
            'fields': ('target_audience', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def business_name(self, obj):
        return obj.business.business_name if obj.business else '-'
    business_name.short_description = 'Business'
    business_name.admin_order_field = 'business__business_name'
    
    def collab_count(self, obj):
        return obj.collaborators.count()
    collab_count.short_description = 'Collaborators'
    
    def product_count(self, obj):
        # Count related CampaignProduct items via the correct related_name
        return obj.campaign_products.count()
    product_count.short_description = 'Products'

# CampaignCollaborator is now managed as inline in Campaign
# Removed separate admin registration to simplify UI

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'listing_type', 'price', 'status', 'user_email', 'business_name', 'is_active', 'created_at')
    list_filter = ('listing_type', 'status', 'category', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'user__email', 'business__business_name', 'category')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user', 'business')
    list_per_page = 25
    list_display_links = ('title',)
    readonly_fields = ('created_at', 'updated_at')
    show_full_result_count = False
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'listing_type', 'category', 'price')
        }),
        ('Owner', {
            'fields': ('user', 'business')
        }),
        ('Details', {
            'fields': ('tags', 'is_negotiable', 'is_for_collaboration', 'quantity', 'min_order', 'max_order', 'lead_time')
        }),
        ('Status', {
            'fields': ('status', 'is_active', 'commission_rate')
        }),
        ('Media', {
            'fields': ('image_urls', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email if obj.user else '-'
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def business_name(self, obj):
        return obj.business.business_name if obj.business else '-'
    business_name.short_description = 'Business'
    business_name.admin_order_field = 'business__business_name'

# Message Inline
class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ('sender', 'message_type', 'content_preview', 'is_read', 'created_at')
    readonly_fields = ('created_at', 'content_preview')
    raw_id_fields = ('sender',)
    verbose_name_plural = 'Messages'
    classes = ('collapse',)
    
    def content_preview(self, obj):
        if obj.content:
            return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
        return '-'
    content_preview.short_description = 'Content'

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing_title', 'buyer_email', 'seller_email', 'status', 'message_count', 'last_message_at')
    list_filter = ('status', 'last_message_at')
    search_fields = ('listing__title', 'buyer__email', 'seller__email')
    date_hierarchy = 'last_message_at'
    raw_id_fields = ('listing', 'buyer', 'seller')
    list_per_page = 25
    list_display_links = ('id',)
    inlines = [MessageInline]
    readonly_fields = ('created_at', 'updated_at')
    show_full_result_count = False
    
    fieldsets = (
        ('Conversation', {
            'fields': ('listing', 'buyer', 'seller', 'status')
        }),
        ('Timestamps', {
            'fields': ('last_message_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def listing_title(self, obj):
        return obj.listing.title if obj.listing else '-'
    listing_title.short_description = 'Listing'
    listing_title.admin_order_field = 'listing__title'
    
    def buyer_email(self, obj):
        return obj.buyer.email if obj.buyer else '-'
    buyer_email.short_description = 'Buyer'
    buyer_email.admin_order_field = 'buyer__email'
    
    def seller_email(self, obj):
        return obj.seller.email if obj.seller else '-'
    seller_email.short_description = 'Seller'
    seller_email.admin_order_field = 'seller__email'
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'

# Message is now managed as inline in Conversation
# Removed separate admin registration to simplify UI

# CampaignProduct is now managed as inline in Campaign
# Removed separate admin registration to simplify UI


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

# -----------------------------
# Custom Group (Authorization) Admin
# -----------------------------

class PermissionAppFilter(admin.SimpleListFilter):
    title = 'App label'
    parameter_name = 'app_label'

    def lookups(self, request, model_admin):
        apps = Permission.objects.values_list('content_type__app_label', flat=True).distinct().order_by('content_type__app_label')
        return [(a, a) for a in apps]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(permissions__content_type__app_label=self.value()).distinct()
        return queryset

class PermissionCodePrefixFilter(admin.SimpleListFilter):
    title = 'Permission code starts with'
    parameter_name = 'codename_starts'

    def lookups(self, request, model_admin):
        return (
            ('add_', 'add_'),
            ('change_', 'change_'),
            ('delete_', 'delete_'),
            ('view_', 'view_'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(permissions__codename__startswith=self.value()).distinct()
        return queryset

try:
    admin.site.unregister(Group)
except NotRegistered:
    pass

@admin.register(Group)
class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'permission_count')
    search_fields = ('name', 'permissions__name', 'permissions__codename')
    list_filter = (PermissionAppFilter, PermissionCodePrefixFilter)
    filter_horizontal = ('permissions',)
    actions = ('apply_readonly_policy', 'apply_business_manager_policy')

    fieldsets = (
        ('Basic Info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('permissions',)}),
    )

    def permission_count(self, obj):
        return obj.permissions.count()
    permission_count.short_description = 'Permissions'

    # --- Policy presets ---
    def _set_perms(self, group, perms_qs):
        group.permissions.set(perms_qs.distinct())
        group.save()

    @admin.action(description='Apply Read-only policy (view_* on broker & product)')
    def apply_readonly_policy(self, request, queryset):
        perms = Permission.objects.filter(
            content_type__app_label__in=['broker', 'product'],
            codename__startswith='view_'
        )
        for group in queryset:
            self._set_perms(group, perms)

    @admin.action(description='Apply Business Manager policy (view_* all, change on Promotion & Listing)')
    def apply_business_manager_policy(self, request, queryset):
        view_perms = Permission.objects.filter(codename__startswith='view_')
        change_targets = ['change_promotion', 'change_listing']
        change_perms = Permission.objects.filter(codename__in=change_targets)
        perms = view_perms.union(change_perms)
        for group in queryset:
            self._set_perms(group, perms)
