from rest_framework import serializers
from .models import Session, Message, Lead


class SessionSerializer(serializers.ModelSerializer):
    """Serializer for Session model."""
    
    class Meta:
        model = Session
        fields = ['id', 'created_at', 'updated_at']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""
    
    class Meta:
        model = Message
        fields = ['id', 'text', 'sender', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class LeadSerializer(serializers.ModelSerializer):
    """Serializer for Lead model."""
    
    class Meta:
        model = Lead
        fields = ['id', 'name', 'email', 'interest_score', 'source_session', 'created_at', 'notes']
        read_only_fields = ['id', 'created_at']


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for chat request."""
    session_id = serializers.UUIDField(required=False)
    message = serializers.CharField(max_length=2000)


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat response."""
    reply = serializers.CharField()
    session_id = serializers.UUIDField()
    lead_qualified = serializers.BooleanField(default=False)
    lead_data = serializers.DictField(required=False)


class SessionHistorySerializer(serializers.ModelSerializer):
    """Serializer for session with messages."""
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Session
        fields = ['id', 'created_at', 'updated_at', 'messages']



