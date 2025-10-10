from typing import Dict, Any
from .llm_client import llm_client


class LeadQualifier:
    """Service for qualifying leads from chat messages."""
    
    def __init__(self):
        self.llm_client = llm_client
    
    def qualify_lead(self, message: str) -> Dict[str, Any]:
        """
        Qualify a lead from a chat message.
        
        Args:
            message: User message to analyze
            
        Returns:
            Dictionary with qualification results
        """
        try:
            result = self.llm_client.classify_and_extract(message)
            
            # Additional validation
            if result.get('is_lead'):
                # Ensure we have at least name or email
                if not result.get('name') and not result.get('email'):
                    result['is_lead'] = False
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
    
    def should_save_lead(self, qualification_result: Dict[str, Any]) -> bool:
        """
        Determine if a lead should be saved based on qualification results.
        
        Args:
            qualification_result: Result from qualify_lead
            
        Returns:
            True if lead should be saved
        """
        return (
            qualification_result.get('is_lead', False) and
            qualification_result.get('interest_score', 0.0) > 0.3 and
            (qualification_result.get('name') or qualification_result.get('email'))
        )


# Global instance
lead_qualifier = LeadQualifier()



