# broker/api/v1/serializers/campaign.py
from rest_framework import serializers
from broker.models.campaign import Campaign, CampaignCollaborator, CampaignProduct

class CampaignProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignProduct
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class CampaignCollaboratorSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = CampaignCollaborator
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class CampaignSerializer(serializers.ModelSerializer):
    products = CampaignProductSerializer(many=True, read_only=True)
    collaborators = CampaignCollaboratorSerializer(many=True, read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    
    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'status')
        
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)