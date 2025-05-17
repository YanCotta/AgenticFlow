"""Newsletter Processor Agent

This agent processes newsletter emails to extract and format content for social media posts,
using AI-powered analysis and content extraction.
"""
import logging
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import os
from enum import Enum
import openai
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class ContentType(str, Enum):
    """Types of content that can be extracted from newsletters."""
    ARTICLE = "article"
    EVENT = "event"
    PROMOTION = "promotion"
    UPDATE = "update"
    OTHER = "other"

class NewsletterProcessor:
    """Agent responsible for processing and extracting value from newsletter content."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the NewsletterProcessor agent.
        
        Args:
            config: Configuration dictionary for the agent.
        """
        self.config = config or {}
        self.initialized = False
        self.client = None
        self.default_model = "gpt-4-turbo-preview"
        self.max_tokens = 4000
        self.temperature = 0.3
    
    async def initialize(self) -> None:
        """Initialize the agent and required services."""
        if self.initialized:
            return
            
        logger.info("Initializing NewsletterProcessor agent with OpenAI")
        
        # Initialize OpenAI client
        api_key = self.config.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in config or environment variables")
            
        self.client = AsyncOpenAI(api_key=api_key)
        
        # Update configuration
        self.default_model = self.config.get('model', self.default_model)
        self.max_tokens = self.config.get('max_tokens', self.max_tokens)
        self.temperature = self.config.get('temperature', self.temperature)
        
        self.initialized = True
    
    async def process_newsletter(
        self,
        email_data: Dict,
        format_rules: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Process a newsletter email to extract structured content using AI.
        
        Args:
            email_data: The newsletter email data with 'subject', 'from', 'date', and 'body'.
            format_rules: Optional formatting rules for the content.
            
        Returns:
            Dictionary containing the processed newsletter content with articles and metadata.
        """
        if not self.initialized:
            await self.initialize()
            
        logger.info(f"Processing newsletter: {email_data.get('subject', 'No subject')}")
        
        try:
            # Clean and preprocess the email body
            body = self._clean_newsletter_content(email_data.get('body', ''))
            
            # Extract structured content using AI
            structured_content = await self._extract_structured_content(
                subject=email_data.get('subject', ''),
                body=body,
                sender=email_data.get('from', '')
            )
            
            # Process articles if any
            articles = []
            if structured_content.get('articles'):
                articles = await self._process_articles(
                    structured_content['articles'], 
                    format_rules
                )
            
            # Prepare the final response
            processed = {
                "title": structured_content.get('title', email_data.get('subject', '')),
                "summary": structured_content.get('summary', ''),
                "articles": articles,
                "content_type": structured_content.get('content_type', ContentType.OTHER),
                "metadata": {
                    "source": email_data.get('from', ''),
                    "date": email_data.get('date', ''),
                    "processing_date": datetime.utcnow().isoformat(),
                    "model_used": self.default_model
                },
                "format_rules_applied": format_rules or {}
            }
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing newsletter: {e}")
            return self._create_error_response(email_data, str(e))
    
    async def extract_articles(
        self,
        email_data: Dict,
        body: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Extract individual articles from a newsletter using AI.
        
        Args:
            email_data: The newsletter email data.
            body: Optional pre-extracted email body.
            
        Returns:
            List of extracted articles with metadata.
        """
        if not self.initialized:
            await self.initialize()
            
        logger.info("Extracting articles from newsletter")
        
        try:
            if body is None:
                body = self._clean_newsletter_content(email_data.get('body', ''))
            
            # Use AI to identify and extract articles
            prompt = self._build_article_extraction_prompt(
                subject=email_data.get('subject', ''),
                body=body,
                sender=email_data.get('from', '')
            )
            
            response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": "You are an AI that extracts articles from newsletters."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            content = response.choices[0].message.content
            try:
                result = json.loads(content)
                return result.get('articles', [])
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse article extraction JSON: {e}")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting articles: {e}")
            return []
    
    async def _extract_structured_content(
        self,
        subject: str,
        body: str,
        sender: str
    ) -> Dict[str, Any]:
        """Extract structured content from the newsletter using AI."""
        try:
            prompt = self._build_extraction_prompt(subject, body, sender)
            
            response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": "You are an AI that extracts structured information from newsletters."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            # Parse and validate the response
            content = response.choices[0].message.content
            try:
                result = json.loads(content)
                return self._validate_structured_content(result)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse structured content JSON: {e}")
                raise ValueError("Failed to parse newsletter content")
                
        except Exception as e:
            logger.error(f"Error in AI content extraction: {e}")
            raise
    
    def _clean_newsletter_content(self, content: str) -> str:
        """Clean and preprocess the newsletter content."""
        if not content:
            return ""
            
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', ' ', content)
        
        # Remove common email signatures and disclaimers
        patterns = [
            r'(?i)unsubscribe.*?$',
            r'(?i)subscribe.*?$',
            r'(?i)privacy policy',
            r'(?i)terms of service',
            r'(?i)all rights reserved',
            r'\[.*?\]',  # Remove anything in square brackets
            r'http\S+',  # Remove URLs
        ]
        
        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE)
            
        # Remove extra whitespace and limit length
        content = ' '.join(content.split())
        return content[:15000]  # Limit content length to save tokens
    
    def _build_extraction_prompt(
        self, 
        subject: str, 
        body: str, 
        sender: str
    ) -> str:
        """Build the prompt for content extraction."""
        return f"""
        Analyze the following newsletter and extract structured information.
        
        SUBJECT: {subject}
        FROM: {sender}
        
        CONTENT:
        {body}
        
        Extract the following information as a JSON object:
        1. title: A clear title for the newsletter
        2. summary: A brief 2-3 sentence summary
        3. content_type: One of {[t.value for t in ContentType]}
        4. articles: Array of articles, each with:
           - title
           - summary
           - key_points: 3-5 bullet points
           - category: Topic/category
           - sentiment: positive/negative/neutral
        
        Format the response as a valid JSON object.
        """
    
    def _build_article_extraction_prompt(
        self,
        subject: str,
        body: str,
        sender: str
    ) -> str:
        """Build the prompt for article extraction."""
        return f"""
        Extract all articles from the following newsletter.
        
        SUBJECT: {subject}
        FROM: {sender}
        
        CONTENT:
        {body}
        
        For each article, extract:
        1. Title
        2. Summary (2-3 sentences)
        3. 3-5 key points
        4. Category/topic
        5. Sentiment (positive/negative/neutral)
        6. Any relevant URLs or links
        
        Return the results as a JSON object with an 'articles' array.
        """
    
    async def _process_articles(
        self, 
        articles: List[Dict], 
        format_rules: Optional[Dict] = None
    ) -> List[Dict]:
        """Process and format extracted articles."""
        if not articles:
            return []
            
        processed = []
        for article in articles:
            try:
                # Apply formatting rules if provided
                if format_rules:
                    article = self._apply_formatting(article, format_rules)
                
                # Add additional processing as needed
                if 'sentiment' not in article:
                    article['sentiment'] = 'neutral'
                    
                processed.append(article)
                
            except Exception as e:
                logger.warning(f"Error processing article: {e}")
                continue
                
        return processed
    
    def _apply_formatting(self, article: Dict, rules: Dict) -> Dict:
        """Apply formatting rules to an article."""
        formatted = article.copy()
        
        if 'title' in formatted and rules.get('title_case', True):
            formatted['title'] = formatted['title'].title()
            
        if 'summary' in formatted and 'max_summary_length' in rules:
            max_len = rules['max_summary_length']
            if len(formatted['summary']) > max_len:
                formatted['summary'] = formatted['summary'][:max_len-3] + '...'
                
        return formatted
    
    def _validate_structured_content(self, content: Dict) -> Dict:
        """Validate and clean the extracted content."""
        required_fields = ['title', 'summary', 'content_type', 'articles']
        for field in required_fields:
            if field not in content:
                content[field] = '' if field != 'articles' else []
        
        # Ensure content_type is valid
        if content['content_type'] not in [t.value for t in ContentType]:
            content['content_type'] = ContentType.OTHER.value
            
        # Ensure articles is a list
        if not isinstance(content.get('articles', []), list):
            content['articles'] = []
            
        return content
    
    def _create_error_response(
        self, 
        email_data: Dict, 
        error_msg: str
    ) -> Dict[str, Any]:
        """Create an error response with minimal information."""
        return {
            "title": email_data.get('subject', 'Error Processing Newsletter'),
            "error": error_msg,
            "articles": [],
            "metadata": {
                "source": email_data.get('from', ''),
                "date": email_data.get('date', str(datetime.utcnow())),
                "error": True,
                "error_message": error_msg
            }
        }


# Example usage
if __name__ == "__main__":
    import asyncio
    import os
    from dotenv import load_dotenv
    
    async def main():
        # Load environment variables
        load_dotenv()
        
        # Initialize the processor with OpenAI API key
        config = {
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "model": "gpt-4-turbo-preview",
            "max_tokens": 4000,
            "temperature": 0.3
        }
        
        processor = NewsletterProcessor(config=config)
        
        # Sample newsletter data
        test_newsletter = {
            "subject": "Weekly Tech Digest: AI Breakthroughs & More",
            "from": "newsletter@tech.example.com",
            "date": "2023-06-15T10:00:00Z",
            "body": """
            <h1>This Week in Tech</h1>
            
            <article>
                <h2>New AI Model Surpasses Human Performance</h2>
                <p>Researchers have developed a new AI model that outperforms humans in complex reasoning tasks. 
                The model, called ReasonNet, achieved 92% accuracy on standardized tests.</p>
                <p>Key points:</p>
                <ul>
                    <li>ReasonNet achieves 92% accuracy on complex reasoning tests</li>
                    <li>Uses novel attention mechanism for better context understanding</li>
                    <li>Potential applications in education and research</li>
                </ul>
                <p>Read more: https://example.com/ai-breakthrough</p>
            </article>
            
            <article>
                <h2>Tech Giant Announces Revolutionary Chip</h2>
                <p>TechCorp has unveiled its latest quantum computing chip, claiming it's 100x faster than 
                current market leaders. The chip uses photonic technology for improved efficiency.</p>
                <p>Key points:</p>
                <ul>
                    <li>New photonic quantum chip announced</li>
                    <li>100x performance improvement claimed</li>
                    <li>Expected to ship Q1 2024</li>
                </ul>
            </article>
            
            <footer>
                <p>© 2023 Tech Digest. All rights reserved.</p>
                <p><a href="#unsubscribe">Unsubscribe</a> | <a href="#privacy">Privacy Policy</a></p>
            </footer>
            """
        }
        
        # Process the newsletter
        try:
            print("Processing newsletter...")
            processed = await processor.process_newsletter(
                test_newsletter,
                format_rules={
                    "title_case": True,
                    "max_summary_length": 200
                }
            )
            
            # Display results
            print("\n=== Processed Newsletter ===")
            print(f"Title: {processed.get('title')}")
            print(f"Summary: {processed.get('summary')}")
            print(f"Content Type: {processed.get('content_type')}")
            
            print("\n=== Extracted Articles ===")
            for i, article in enumerate(processed.get('articles', []), 1):
                print(f"\nArticle {i}: {article.get('title')}")
                print(f"Sentiment: {article.get('sentiment', 'neutral')}")
                print(f"Summary: {article.get('summary')}")
                print("Key Points:")
                for point in article.get('key_points', []):
                    print(f"- {point}")
            
            # Extract articles separately
            print("\n=== Article Extraction Test ===")
            articles = await processor.extract_articles(test_newsletter)
            print(f"Extracted {len(articles)} articles")
            
        except Exception as e:
            print(f"Error: {e}")
    
    asyncio.run(main())
