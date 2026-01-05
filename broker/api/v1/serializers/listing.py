# broker/api/v1/serializers/listing.py
from rest_framework import serializers
from broker.models.listing import Listing

# DraftOrder model was removed - use product.Order instead

class ListingSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    business_name = serializers.CharField(source='business.business_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
        
    def create(self, validated_data):
        # User is set in the view's perform_create
        return super().create(validated_data)
