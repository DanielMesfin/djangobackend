# broker/api/v1/serializers/business.py
from rest_framework import serializers
from broker.models.business import BusinessProfile, BusinessMember
from broker.models.kyc import BusinessDocument

class BusinessDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessDocument
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'uploaded_by')

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)

class BusinessMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = BusinessMember
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class BusinessProfileSerializer(serializers.ModelSerializer):
    documents = BusinessDocumentSerializer(many=True, read_only=True)
    members = BusinessMemberSerializer(many=True, read_only=True)
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    
    class Meta:
        model = BusinessProfile
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'owner')
        
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)