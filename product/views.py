from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Category, Product, Order, Review, OrderItem
from .serializers import (
    UserSerializer, RegisterSerializer, CustomTokenObtainPairSerializer,
    CategorySerializer, ProductSerializer, OrderSerializer, ReviewSerializer, OrderItemSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.pagination import PageNumberPagination

User = get_user_model()

# Auth Views
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

# User Views
class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

# Custom Pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# Category Views
class CategoryViewSet(ModelViewSet):
    """
    A viewset for viewing and editing category instances.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'id']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """
        Get all products in a specific category
        """
        category = self.get_object()
        products = Product.objects.filter(category=category)
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# Product Views
class ProductViewSet(ModelViewSet):
    """
    A viewset for viewing and editing product instances.
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'price', 'created_at', 'updated_at']

    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category is not None:
            queryset = queryset.filter(category_id=category)
            
        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
            
        # Filter by seller
        seller = self.request.query_params.get('seller', None)
        if seller is not None:
            queryset = queryset.filter(seller_id=seller)
            
        return queryset

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action in ['create']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def perform_update(self, serializer):
        if self.request.user == serializer.instance.seller or self.request.user.is_staff:
            serializer.save()
        else:
            raise permissions.PermissionDenied("You do not have permission to perform this action.")

    def perform_destroy(self, instance):
        if self.request.user == instance.seller or self.request.user.is_staff:
            instance.delete()
        else:
            raise permissions.PermissionDenied("You do not have permission to perform this action.")
            
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """
        Get all reviews for a specific product
        """
        product = self.get_object()
        reviews = Review.objects.filter(product=product)
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

# Order Views
class OrderViewSet(ModelViewSet):
    """
    A viewset for viewing and editing order instances.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['buyer__email', 'status', 'shipping_address']
    ordering_fields = ['order_date', 'total_amount', 'status']

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.all()
        
        # Non-staff users can only see their own orders
        if not user.is_staff:
            queryset = queryset.filter(buyer=user)
            
        # Filter by status
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)
            
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(order_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(order_date__lte=end_date)
            
        return queryset

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['create']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        order = serializer.save(buyer=self.request.user)
        
        # Calculate total amount from order items
        total = 0
        for item in serializer.validated_data['items']:
            product = item['product']
            quantity = item['quantity']
            total += product.price * quantity
            
            # Update product stock
            product.stock -= quantity
            product.save()
            
            # Create order item
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )
            
        # Update order total amount
        order.total_amount = total
        order.save()

    def perform_update(self, serializer):
        order = self.get_object()
        if self.request.user.is_staff:
            old_status = order.status
            new_status = serializer.validated_data.get('status', old_status)
            
            # If status changed, update order status
            if old_status != new_status:
                order.status = new_status
                order.save()
                
                # Here you could add logic to send status update notifications
                # e.g., send_order_status_update_email(order)
                
            serializer.save()
        else:
            raise permissions.PermissionDenied("You do not have permission to perform this action.")

    def perform_destroy(self, instance):
        if self.request.user.is_staff:
            # Restore product stock when order is deleted
            for item in instance.items.all():
                product = item.product
                product.stock += item.quantity
                product.save()
            instance.delete()
        else:
            raise permissions.PermissionDenied("You do not have permission to perform this action.")
            
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an order
        """
        order = self.get_object()
        
        # Only the buyer or admin can cancel the order
        if request.user != order.buyer and not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to cancel this order."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Only allow cancelling of pending or processing orders
        if order.status not in ['pending', 'processing']:
            return Response(
                {"detail": f"Cannot cancel order with status '{order.status}'"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Update order status
        order.status = 'cancelled'
        order.save()
        
        # Restore product stock
        for item in order.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()
            
        return Response({"status": "Order cancelled successfully"})

# Review Views
class ReviewViewSet(ModelViewSet):
    """
    A viewset for viewing and editing review instances.
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['comment', 'user__email', 'product__name']
    ordering_fields = ['rating', 'created_at']
    
    def get_queryset(self):
        queryset = Review.objects.all()
        
        # Filter by product if product_id is provided in URL
        product_id = self.kwargs.get('product_id')
        if product_id is not None:
            queryset = queryset.filter(product_id=product_id)
            
        # Filter by user
        user_id = self.request.query_params.get('user_id', None)
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
            
        # Filter by rating
        min_rating = self.request.query_params.get('min_rating', None)
        max_rating = self.request.query_params.get('max_rating', None)
        
        if min_rating is not None:
            queryset = queryset.filter(rating__gte=min_rating)
        if max_rating is not None:
            queryset = queryset.filter(rating__lte=max_rating)
            
        return queryset

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action in ['create']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_id')
        if product_id:
            product = get_object_or_404(Product, id=product_id)
            serializer.save(user=self.request.user, product=product)
        else:
            serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if self.request.user == serializer.instance.user or self.request.user.is_staff:
            serializer.save()
        else:
            raise permissions.PermissionDenied("You do not have permission to perform this action.")

    def perform_destroy(self, instance):
        if self.request.user == instance.user or self.request.user.is_staff:
            instance.delete()
        else:
            raise permissions.PermissionDenied("You do not have permission to perform this action.")
            
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent reviews
        """
        recent_reviews = Review.objects.all().order_by('-created_at')[:5]
        serializer = self.get_serializer(recent_reviews, many=True)
        return Response(serializer.data)
