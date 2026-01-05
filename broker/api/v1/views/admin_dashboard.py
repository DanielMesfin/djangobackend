# broker/api/v1/views/admin_dashboard.py
"""
Admin Dashboard API endpoints for AJAX updates
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.cache import cache
from broker.admin_dashboard import get_dashboard_stats


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def dashboard_stats_api(request):
    """
    API endpoint to get dashboard statistics
    Returns cached statistics that can be refreshed
    """
    days = int(request.GET.get('days', 30))
    refresh = request.GET.get('refresh', 'false').lower() == 'true'
    
    if refresh:
        # Clear cache and get fresh data
        cache.delete(f'dashboard_stats_{days}')
    
    stats = get_dashboard_stats(days=days)
    
    return Response({
        'success': True,
        'data': stats,
        'cache_refreshed': refresh
    })
