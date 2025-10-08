import uuid
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .models import Session, Message, Lead
from .serializers import (
    ChatRequestSerializer, ChatResponseSerializer, 
    SessionHistorySerializer, LeadSerializer
)
from .services.llm_client import llm_client
from .services.retriever import retriever
from .services.lead_qualifier import lead_qualifier


@api_view(['POST'])
def chat(request):
    """
    Handle chat messages and return AI responses.
    
    POST /api/chat/
    Body: {"session_id": "uuid", "message": "user message"}
    Returns: {"reply": "AI response", "session_id": "uuid", "lead_qualified": bool}
    """
    serializer = ChatRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    session_id = serializer.validated_data.get('session_id')
    message_text = serializer.validated_data['message']
    
    # Get or create session
    if session_id:
        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            session = Session.objects.create()
    else:
        session = Session.objects.create()
    
    # Save user message
    user_message = Message.objects.create(
        session=session,
        text=message_text,
        sender='user'
    )
    
    # Get context from retriever
    context = retriever.get_context(message_text, top_k=3)
    
    # Generate AI response
    try:
        reply = llm_client.generate_reply(message_text, str(session.id), context)
    except Exception as e:
        reply = f"I apologize, but I'm experiencing technical difficulties. Please try again later."
    
    # Save AI response
    ai_message = Message.objects.create(
        session=session,
        text=reply,
        sender='assistant'
    )
    
    # Qualify lead
    lead_data = lead_qualifier.qualify_lead(message_text)
    lead_qualified = False
    
    if lead_qualifier.should_save_lead(lead_data):
        # Save lead
        lead = Lead.objects.create(
            name=lead_data.get('name'),
            email=lead_data.get('email'),
            interest_score=lead_data.get('interest_score', 0.0),
            source_session=session,
            notes=f"Qualified from message: {message_text[:200]}"
        )
        lead_qualified = True
    
    # Prepare response
    response_data = {
        'reply': reply,
        'session_id': session.id,
        'lead_qualified': lead_qualified,
        'lead_data': lead_data if lead_qualified else None
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def session_history(request, session_id):
    """
    Get chat history for a session.
    
    GET /api/session/{session_id}/history/
    Returns: Session with messages
    """
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return Response(
            {'error': 'Session not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = SessionHistorySerializer(session)
    return Response(serializer.data)


@api_view(['GET'])
def leads_list(request):
    """
    List all qualified leads.
    
    GET /api/leads/
    Returns: List of leads
    """
    leads = Lead.objects.all()
    serializer = LeadSerializer(leads, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def frontend_view(request):
    """
    Serve the frontend HTML page.
    
    GET /
    Returns: Frontend HTML
    """
    from django.shortcuts import render
    return render(request, 'index.html')
