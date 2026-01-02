# broker/api/v1/views/user.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from broker.models.user import User, UserProfile, SocialLink
from ..serializers.user import SocialLinkSerializer, UserProfileSerializer, UserSerializer
from .base import BaseViewSet

class UserProfileViewSet(BaseViewSet):
    """
    ViewSet for managing user profiles.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    
    def get_object(self):
        return self.request.user.profile
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """
        Get or update the current user's profile.
        """
        profile = self.get_object()
        
        if request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(profile, data=request.data, partial=request.method == 'PATCH')
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
            
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def upload_photo(self, request):
        """
        Upload a profile photo for the current user.
        """
        profile = self.get_object()
        if 'photo' not in request.FILES:
            return Response(
                {'error': 'No photo file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        profile.photo = request.FILES['photo']
        profile.save()
        return Response({'photo_url': profile.photo.url} if profile.photo else {})

class UserSocialLinkViewSet(BaseViewSet):
    """
    ViewSet for managing user social links.
    """
    serializer_class = SocialLinkSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SocialLink.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context