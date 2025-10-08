import json
from unittest.mock import patch, MagicMock
from django.test import TestCase

from chat.services.lead_qualifier import LeadQualifier


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
    
    def test_qualify_lead_missing_fields(self):
        """Test lead qualification with missing fields in response."""
        with patch('chat.services.lead_qualifier.llm_client.classify_and_extract') as mock_classify:
            mock_classify.return_value = {
                'is_lead': True,
                # Missing name, email, interest_score
            }
            
            result = self.qualifier.qualify_lead("Test message")
            
            # Should handle missing fields gracefully
            self.assertTrue(result['is_lead'])
            self.assertIsNone(result['name'])
            self.assertIsNone(result['email'])
            self.assertEqual(result['interest_score'], 0.0)
    
    def test_qualify_lead_invalid_interest_score(self):
        """Test lead qualification with invalid interest score."""
        with patch('chat.services.lead_qualifier.llm_client.classify_and_extract') as mock_classify:
            mock_classify.return_value = {
                'is_lead': True,
                'name': 'John Doe',
                'email': 'john@example.com',
                'interest_score': 'invalid'  # Not a number
            }
            
            result = self.qualifier.qualify_lead("Test message")
            
            # Should handle invalid interest score
            self.assertTrue(result['is_lead'])
            self.assertEqual(result['name'], 'John Doe')
            self.assertEqual(result['email'], 'john@example.com')
            self.assertEqual(result['interest_score'], 0.0)  # Default value


