"""
Orchestrator for the AgenticFlow system.

This module coordinates the different agents to process emails and generate responses.
"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

# Import agents
from .email_fetcher import EmailFetcher
from .email_analyzer import EmailAnalyzer
from .reply_generator import ReplyGenerator
from .newsletter_processor import NewsletterProcessor
from .post_formatter import PostFormatter
from .social_poster import SocialPoster, Platform

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailOrchestrator:
    """Orchestrates the email processing pipeline."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the orchestrator with all required agents.
        
        Args:
            config: Configuration dictionary for the orchestrator and agents.
        """
        self.config = config or {}
        
        # Initialize agents
        self.email_fetcher = EmailFetcher(config.get('email_fetcher', {}))
        self.email_analyzer = EmailAnalyzer(config.get('email_analyzer', {}))
        self.reply_generator = ReplyGenerator(config.get('reply_generator', {}))
        self.newsletter_processor = NewsletterProcessor(config.get('newsletter_processor', {}))
        self.post_formatter = PostFormatter(config.get('post_formatter', {}))
        self.social_poster = SocialPoster(config.get('social_poster', {}))
        
        # Initialize state
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize all agents."""
        if self.initialized:
            return
            
        logger.info("Initializing EmailOrchestrator and all agents")
        
        # Initialize all agents
        await self.email_fetcher.initialize()
        await self.email_analyzer.initialize()
        await self.reply_generator.initialize()
        await self.newsletter_processor.initialize()
        await self.post_formatter.initialize()
        await self.social_poster.initialize()
        
        self.initialized = True
    
    async def process_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an email through the agent pipeline.
        
        Args:
            email_data: Dictionary containing email data.
            
        Returns:
            Dict containing the processing results.
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            # Step 1: Analyze the email
            analysis = await self.email_analyzer.analyze_email(email_data)
            
            # Step 2: Determine if it's a newsletter
            is_newsletter = any(cat in ["newsletter", "marketing"] 
                              for cat in analysis.get("categories", []))
            result = {
                "email_id": email_data.get("id"),
                "subject": email_data.get("subject"),
                "from": email_data.get("from"),
                "analysis": analysis,
                "is_newsletter": is_newsletter,
                "actions_taken": [],
                "generated_responses": [],
                "social_posts": []
            }
            
            # Step 3: Handle newsletters
            if is_newsletter:
                processed_newsletter = await self.newsletter_processor.process_newsletter(email_data)
                articles = await self.newsletter_processor.extract_articles(processed_newsletter)
                
                # Format articles as social posts
                for article in articles:
                    # Format for Twitter
                    twitter_post = await self.post_formatter.format_post(
                        article, 
                        platform="twitter",
                        style="engaging"
                    )
                    
                    # Format for LinkedIn
                    linkedin_post = await self.post_formatter.format_post(
                        article,
                        platform="linkedin",
                        style="professional"
                    )
                    
                    result["social_posts"].extend([twitter_post, linkedin_post])
                
                result["actions_taken"].append("processed_newsletter")
                
                # Optionally post to social media
                for post in result["social_posts"]:
                    try:
                        await self.social_poster.post(
                            platform=post["platform"],
                            content=post["content"]
                        )
                        result["actions_taken"].append(f"posted_to_{post['platform']}")
                    except Exception as e:
                        logger.error(f"Error posting to {post['platform']}: {str(e)}")
            
            # Step 4: Generate reply if needed
            if analysis.get("requires_response", False):
                reply = await self.reply_generator.generate_reply(
                    email_data=email_data,
                    context=analysis
                )
                result["generated_responses"].append(reply)
                result["actions_taken"].append("generated_reply")
            
            result["status"] = "success"
            result["timestamp"] = datetime.utcnow().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing email: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "email_id": email_data.get("id"),
                "timestamp": datetime.utcnow().isoformat()
            }
