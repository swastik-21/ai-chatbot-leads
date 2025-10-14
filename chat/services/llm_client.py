import os
import time
import hashlib
import json
from typing import Optional, Dict, Any
from django.core.cache import cache
from django.conf import settings
from openai import OpenAI


class LLMClient:
    """Client for OpenAI API calls with retry logic and caching."""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-3.5-turbo"
        self.max_retries = 3
        self.retry_delay = 1
        self._initialized = False
        
        # Initialize OpenAI client
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the OpenAI client with error handling."""
        try:
            if not self.api_key:
                print("Warning: OPENAI_API_KEY environment variable is not set")
                self._initialized = False
                return
            
            # Initialize the OpenAI client with the new API
            self.client = OpenAI(api_key=self.api_key)
            self._initialized = True
            print("OpenAI client initialized successfully")
            
        except Exception as e:
            print(f"Warning: OpenAI client initialization failed: {e}")
            self._initialized = False
    
    def _get_cache_key(self, prompt: str, session_id: str) -> str:
        """Generate cache key for prompt and session."""
        content = f"{prompt}:{session_id}"
        return f"llm_cache:{hashlib.md5(content.encode()).hexdigest()}"
    
    def _get_quick_response(self, prompt: str) -> Optional[str]:
        """Get quick response for common questions without API call."""
        quick_responses = {
            'hi': "Hello! I'm Swastik's AI assistant. I help businesses with AI solutions like chatbots, automation, and custom AI models. What's your business looking to achieve with AI?",
            'hello': "Hello! I'm Swastik's AI assistant. I help businesses with AI solutions like chatbots, automation, and custom AI models. What's your business looking to achieve with AI?",
            'what services': "Swastik offers: Chatbots ($150-300), Automation ($200-400), AI models ($300-600), Full-stack projects ($500-1200). What type of project are you considering?",
            'pricing': "Pricing: Chatbots $150-300, Automation $200-400, AI models $300-600, Full-stack $500-1200. What's your budget range for this project?",
            'how much': "Chatbots: $150-300, Automation: $200-400, AI models: $300-600, Full-stack: $500-1200. What's your timeline and budget for this project?",
            'contact': "Contact Swastik: https://www.upwork.com/freelancers/~01a3695131c30e858f - Free consultations! What's your project timeline?",
            'hire': "Hire Swastik: https://www.upwork.com/freelancers/~01a3695131c30e858f - Budget-friendly AI solutions! What's your project about?",
            'upwork': "Swastik's Upwork: https://www.upwork.com/freelancers/~01a3695131c30e858f",
            'chatbot': "Swastik builds custom chatbots for $150-300. What's your main use case - customer service, lead generation, or sales support?",
            'automation': "Swastik creates automation workflows using Botpress, Make.com, Zapier, n8n. Starting at $200-400! What processes do you want to automate?",
            'ai model': "Swastik develops custom AI models for $300-600. Text classification, sentiment analysis, predictive modeling! What data do you have?",
            'project': "Swastik delivers full-stack AI projects for $500-1200. Complete solutions with frontend, backend, and AI integration! What's your project scope?",
            'startup': "Perfect for startups! Swastik offers budget-friendly AI solutions with 20% discount and payment plans. What's your startup's main challenge?",
            'budget': "Budget-friendly pricing: Chatbots $150-300, Automation $200-400, AI models $300-600. 20% startup discount! What's your budget range?",
            'business': "Great! What industry is your business in? And what's your main challenge that AI could help solve?",
            'company': "Excellent! What's your company size and what's your biggest operational challenge right now?",
            'need': "Perfect! What specific AI solution do you need? And what's your timeline for this project?",
            'want': "Great! What's your budget range for this project? And when do you need it completed?",
            'looking': "Excellent! What's your business type and what's your main goal with AI?",
            'interested': "Perfect! What's your project about and what's your budget range?",
            'considering': "Great! What's your timeline for this project and what's your main challenge?",
            'thinking': "Excellent! What's your business and what specific AI solution are you thinking about?",
            'planning': "Perfect! What's your project scope and what's your budget range?",
            'timeline': "Great! What's your project about and what's your budget range?",
            'budget': "Perfect! What's your project scope and what's your timeline?",
            'cost': "Excellent! What's your project about and what's your timeline?",
            'price': "Great! What's your project scope and what's your timeline?",
            'when': "Perfect! What's your project about and what's your budget range?",
            'how long': "Excellent! What's your project scope and what's your budget range?",
            'help': "I can help with: Service information, pricing details, project consultation. What specific challenge is your business facing?"
        }
        
        for keyword, response in quick_responses.items():
            if keyword in prompt:
                return response
        
        return None
    
    def _make_api_call(self, messages: list, temperature: float = 0.7, max_tokens: int = 300) -> str:
        """Make API call with optimized settings for faster responses."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=5,  # 5 second timeout for faster responses
                stream=False
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Return quick fallback instead of retrying
            return "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
    
    def generate_reply(self, prompt: str, session_id: str, context: Optional[str] = None) -> str:
        """
        Generate a reply using OpenAI API with caching and quick responses.
        
        Args:
            prompt: The user's message
            session_id: Session identifier for caching
            context: Optional context from retrieval
            
        Returns:
            Generated reply text
        """
        # Check if client is initialized
        if not self._initialized:
            return "I apologize, but I'm currently unavailable. Please try again later."
        
        # Quick responses for common questions
        quick_responses = self._get_quick_response(prompt.lower())
        if quick_responses:
            return quick_responses
        
        # Check cache first (10 second TTL)
        cache_key = self._get_cache_key(prompt, session_id)
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response
        
        # Build messages with shorter system prompt
        messages = [
            {
                "role": "system",
                "content": "You are Swastik's AI assistant. Swastik is an AI developer offering chatbots ($150-300), automation ($200-400), AI models ($300-600), and full-stack projects ($500-1200). Help clients understand services and pricing. Be brief, professional, and ask qualifying questions like: What's your business? What's your budget? What's your timeline? What's your main challenge? Always encourage them to provide contact info for consultation."
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
        # Check if client is initialized
        if not self._initialized:
            return {
                'is_lead': False,
                'name': None,
                'email': None,
                'interest_score': 0.0
            }
        
        prompt = f"""
        Analyze the following message to determine if it contains lead qualification information for Swastik's AI development services.
        
        Swastik is an AI developer who provides:
        - Custom AI model development ($300-600)
        - Machine learning solutions
        - Chatbot development ($150-300)
        - Automation workflows (Botpress, Make.com, Zapier, n8n) ($200-400)
        - Full-stack AI projects ($500-1200)
        - Data analysis and insights
        - Business process automation
        - Budget-friendly pricing for startups and small businesses
        - Payment plans and startup discounts available
        
        Look for:
        1. Name (person's name)
        2. Email address
        3. Interest in AI/ML services, chatbots, automation, or development
        4. Business needs or project requirements
        5. Contact intent or request for consultation
        
        Message: "{message}"
        
        Respond with ONLY a JSON object in this exact format:
        {{
            "is_lead": true/false,
            "name": "extracted name or null",
            "email": "extracted email or null", 
            "interest_score": 0.0-1.0
        }}
        
        Rules:
        - is_lead should be true if the person shows interest in AI/ML services AND provides contact info (name or email)
        - interest_score should be 0.0-1.0 based on how interested they seem in AI development services
        - High interest (0.7-1.0): Mentions specific AI/ML needs, chatbot requirements, automation needs, or asks for consultation
        - Medium interest (0.4-0.6): Shows general interest in AI or mentions business needs
        - Low interest (0.1-0.3): Casual inquiry or general questions
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
            response = self._make_api_call(messages, temperature=0.1, max_tokens=200)
            
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
