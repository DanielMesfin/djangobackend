# broker/api/v1/serializers/promotion.py
from rest_framework import serializers
from broker.models.promotion import Promotion, PromotionClaim

class PromotionSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source='business.business_name', read_only=True)
    
    class Meta:
        model = Promotion
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class PromotionClaimSerializer(serializers.ModelSerializer):
    promotion_title = serializers.CharField(source='promotion.title', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = PromotionClaim
        fields = '__all__'
        read_only_fields = ('claimed_at', 'updated_at')


