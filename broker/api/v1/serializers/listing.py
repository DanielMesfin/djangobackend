# broker/api/v1/serializers/listing.py
from rest_framework import serializers
from broker.models.listing import Listing, DraftOrder

class DraftOrderSerializer(serializers.ModelSerializer):
    buyer_email = serializers.EmailField(source='buyer.email', read_only=True)
    buyer_name = serializers.CharField(source='buyer.get_full_name', read_only=True)
    
    class Meta:
        model = DraftOrder
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'status')

class ListingSerializer(serializers.ModelSerializer):
    draft_orders = DraftOrderSerializer(many=True, read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'status')
        
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)