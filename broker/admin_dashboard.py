from django.contrib import admin
from django.db.models import Count, Sum, Q, Avg
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
import json

try:
    from .models import (
        User, UserProfile, BusinessProfile, BusinessMember,
        Promotion, PromotionClaim, Transaction, Wallet,
        KYCVerification, BusinessDocument, Campaign, CampaignCollaborator,
        CampaignProduct, Listing, Conversation, Message
    )
    from product.models import Product, Order, OrderItem, Review, Category
except ImportError:
    # Handle import errors gracefully
    pass


def get_dashboard_stats(days=30):
    """
    Get comprehensive dashboard statistics with optimized queries
    Uses caching and database optimizations for better performance
    """
    cache_key = f'dashboard_stats_{days}'
    cached_stats = cache.get(cache_key)
    
    if cached_stats:
        return cached_stats
    
    now = timezone.now()
    today = now.date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=days)
    
    # Optimized User Statistics - single query with aggregations
    user_stats = User.objects.aggregate(
        total=Count('id'),
        active=Count('id', filter=Q(is_active=True)),
        verified=Count('id', filter=Q(is_verified=True)),
        new_today=Count('id', filter=Q(date_joined__date=today)),
        new_week=Count('id', filter=Q(date_joined__date__gte=week_ago)),
        new_month=Count('id', filter=Q(date_joined__date__gte=month_ago))
    )
    
    # Business Statistics - optimized with select_related
    business_stats = BusinessProfile.objects.aggregate(
        total=Count('id'),
        verified=Count('id', filter=Q(is_verified=True)),
        new_month=Count('id', filter=Q(created_at__date__gte=month_ago))
    )
    
    # Transaction Statistics - single aggregation query
    transaction_stats = Transaction.objects.aggregate(
        total_count=Count('id'),
        total_amount=Sum('amount'),
        today_count=Count('id', filter=Q(created_at__date=today)),
        month_count=Count('id', filter=Q(created_at__date__gte=month_ago)),
        pending=Count('id', filter=Q(status='pending'))
    )
    
    # Wallet Statistics - single aggregation
    wallet_stats = Wallet.objects.aggregate(
        total=Count('id'),
        total_balance=Sum('balance'),
        total_points=Sum('points')
    )
    
    # Campaign Statistics - optimized query
    campaign_stats = Campaign.objects.aggregate(
        total=Count('id'),
        active=Count('id', filter=Q(status='ACTIVE')),
        draft=Count('id', filter=Q(status='DRAFT'))
    )
    
    # Promotion Statistics
    promotion_stats = Promotion.objects.aggregate(
        total=Count('id'),
        active=Count('id', filter=Q(is_active=True))
    )
    total_claims = PromotionClaim.objects.count()
    
    # Listing Statistics
    listing_stats = Listing.objects.aggregate(
        total=Count('id'),
        active=Count('id', filter=Q(is_active=True, status='PUBLISHED')),
        draft=Count('id', filter=Q(status='DRAFT'))
    )
    
    # Product Statistics - optimized
    product_stats = Product.objects.aggregate(
        total=Count('id')
    )
    order_stats = Order.objects.aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='pending'))
    )
    total_reviews = Review.objects.count()
    
    # Conversation Statistics
    conversation_stats = Conversation.objects.aggregate(
        total=Count('id'),
        active=Count('id', filter=Q(status='ACTIVE'))
    )
    total_messages = Message.objects.count()
    
    # KYC Statistics
    kyc_stats = KYCVerification.objects.aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='PENDING')),
        approved=Count('id', filter=Q(status='APPROVED'))
    )
    
    # Recent Activity - optimized with select_related/prefetch_related
    recent_users = User.objects.filter(
        date_joined__date__gte=week_ago
    ).select_related('profile').order_by('-date_joined')[:5]
    
    recent_transactions = Transaction.objects.filter(
        created_at__date__gte=week_ago
    ).select_related('sender', 'recipient').order_by('-created_at')[:5]
    
    recent_orders = Order.objects.filter(
        order_date__date__gte=week_ago
    ).select_related('buyer').order_by('-order_date')[:5]
    
    # User growth data (last N days) - using TruncDate instead of .extra()
    try:
        user_growth = User.objects.filter(
            date_joined__gte=month_ago
        ).annotate(
            day=TruncDate('date_joined')
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
    except Exception as e:
        user_growth = []
    
    # Transaction data (last N days) - optimized with TruncDate
    try:
        transaction_growth = Transaction.objects.filter(
            created_at__gte=month_ago
        ).annotate(
            day=TruncDate('created_at')
        ).values('day').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('day')
    except Exception as e:
        transaction_growth = []
    
    stats = {
        'users': {
            'total': user_stats['total'] or 0,
            'new_today': user_stats['new_today'] or 0,
            'new_week': user_stats['new_week'] or 0,
            'new_month': user_stats['new_month'] or 0,
            'active': user_stats['active'] or 0,
            'verified': user_stats['verified'] or 0,
            'growth_data': [{'day': str(item['day']), 'count': item['count']} for item in user_growth],
        },
        'businesses': {
            'total': business_stats['total'] or 0,
            'verified': business_stats['verified'] or 0,
            'new_month': business_stats['new_month'] or 0,
        },
        'transactions': {
            'total': transaction_stats['total_count'] or 0,
            'total_amount': float(transaction_stats['total_amount'] or 0),
            'today': transaction_stats['today_count'] or 0,
            'month': transaction_stats['month_count'] or 0,
            'pending': transaction_stats['pending'] or 0,
            'growth_data': [{
                'day': str(item['day']), 
                'count': item['count'],
                'total': float(item['total'] or 0)
            } for item in transaction_growth],
        },
        'wallets': {
            'total': wallet_stats['total'] or 0,
            'total_balance': float(wallet_stats['total_balance'] or 0),
            'total_points': wallet_stats['total_points'] or 0,
        },
        'campaigns': {
            'total': campaign_stats['total'] or 0,
            'active': campaign_stats['active'] or 0,
            'draft': campaign_stats['draft'] or 0,
        },
        'promotions': {
            'total': promotion_stats['total'] or 0,
            'active': promotion_stats['active'] or 0,
            'total_claims': total_claims or 0,
        },
        'listings': {
            'total': listing_stats['total'] or 0,
            'active': listing_stats['active'] or 0,
            'draft': listing_stats['draft'] or 0,
        },
        'products': {
            'total': product_stats['total'] or 0,
            'total_orders': order_stats['total'] or 0,
            'total_reviews': total_reviews or 0,
            'pending_orders': order_stats['pending'] or 0,
        },
        'conversations': {
            'total': conversation_stats['total'] or 0,
            'active': conversation_stats['active'] or 0,
            'total_messages': total_messages or 0,
        },
        'kyc': {
            'pending': kyc_stats['pending'] or 0,
            'approved': kyc_stats['approved'] or 0,
            'total': kyc_stats['total'] or 0,
        },
        'recent': {
            'users': list(recent_users.values('id', 'email', 'first_name', 'last_name', 'date_joined')),
            'transactions': list(recent_transactions.values('id', 'amount', 'transaction_type', 'status', 'created_at')),
            'orders': list(recent_orders.values('id', 'total_amount', 'status', 'order_date')),
        },
    }
    
    # Cache for 5 minutes
    cache.set(cache_key, stats, 300)
    
    return stats


def admin_dashboard_view(request):
    """Modern admin dashboard view with optimized queries and caching"""
    from django.contrib import admin
    from django.http import JsonResponse
    from django.views.decorators.cache import cache_page
    
    # Handle AJAX requests for real-time updates
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        days = int(request.GET.get('days', 30))
        stats = get_dashboard_stats(days=days)
        # Clear cache on AJAX refresh to get fresh data
        cache.delete(f'dashboard_stats_{days}')
        stats = get_dashboard_stats(days=days)
        return JsonResponse(stats)
    
    # Get date range from query params
    days = int(request.GET.get('days', 30))
    
    stats = get_dashboard_stats(days=days)
    
    # Get the default admin context
    context = admin.site.each_context(request)
    context.update({
        'title': 'Dashboard',
        'stats': stats,
        'has_permission': request.user.is_staff,
        'opts': {'app_label': 'admin', 'model_name': 'dashboard'},
        'date_range_days': days,
    })
    
    return TemplateResponse(request, 'admin/dashboard.html', context)

