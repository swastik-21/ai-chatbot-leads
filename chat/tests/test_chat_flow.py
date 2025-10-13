import json
import uuid
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from chat.models import Session, Message, Lead
from chat.services.llm_client import LLMClient
from chat.services.lead_qualifier import LeadQualifier


class ChatFlowTestCase(APITestCase):
    """Test cases for chat flow functionality."""
    
    def setUp(self):
        self.client = Client()
        self.chat_url = '/api/chat/'
    
    @patch('chat.services.llm_client.llm_client.generate_reply')
    @patch('chat.services.retriever.retriever.get_context')
    @patch('chat.services.lead_qualifier.lead_qualifier.qualify_lead')
    def test_chat_endpoint_basic_flow(self, mock_qualify, mock_context, mock_reply):
        """Test basic chat flow with mocked LLM responses."""
        # Mock the services
        mock_context.return_value = "Mock context from FAQ"
        mock_reply.return_value = "Hello! How can I help you today?"
        mock_qualify.return_value = {
            'is_lead': False,
            'name': None,
            'email': None,
            'interest_score': 0.0
        }
        
        # Test data
        test_message = "Hello, I need help with your products"
        
        # Make request
        response = self.client.post(
            self.chat_url,
            data={'message': test_message},
            content_type='application/json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('reply', data)
        self.assertIn('session_id', data)
        self.assertIn('lead_qualified', data)
        
        self.assertEqual(data['reply'], "Hello! How can I help you today?")
        self.assertFalse(data['lead_qualified'])
        
        # Verify services were called
        mock_context.assert_called_once_with(test_message, top_k=3)
        mock_reply.assert_called_once()
        mock_qualify.assert_called_once_with(test_message)
        
        # Verify database records
        self.assertEqual(Session.objects.count(), 1)
        self.assertEqual(Message.objects.count(), 2)  # User + AI message
        self.assertEqual(Lead.objects.count(), 0)
    
    @patch('chat.services.llm_client.llm_client.generate_reply')
    @patch('chat.services.retriever.retriever.get_context')
    @patch('chat.services.lead_qualifier.lead_qualifier.qualify_lead')
    def test_chat_with_lead_qualification(self, mock_qualify, mock_context, mock_reply):
        """Test chat flow that qualifies a lead."""
        # Mock the services
        mock_context.return_value = "Mock context"
        mock_reply.return_value = "Thank you for your interest!"
        mock_qualify.return_value = {
            'is_lead': True,
            'name': 'John Doe',
            'email': 'john@example.com',
            'interest_score': 0.8
        }
        
        # Test data
        test_message = "Hi, I'm John Doe (john@example.com) and I'm very interested in your premium package!"
        
        # Make request
        response = self.client.post(
            self.chat_url,
            data={'message': test_message},
            content_type='application/json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertTrue(data['lead_qualified'])
        self.assertIn('lead_data', data)
        self.assertEqual(data['lead_data']['name'], 'John Doe')
        self.assertEqual(data['lead_data']['email'], 'john@example.com')
        
        # Verify lead was saved
        self.assertEqual(Lead.objects.count(), 1)
        lead = Lead.objects.first()
        self.assertEqual(lead.name, 'John Doe')
        self.assertEqual(lead.email, 'john@example.com')
        self.assertEqual(lead.interest_score, 0.8)
    
    def test_chat_with_existing_session(self):
        """Test chat with existing session ID."""
        # Create a session
        session = Session.objects.create()
        
        with patch('chat.services.llm_client.llm_client.generate_reply') as mock_reply, \
             patch('chat.services.retriever.retriever.get_context') as mock_context, \
             patch('chat.services.lead_qualifier.lead_qualifier.qualify_lead') as mock_qualify:
            
            mock_context.return_value = ""
            mock_reply.return_value = "Response"
            mock_qualify.return_value = {'is_lead': False, 'name': None, 'email': None, 'interest_score': 0.0}
            
            response = self.client.post(
                self.chat_url,
                data={'session_id': str(session.id), 'message': 'Test message'},
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data['session_id'], str(session.id))
    
    def test_chat_invalid_data(self):
        """Test chat endpoint with invalid data."""
        response = self.client.post(
            self.chat_url,
            data={'invalid': 'data'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LeadQualifierTestCase(TestCase):
    """Test cases for lead qualification functionality."""
    
    def setUp(self):
        self.qualifier = LeadQualifier()
    
    @patch('chat.services.lead_qualifier.llm_client.classify_and_extract')
    def test_qualify_lead_success(self, mock_classify):
        """Test successful lead qualification."""
        mock_classify.return_value = {
            'is_lead': True,
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'interest_score': 0.9
        }
        
        result = self.qualifier.qualify_lead("Hi, I'm Jane Smith and I want to buy your product!")
        
        self.assertTrue(result['is_lead'])
        self.assertEqual(result['name'], 'Jane Smith')
        self.assertEqual(result['email'], 'jane@example.com')
        self.assertEqual(result['interest_score'], 0.9)
    
    @patch('chat.services.lead_qualifier.llm_client.classify_and_extract')
    def test_qualify_lead_no_lead(self, mock_classify):
        """Test message that doesn't qualify as lead."""
        mock_classify.return_value = {
            'is_lead': False,
            'name': None,
            'email': None,
            'interest_score': 0.1
        }
        
        result = self.qualifier.qualify_lead("Just asking a general question")
        
        self.assertFalse(result['is_lead'])
        self.assertIsNone(result['name'])
        self.assertIsNone(result['email'])
        self.assertEqual(result['interest_score'], 0.1)
    
    @patch('chat.services.lead_qualifier.llm_client.classify_and_extract')
    def test_qualify_lead_error_handling(self, mock_classify):
        """Test error handling in lead qualification."""
        mock_classify.side_effect = Exception("API Error")
        
        result = self.qualifier.qualify_lead("Any message")
        
        # Should return safe defaults
        self.assertFalse(result['is_lead'])
        self.assertIsNone(result['name'])
        self.assertIsNone(result['email'])
        self.assertEqual(result['interest_score'], 0.0)
    
    def test_should_save_lead_true(self):
        """Test should_save_lead returns True for valid lead."""
        qualification_result = {
            'is_lead': True,
            'name': 'John Doe',
            'email': 'john@example.com',
            'interest_score': 0.8
        }
        
        result = self.qualifier.should_save_lead(qualification_result)
        self.assertTrue(result)
    
    def test_should_save_lead_false_low_score(self):
        """Test should_save_lead returns False for low interest score."""
        qualification_result = {
            'is_lead': True,
            'name': 'John Doe',
            'email': 'john@example.com',
            'interest_score': 0.2  # Below threshold
        }
        
        result = self.qualifier.should_save_lead(qualification_result)
        self.assertFalse(result)
    
    def test_should_save_lead_false_no_contact(self):
        """Test should_save_lead returns False when no contact info."""
        qualification_result = {
            'is_lead': True,
            'name': None,
            'email': None,
            'interest_score': 0.8
        }
        
        result = self.qualifier.should_save_lead(qualification_result)
        self.assertFalse(result)


class SessionHistoryTestCase(APITestCase):
    """Test cases for session history endpoint."""
    
    def test_session_history_success(self):
        """Test successful session history retrieval."""
        # Create session and messages
        session = Session.objects.create()
        Message.objects.create(session=session, text="Hello", sender="user")
        Message.objects.create(session=session, text="Hi there!", sender="assistant")
        
        url = f'/api/session/{session.id}/history/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['id'], str(session.id))
        self.assertEqual(len(data['messages']), 2)
        self.assertEqual(data['messages'][0]['text'], "Hello")
        self.assertEqual(data['messages'][1]['text'], "Hi there!")
    
    def test_session_history_not_found(self):
        """Test session history for non-existent session."""
        fake_uuid = uuid.uuid4()
        url = f'/api/session/{fake_uuid}/history/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LeadsListTestCase(APITestCase):
    """Test cases for leads list endpoint."""
    
    def test_leads_list_empty(self):
        """Test leads list when no leads exist."""
        response = self.client.get('/api/leads/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 0)
    
    def test_leads_list_with_data(self):
        """Test leads list with existing leads."""
        # Create session and lead
        session = Session.objects.create()
        Lead.objects.create(
            name="John Doe",
            email="john@example.com",
            interest_score=0.8,
            source_session=session
        )
        
        response = self.client.get('/api/leads/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "John Doe")
        self.assertEqual(data[0]['email'], "john@example.com")




