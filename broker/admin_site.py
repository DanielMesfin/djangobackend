from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from django.urls import path, reverse
from django.views.i18n import JavaScriptCatalog
from django.http import HttpResponseRedirect

User = get_user_model()

class BrokerAdminSite(admin.AdminSite):
    site_header = 'Broker Admin'
    site_title = 'Broker Admin'
    index_title = 'Dashboard'
    login_form = AuthenticationForm
    login_template = 'admin/login.html'
    
    def has_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def get_urls(self):
        from django.urls import include
        urls = super().get_urls()
        
        # Add custom URLs
        custom_urls = [
            path('jsi18n/', JavaScriptCatalog.as_view(), name='jsi18n'),
            path('', self.admin_view(self.admin_dashboard), name='index'),
        ]
        
        return custom_urls + urls
    
    def admin_dashboard(self, request, extra_context=None):
        # Redirect to the default admin index
        return HttpResponseRedirect(reverse('admin:index'))

    def _build_app_dict(self, request, label=None):
        """
        Build the app dictionary for the admin index.
        Uses the default implementation for simplicity.
        """
        return super()._build_app_dict(request, label)

# Create an instance of our custom admin site
broker_admin_site = BrokerAdminSite(name='broker_admin')

# Register models with the admin site
broker_admin_site.register(Group, GroupAdmin)

# Note: The User model should be registered in the app's admin.py file
# This keeps the admin configuration close to the app it belongs to
