from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

class RoleBasedAdminSite(admin.AdminSite):
    """Custom admin site with role-based access control"""
    
    def has_permission(self, request):
        """
        Only superusers can access the admin site by default
        """
        return request.user.is_active and request.user.is_staff and request.user.is_superuser

# Create custom admin site
admin_site = RoleBasedAdminSite(name='admin')

class UserRoleFilter(admin.SimpleListFilter):
    """Filter users by role"""
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

class UserAdmin(BaseUserAdmin):
    """Custom User admin with role-based fields and filtering"""
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = (UserRoleFilter, 'is_active', 'is_staff', 'is_superuser')
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
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # For non-superusers, only show their own profile
            return qs.filter(pk=request.user.pk)
        return qs

# Register the custom admin classes
admin_site.register(User, UserAdmin)

# Import and register other models with their custom admin classes
from .models import (
    BusinessProfile, BusinessMember, Campaign, CampaignCollaborator,
    Promotion, PromotionClaim
)

@admin.register(BusinessProfile, site=admin_site)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('name', 'description', 'owner__email')
    raw_id_fields = ('owner',)

@admin.register(BusinessMember, site=admin_site)
class BusinessMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'business', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('user__email', 'business__name')
    raw_id_fields = ('user', 'business')

@admin.register(Campaign, site=admin_site)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'business', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('name', 'description', 'business__name')
    raw_id_fields = ('business',)
    filter_horizontal = ('products',)

@admin.register(CampaignCollaborator, site=admin_site)
class CampaignCollaboratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'campaign', 'role', 'status')
    list_filter = ('role', 'status')
    search_fields = ('user__email', 'campaign__name')
    raw_id_fields = ('user', 'campaign')

@admin.register(Promotion, site=admin_site)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'business', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'business__name')
    raw_id_fields = ('business',)

@admin.register(PromotionClaim, site=admin_site)
class PromotionClaimAdmin(admin.ModelAdmin):
    list_display = ('promotion', 'user', 'status', 'claimed_at')
    list_filter = ('status', 'claimed_at')
    search_fields = ('promotion__title', 'user__email')
    raw_id_fields = ('promotion', 'user')

# Update the default admin site
admin.site = admin_site
