"""Reply Generator Agent

This agent generates responses to emails using OpenAI's API.
"""
import logging
import os
from typing import Dict, Optional, List, Any
import openai
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class ReplyGenerator:
    """Agent responsible for generating context-aware email replies."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the ReplyGenerator agent.
        
        Args:
            config: Configuration dictionary for the agent.
        """
        self.config = config or {}
        self.initialized = False
        self.client = None
        self.default_model = "gpt-4-turbo-preview"
        self.max_tokens = 1000
        self.temperature = 0.7
    
    async def initialize(self) -> None:
        """Initialize the OpenAI client and other services."""
        if self.initialized:
            return
            
        logger.info("Initializing ReplyGenerator agent with OpenAI")
        
        # Initialize OpenAI client
        api_key = self.config.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in config or environment variables")
            
        self.client = AsyncOpenAI(api_key=api_key)
        
        # Update configuration from config
        self.default_model = self.config.get('model', self.default_model)
        self.max_tokens = self.config.get('max_tokens', self.max_tokens)
        self.temperature = self.config.get('temperature', self.temperature)
        
        self.initialized = True
    
    async def generate_reply(
        self, 
        email_data: Dict, 
        context: Optional[Dict] = None,
        style: str = "professional"
    ) -> Dict[str, Any]:
        """Generate a reply to an email using OpenAI's API.
        
        Args:
            email_data: The email data to reply to.
            context: Additional context for generating the reply.
            style: The style of the reply (e.g., 'professional', 'casual').
            
        Returns:
            Dictionary containing the generated reply and metadata.
        """
        if not self.initialized:
            await self.initialize()
            
        logger.info(f"Generating {style} reply to email: {email_data.get('subject')}")
        
        try:
            # Prepare the prompt
            prompt = self._build_prompt(email_data, context, style)
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                n=1,
                stop=None,
            )
            
            # Extract the generated reply
            reply_content = response.choices[0].message.content.strip()
            
            # Process and format the reply
            reply = {
                "content": reply_content,
                "tone": style,
                "model": self.default_model,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None,
                "suggested_actions": self._extract_actions(reply_content)
            }
            
            return reply
            
        except Exception as e:
            logger.error(f"Error generating reply: {e}")
            # Fallback to a simple response
            return {
                "content": "Thank you for your email. I'll get back to you soon.",
                "tone": style,
                "error": str(e)
            }
    
    def _build_prompt(
        self, 
        email_data: Dict, 
        context: Optional[Dict],
        style: str
    ) -> str:
        """Build the prompt for the OpenAI API."""
        subject = email_data.get('subject', 'No subject')
        sender = email_data.get('from', 'Unknown sender')
        body = email_data.get('body', '')
        
        # Truncate long emails to save tokens
        if len(body) > 2000:
            body = body[:2000] + "... [truncated]"
        
        prompt = f"""You are an AI assistant helping to draft email responses. 
        
        Email Details:
        - Subject: {subject}
        - From: {sender}
        - Style: {style}
        
        Email Content:
        {body}
        
        """
        
        # Add context if available
        if context:
            prompt += f"\nAdditional Context:\n{context}\n"
        
        prompt += """
        Please draft a response to this email. The response should be:
        1. Appropriate for a {style} context
        2. Clear and concise
        3. Address all points in the original email
        4. End with an appropriate closing
        
        Response:
        """
        
        return prompt
    
    def _extract_actions(self, reply_content: str) -> List[Dict]:
        """Extract suggested actions from the reply content."""
        # Simple implementation - can be enhanced with more sophisticated parsing
        actions = []
        
        # Look for action items in the reply
        if "follow up" in reply_content.lower():
            actions.append({"type": "follow_up", "description": "Follow up on this email"})
        if "schedule" in reply_content.lower():
            actions.append({"type": "schedule", "description": "Schedule a meeting"})
            
        return actions or [{"type": "none", "description": "No specific action required"}]
    
    async def suggest_responses(
        self, 
        email_data: Dict, 
        count: int = 3,
        styles: Optional[List[str]] = None
    ) -> List[Dict]:
        """Generate multiple response suggestions with different styles.
        
        Args:
            email_data: The email data to respond to.
            count: Number of response suggestions to generate.
            styles: List of styles to use for the responses.
            
        Returns:
            List of response suggestions with different tones/styles.
        """
        if not self.initialized:
            await self.initialize()
            
        if not styles:
            styles = ["professional", "friendly", "concise"]
            
        # Limit the number of suggestions to the number of available styles
        count = min(count, len(styles))
        styles = styles[:count]
        
        logger.info(f"Generating {count} response suggestions with styles: {', '.join(styles)}")
        
        suggestions = []
        for style in styles:
            try:
                reply = await self.generate_reply(email_data, style=style)
                suggestions.append({
                    "content": reply["content"],
                    "tone": style,
                    "tokens_used": reply.get("tokens_used")
                })
            except Exception as e:
                logger.error(f"Error generating {style} response: {e}")
        
        return suggestions
    
    async def generate_follow_up(
        self,
        thread: List[Dict],
        context: Optional[Dict] = None,
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """Generate a follow-up message in an email thread.
        
        Args:
            thread: List of emails in the thread (oldest first).
            context: Additional context for the follow-up.
            tone: Desired tone for the follow-up.
            
        Returns:
            Dictionary containing the generated follow-up and metadata.
        """
        if not self.initialized:
            await self.initialize()
            
        logger.info(f"Generating {tone} follow-up for thread: {thread[0].get('subject', 'No subject')}")
        
        try:
            # Prepare the prompt
            prompt = self._build_follow_up_prompt(thread, context, tone)
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                n=1,
                stop=None,
            )
            
            # Extract the generated follow-up
            follow_up_content = response.choices[0].message.content.strip()
            
            # Process and format the follow-up
            follow_up = {
                "content": follow_up_content,
                "tone": tone,
                "model": self.default_model,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None,
                "suggested_actions": self._extract_actions(follow_up_content)
            }
            
            return follow_up
            
        except Exception as e:
            logger.error(f"Error generating follow-up: {e}")
            # Fallback to a simple response
            return {
                "content": "Just following up on my previous email. Please let me know if you have any questions.",
                "tone": tone,
                "error": str(e)
            }
    
    def _build_follow_up_prompt(
        self, 
        thread: List[Dict], 
        context: Optional[Dict],
        tone: str
    ) -> str:
        """Build the prompt for the OpenAI API."""
        subject = thread[0].get('subject', 'No subject')
        sender = thread[0].get('from', 'Unknown sender')
        body = '\n\n'.join([email.get('body', '') for email in thread])
        
        # Truncate long emails to save tokens
        if len(body) > 2000:
            body = body[:2000] + "... [truncated]"
        
        prompt = f"""You are an AI assistant helping to draft email responses. 
        
        Email Thread:
        - Subject: {subject}
        - From: {sender}
        - Tone: {tone}
        
        Email Content:
        {body}
        
        """
        
        # Add context if available
        if context:
            prompt += f"\nAdditional Context:\n{context}\n"
        
        prompt += """
        Please draft a follow-up message to this email thread. The response should be:
        1. Appropriate for a {tone} context
        2. Clear and concise
        3. Address all points in the original email thread
        4. End with an appropriate closing
        
        Response:
        """
        
        return prompt


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        generator = ReplyGenerator()
        test_email = {
            "subject": "Project Update",
            "from": "manager@example.com",
            "body": "Hi, could you please provide an update on the project?"
        }
        reply = await generator.generate_reply(test_email, tone="professional")
        print(f"Generated reply: {reply}")
    
    asyncio.run(main())
