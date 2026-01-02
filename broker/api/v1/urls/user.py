# broker/api/v1/urls/user.py
from django.urls import path
from rest_framework.routers import SimpleRouter

# Create a module-level router that will be initialized only once
router = SimpleRouter()

def get_user_urlpatterns():
    from broker.api.v1.views.user import UserProfileViewSet, UserSocialLinkViewSet
    if not router.registry:
        router.register(r'profiles', UserProfileViewSet, basename='user-profile')
        router.register(r'social-links', UserSocialLinkViewSet, basename='user-social-link')
    return router.urls

# Initialize URL patterns
urlpatterns = get_user_urlpatterns()