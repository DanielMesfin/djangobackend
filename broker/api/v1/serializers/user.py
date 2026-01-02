# broker/api/v1/serializers/user.py
from rest_framework import serializers
from broker.models.user import User, UserProfile, SocialLink

class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class UserProfileSerializer(serializers.ModelSerializer):
    social_links = SocialLinkSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'is_active', 
                 'is_staff', 'date_joined', 'last_login', 'profile')
        read_only_fields = ('id', 'date_joined', 'last_login')