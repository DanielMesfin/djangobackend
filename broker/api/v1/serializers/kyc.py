# broker/api/v1/serializers/kyc.py
from rest_framework import serializers
from broker.models.kyc import KYCVerification

class KYCVerificationSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    verified_by_email = serializers.EmailField(source='verified_by.email', read_only=True)
    
    class Meta:
        model = KYCVerification
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'user', 'status', 'verified_by', 'verified_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class KYCVerificationAdminSerializer(KYCVerificationSerializer):
    class Meta(KYCVerificationSerializer.Meta):
        read_only_fields = ('created_at', 'updated_at', 'verified_at')