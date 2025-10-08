import os
import time
import hashlib
import json
from typing import Optional, Dict, Any
from django.core.cache import cache
from django.conf import settings
import openai


class LLMClient:
    """Client for OpenAI API calls with retry logic and caching."""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Set the API key for the openai module
        openai.api_key = self.api_key
        
        self.model = "gpt-3.5-turbo"
        self.max_retries = 3
        self.retry_delay = 1
    
    def _get_cache_key(self, prompt: str, session_id: str) -> str:
        """Generate cache key for prompt and session."""
        content = f"{prompt}:{session_id}"
        return f"llm_cache:{hashlib.md5(content.encode()).hexdigest()}"
    
    def _make_api_call(self, messages: list, temperature: float = 0.7) -> str:
        """Make API call with retry logic."""
        for attempt in range(self.max_retries):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=1000
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                time.sleep(self.retry_delay * (2 ** attempt))
        
        raise Exception("Max retries exceeded")
    
    def generate_reply(self, prompt: str, session_id: str, context: Optional[str] = None) -> str:
        """
        Generate a reply using OpenAI API with caching.
        
        Args:
            prompt: The user's message
            session_id: Session identifier for caching
            context: Optional context from retrieval
            
        Returns:
            Generated reply text
        """
        # Check cache first (10 second TTL)
        cache_key = self._get_cache_key(prompt, session_id)
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response
        
        # Build messages
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant for a company. Provide helpful, accurate responses based on the context provided. If you don't know something, say so politely."
            }
        ]
        
        if context:
            messages.append({
                "role": "system",
                "content": f"Context: {context}"
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Generate response
        try:
            response = self._make_api_call(messages)
            
            # Cache the response for 10 seconds
            cache.set(cache_key, response, 10)
            
            return response
        except Exception as e:
            return f"I apologize, but I'm experiencing technical difficulties. Please try again later. Error: {str(e)}"
    
    def classify_and_extract(self, message: str) -> Dict[str, Any]:
        """
        Use LLM to classify if message contains lead information and extract details.
        
        Args:
            message: User message to analyze
            
        Returns:
            Dictionary with is_lead, name, email, interest_score
        """
        prompt = f"""
        Analyze the following message to determine if it contains lead qualification information.
        Look for:
        1. Name (person's name)
        2. Email address
        3. Interest in products/services
        4. Contact intent
        
        Message: "{message}"
        
        Respond with ONLY a JSON object in this exact format:
        {{
            "is_lead": true/false,
            "name": "extracted name or null",
            "email": "extracted email or null", 
            "interest_score": 0.0-1.0
        }}
        
        Rules:
        - is_lead should be true if the person shows interest in products/services AND provides contact info
        - interest_score should be 0.0-1.0 based on how interested they seem
        - Only extract name/email if clearly present
        - Return null for missing fields
        """
        
        messages = [
            {
                "role": "system",
                "content": "You are a lead qualification AI. Analyze messages and extract contact information and interest level. Always respond with valid JSON only."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ]
        
        try:
            response = self._make_api_call(messages, temperature=0.1)
            
            # Parse JSON response
            result = json.loads(response)
            
            # Validate structure
            required_fields = ['is_lead', 'name', 'email', 'interest_score']
            for field in required_fields:
                if field not in result:
                    result[field] = None if field in ['name', 'email'] else False if field == 'is_lead' else 0.0
            
            # Ensure interest_score is float
            try:
                result['interest_score'] = float(result['interest_score'])
            except (ValueError, TypeError):
                result['interest_score'] = 0.0
            
            return result
            
        except Exception as e:
            # Return safe default on error
            return {
                'is_lead': False,
                'name': None,
                'email': None,
                'interest_score': 0.0
            }


# Global instance
llm_client = LLMClient()
