from django.contrib import admin
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

try:
    from .models import (
        User, UserProfile, BusinessProfile, BusinessMember,
        Promotion, PromotionClaim, Transaction, Wallet,
        KYCVerification, BusinessDocument, Campaign, CampaignCollaborator,
        CampaignProduct, Listing, Conversation, Message, DraftOrder
    )
    from product.models import Product, Order, OrderItem, Review, Category
except ImportError:
    # Handle import errors gracefully
    pass


def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    now = timezone.now()
    today = now.date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # User Statistics
    total_users = User.objects.count()
    new_users_today = User.objects.filter(date_joined__date=today).count()
    new_users_week = User.objects.filter(date_joined__date__gte=week_ago).count()
    new_users_month = User.objects.filter(date_joined__date__gte=month_ago).count()
    active_users = User.objects.filter(is_active=True).count()
    verified_users = User.objects.filter(is_verified=True).count()
    
    # Business Statistics
    total_businesses = BusinessProfile.objects.count()
    verified_businesses = BusinessProfile.objects.filter(is_verified=True).count()
    new_businesses_month = BusinessProfile.objects.filter(created_at__date__gte=month_ago).count()
    
    # Transaction Statistics
    total_transactions = Transaction.objects.count()
    total_transaction_amount = Transaction.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0
    transactions_today = Transaction.objects.filter(created_at__date=today).count()
    transactions_month = Transaction.objects.filter(created_at__date__gte=month_ago).count()
    pending_transactions = Transaction.objects.filter(status='pending').count()
    
    # Wallet Statistics
    total_wallets = Wallet.objects.count()
    total_balance = Wallet.objects.aggregate(
        total=Sum('balance')
    )['total'] or 0
    total_points = Wallet.objects.aggregate(
        total=Sum('points')
    )['total'] or 0
    
    # Campaign Statistics
    total_campaigns = Campaign.objects.count()
    active_campaigns = Campaign.objects.filter(status='ACTIVE').count()
    draft_campaigns = Campaign.objects.filter(status='DRAFT').count()
    
    # Promotion Statistics
    total_promotions = Promotion.objects.count()
    active_promotions = Promotion.objects.filter(is_active=True).count()
    total_claims = PromotionClaim.objects.count()
    
    # Listing Statistics
    total_listings = Listing.objects.count()
    active_listings = Listing.objects.filter(is_active=True, status='PUBLISHED').count()
    draft_listings = Listing.objects.filter(status='DRAFT').count()
    
    # Product Statistics
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_reviews = Review.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    
    # Conversation Statistics
    total_conversations = Conversation.objects.count()
    active_conversations = Conversation.objects.filter(status='ACTIVE').count()
    total_messages = Message.objects.count()
    
    # KYC Statistics
    pending_kyc = KYCVerification.objects.filter(status='PENDING').count()
    approved_kyc = KYCVerification.objects.filter(status='APPROVED').count()
    total_kyc = KYCVerification.objects.count()
    
    # Recent Activity (last 7 days)
    recent_users = User.objects.filter(date_joined__date__gte=week_ago).order_by('-date_joined')[:5]
    recent_transactions = Transaction.objects.filter(created_at__date__gte=week_ago).order_by('-created_at')[:5]
    recent_orders = Order.objects.filter(order_date__date__gte=week_ago).order_by('-order_date')[:5]
    
    # User growth data (last 30 days)
    try:
        user_growth = User.objects.filter(
            date_joined__date__gte=month_ago
        ).extra(
            select={'day': 'date(date_joined)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
    except:
        user_growth = []
    
    # Transaction data (last 30 days)
    try:
        transaction_growth = Transaction.objects.filter(
            created_at__date__gte=month_ago
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('day')
    except:
        transaction_growth = []
    
    return {
        'users': {
            'total': total_users,
            'new_today': new_users_today,
            'new_week': new_users_week,
            'new_month': new_users_month,
            'active': active_users,
            'verified': verified_users,
            'growth_data': list(user_growth),
        },
        'businesses': {
            'total': total_businesses,
            'verified': verified_businesses,
            'new_month': new_businesses_month,
        },
        'transactions': {
            'total': total_transactions,
            'total_amount': float(total_transaction_amount),
            'today': transactions_today,
            'month': transactions_month,
            'pending': pending_transactions,
            'growth_data': list(transaction_growth),
        },
        'wallets': {
            'total': total_wallets,
            'total_balance': float(total_balance),
            'total_points': total_points,
        },
        'campaigns': {
            'total': total_campaigns,
            'active': active_campaigns,
            'draft': draft_campaigns,
        },
        'promotions': {
            'total': total_promotions,
            'active': active_promotions,
            'total_claims': total_claims,
        },
        'listings': {
            'total': total_listings,
            'active': active_listings,
            'draft': draft_listings,
        },
        'products': {
            'total': total_products,
            'total_orders': total_orders,
            'total_reviews': total_reviews,
            'pending_orders': pending_orders,
        },
        'conversations': {
            'total': total_conversations,
            'active': active_conversations,
            'total_messages': total_messages,
        },
        'kyc': {
            'pending': pending_kyc,
            'approved': approved_kyc,
            'total': total_kyc,
        },
        'recent': {
            'users': recent_users,
            'transactions': recent_transactions,
            'orders': recent_orders,
        },
    }


def admin_dashboard_view(request):
    """Modern admin dashboard view"""
    from django.contrib import admin
    from django.http import JsonResponse
    
    # Handle AJAX requests for real-time updates
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        stats = get_dashboard_stats()
        return JsonResponse(stats)
    
    # Get date range from query params
    days = int(request.GET.get('days', 30))
    
    stats = get_dashboard_stats()
    
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

