# broker/api/v1/urls/router.py
"""
Comprehensive API router configuration
Registers all API endpoints with optimized viewsets
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

# Import all viewsets
from ..views.user import UserProfileViewSet, UserSocialLinkViewSet
from ..views.business import BusinessProfileViewSet, BusinessMemberViewSet
from ..views.campaign import CampaignViewSet, CampaignCollaboratorViewSet, CampaignProductViewSet
from ..views.promotion import PromotionViewSet, PromotionClaimViewSet
from ..views.transaction import TransactionViewSet, WalletViewSet
from ..views.kyc import KYCVerificationViewSet
from ..views.listing import ListingViewSet
from ..views.conversation import ConversationViewSet, MessageViewSet
from ..views.admin_dashboard import dashboard_stats_api

# Create main router
router = DefaultRouter()
router.include_format_suffixes = False

# Register all viewsets
router.register(r'profiles', UserProfileViewSet, basename='user-profile')
router.register(r'social-links', UserSocialLinkViewSet, basename='user-social-link')

# Business endpoints
# BusinessDocument is managed as nested resource under BusinessProfile via API
router.register(r'businesses', BusinessProfileViewSet, basename='business-profile')
router.register(r'business-members', BusinessMemberViewSet, basename='business-member')
# Removed business-documents endpoint - use nested endpoint under businesses instead

# Campaign endpoints
router.register(r'campaigns', CampaignViewSet, basename='campaign')
router.register(r'campaign-collaborators', CampaignCollaboratorViewSet, basename='campaign-collaborator')
router.register(r'campaign-products', CampaignProductViewSet, basename='campaign-product')

# Promotion endpoints
router.register(r'promotions', PromotionViewSet, basename='promotion')
router.register(r'promotion-claims', PromotionClaimViewSet, basename='promotion-claim')

# Transaction endpoints
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'wallets', WalletViewSet, basename='wallet')

# KYC endpoints
router.register(r'kyc', KYCVerificationViewSet, basename='kyc-verification')

# Listing endpoints
router.register(r'listings', ListingViewSet, basename='listing')
# DraftOrder was removed - use product.Order instead

# Conversation endpoints
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# Nested routers for related resources
campaigns_router = routers.NestedSimpleRouter(router, r'campaigns', lookup='campaign')
campaigns_router.include_format_suffixes = False
campaigns_router.register(r'collaborators', CampaignCollaboratorViewSet, basename='campaign-collaborators')
campaigns_router.register(r'products', CampaignProductViewSet, basename='campaign-products')

conversations_router = routers.NestedSimpleRouter(router, r'conversations', lookup='conversation')
conversations_router.include_format_suffixes = False
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    # Admin dashboard API
    path('admin/dashboard/stats/', dashboard_stats_api, name='admin-dashboard-stats'),
    # All other endpoints
    path('', include(router.urls)),
    path('', include(campaigns_router.urls)),
    path('', include(conversations_router.urls)),
]
