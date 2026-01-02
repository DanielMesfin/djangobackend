from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

# Create a router for viewsets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'review',views.ReviewViewSet, basename="review")

# Nested router for reviews under products
products_router = routers.NestedSimpleRouter(router, r'products', lookup='product')
products_router.register(r'reviews', views.ReviewViewSet, basename='product-reviews')

urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
    path('', include(products_router.urls)),
    
    # Additional custom endpoints
    path('reviews/recent/', views.ReviewViewSet.as_view({'get': 'recent'}), name='recent-reviews'),
]
