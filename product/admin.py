# product/admin.py
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django import forms

from .models import Category, Product, Order, OrderItem, Review

class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        help_texts = {
            'name': 'Enter a descriptive name for the category',
            'description': 'Provide details about this category',
        }

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    list_display = ('name', 'product_count', 'description')
    search_fields = ('name', 'description')
    list_filter = ()
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _product_count=Count('products', distinct=True)
        )
    
    def product_count(self, obj):
        return obj._product_count
    product_count.admin_order_field = '_product_count'

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'seller', 'category', 'price', 'stock_status', 'created_at')
    list_filter = ('category', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'seller__email', 'category__name')
    list_select_related = ('seller', 'category')
    date_hierarchy = 'created_at'
    raw_id_fields = ('seller', 'category')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('price',)
    list_per_page = 20
    show_full_result_count = False
    
    def stock_status(self, obj):
        if obj.stock < 10:
            return format_html('<span style="color: red;">{}</span>', f'Low ({obj.stock})')
        return obj.stock
    stock_status.admin_order_field = 'stock'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ('product',)
    readonly_fields = ('subtotal',)
    fields = ('product', 'quantity', 'price', 'subtotal')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')
    
    def subtotal(self, obj):
        return obj.quantity * obj.price
    subtotal.short_description = 'Subtotal'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'order_date', 'status', 'total_amount', 'item_count')
    list_filter = ('status', 'order_date')
    search_fields = (
        'buyer__email', 'buyer__first_name', 'buyer__last_name',
        'shipping_address', 'id'
    )
    date_hierarchy = 'order_date'
    inlines = [OrderItemInline]
    raw_id_fields = ('buyer',)
    actions = ['mark_as_shipped']
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('buyer')
    
    @admin.action(description='Mark selected orders as shipped')
    def mark_as_shipped(self, request, queryset):
        updated = queryset.filter(status='processing').update(status='shipped')
        self.message_user(
            request,
            f'Successfully marked {updated} order(s) as shipped.',
            level='success'
        )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_link', 'user_link', 'rating_stars', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = (
        'product__name', 'user__email', 'user__first_name',
        'user__last_name', 'comment'
    )
    date_hierarchy = 'created_at'
    raw_id_fields = ('product', 'user')
    readonly_fields = ('created_at',)
    
    def product_link(self, obj):
        url = reverse('admin:product_product_change', args=[obj.product_id])
        return format_html('<a href="{}">{}</a>', url, str(obj.product))
    product_link.short_description = 'Product'
    product_link.admin_order_field = 'product__name'
    
    def user_link(self, obj):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        url = reverse(f'admin:{User._meta.app_label}_{User._meta.model_name}_change', args=[obj.user_id])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name() or obj.user.email)
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__email'
    
    def rating_stars(self, obj):
        return format_html(
            '<span title="{}" style="color: #ffc107; font-size: 1.2em;">{}</span>',
            obj.get_rating_display(),
            '★' * obj.rating + '☆' * (5 - obj.rating)
        )
    rating_stars.short_description = 'Rating'
    rating_stars.admin_order_field = 'rating'