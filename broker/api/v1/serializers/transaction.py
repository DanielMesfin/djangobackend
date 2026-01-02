# broker/api/v1/serializers/transaction.py
from rest_framework import serializers
from broker.models.transaction import Transaction, Wallet

class WalletSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'balance')

class TransactionSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    recipient_email = serializers.EmailField(source='recipient.email', read_only=True)
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'status', 'transaction_id')

    def create(self, validated_data):
        # Generate a unique transaction ID
        import uuid
        validated_data['transaction_id'] = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        return super().create(validated_data)