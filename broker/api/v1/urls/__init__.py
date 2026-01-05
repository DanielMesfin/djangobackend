# broker/api/v1/urls/__init__.py
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .auth import urlpatterns as auth_urls
from .router import urlpatterns as router_urls

@api_view(['GET'])
def api_root(request):
    """
    API root endpoint - provides links to all available endpoints
    """
    return Response({
        'auth': {
            'register': '/api/v1/auth/register/',
            'login': '/api/v1/auth/login/',
            'change-password': '/api/v1/auth/change-password/',
            'logout': '/api/v1/auth/logout/',
        },
        'user': {
            'profiles': '/api/v1/profiles/',
            'social-links': '/api/v1/social-links/',
        },
        'business': {
            'businesses': '/api/v1/businesses/',
            'business-members': '/api/v1/business-members/',
            'note': 'Business documents are managed as nested resources under businesses',
        },
        'campaign': {
            'campaigns': '/api/v1/campaigns/',
            'campaign-collaborators': '/api/v1/campaign-collaborators/',
            'campaign-products': '/api/v1/campaign-products/',
        },
        'promotion': {
            'promotions': '/api/v1/promotions/',
            'promotion-claims': '/api/v1/promotion-claims/',
        },
        'transaction': {
            'transactions': '/api/v1/transactions/',
            'wallets': '/api/v1/wallets/',
        },
        'kyc': {
            'kyc-verifications': '/api/v1/kyc/',
        },
        'listing': {
            'listings': '/api/v1/listings/',
            'draft-orders': '/api/v1/draft-orders/',
        },
        'conversation': {
            'conversations': '/api/v1/conversations/',
            'messages': '/api/v1/messages/',
        },
        'admin': {
            'dashboard-stats': '/api/v1/admin/dashboard/stats/',
        },
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('auth/', include(auth_urls)),
    path('', include(router_urls)),
]