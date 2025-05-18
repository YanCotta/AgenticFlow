"""Orchestration Module

This module defines the CrewAI crews and tasks for coordinating the email and social media workflows.
"""
import logging
from typing import Dict, List, Optional, Any
from crewai import Agent, Task, Crew, Process
from datetime import datetime

from .agents.email_fetcher import EmailFetcher
from .agents.email_analyzer import EmailAnalyzer
from .agents.reply_generator import ReplyGenerator
from .agents.newsletter_processor import NewsletterProcessor
from .agents.post_formatter import PostFormatter, Platform
from .agents.social_poster import SocialPoster, PostStatus

logger = logging.getLogger(__name__)

class EmailCrew:
    """Crew for handling email-related tasks."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the EmailCrew with agents and tasks."""
        self.config = config or {}
        self.email_fetcher = EmailFetcher(config.get('email_fetcher', {}))
        self.email_analyzer = EmailAnalyzer(config.get('email_analyzer', {}))
        self.reply_generator = ReplyGenerator(config.get('reply_generator', {}))
        
        # Initialize agents with proper integration
        self.fetch_agent = Agent(
            role='Email Fetcher',
            goal='Retrieve unread emails from Gmail',
            backstory='Specialized in efficiently fetching and filtering emails',
            tools=[self.email_fetcher],
            verbose=True
        )
        
        self.analysis_agent = Agent(
            role='Email Analyst',
            goal='Analyze email content and categorize it',
            backstory='Expert in understanding and categorizing email content',
            tools=[self.email_analyzer],
            verbose=True
        )
        
        self.reply_agent = Agent(
            role='Reply Composer',
            goal='Generate appropriate email replies',
            backstory='Skilled at crafting professional and context-appropriate email responses',
            tools=[self.reply_generator],
            verbose=True
        )
        
        # Define tasks with proper context and expected outputs
        self.tasks = [
            Task(
                description='Fetch unread emails from Gmail',
                agent=self.fetch_agent,
                expected_output='List of unread emails with metadata',
                async_execution=True,
                output_file='fetched_emails.json'  # Optional: save output for debugging
            ),
            Task(
                description='Analyze fetched emails and categorize them',
                agent=self.analysis_agent,
                expected_output='Categorized emails with analysis results including sentiment, intent, and priority',
                context=[self.tasks[0]],
                output_file='analyzed_emails.json'  # Optional: save output for debugging
            ),
            Task(
                description='Generate draft replies for emails that need responses',
                agent=self.reply_agent,
                expected_output='Draft replies ready for review, including confidence scores',
                context=[self.tasks[1]],
                output_file='draft_replies.json'  # Optional: save output for debugging
            )
        ]
        
        # Create crew
        self.crew = Crew(
            agents=[self.fetch_agent, self.analysis_agent, self.reply_agent],
            tasks=self.tasks,
            process=Process.sequential,
            verbose=2
        )
    
    async def run(self) -> Dict[str, Any]:
        """Run the email processing workflow."""
        logger.info("Starting EmailCrew workflow")
        try:
            # Initialize all agents
            await asyncio.gather(
                self.email_fetcher.initialize(),
                self.email_analyzer.initialize(),
                self.reply_generator.initialize()
            )
            
            # Execute the crew
            result = await self.crew.kickoff()
            logger.info("EmailCrew workflow completed successfully")
            return {"status": "success", "result": result}
            
        except Exception as e:
            logger.error(f"Error in EmailCrew workflow: {e}")
            return {"status": "error", "error": str(e)}


class SocialCrew:
    """Crew for handling social media posting workflow."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the SocialCrew with agents and tasks."""
        self.config = config or {}
        self.newsletter_processor = NewsletterProcessor(config.get('newsletter_processor', {}))
        self.post_formatter = PostFormatter(config.get('post_formatter', {}))
        self.social_poster = SocialPoster(config.get('social_poster', {}))
        
        # Initialize agents with proper integration
        self.newsletter_agent = Agent(
            role='Newsletter Processor',
            goal='Extract and process content from newsletters',
            backstory='Specialized in analyzing and extracting valuable content from newsletters',
            tools=[self.newsletter_processor],
            verbose=True
        )
        
        self.formatting_agent = Agent(
            role='Content Formatter',
            goal='Format content for different social media platforms',
            backstory='Expert in adapting content for optimal engagement on various platforms',
            tools=[self.post_formatter],
            verbose=True
        )
        
        self.posting_agent = Agent(
            role='Social Media Manager',
            goal='Schedule and post content to social media',
            backstory='Skilled at managing and optimizing social media content distribution',
            tools=[self.social_poster],
            verbose=True
        )
        
        # Define tasks with detailed descriptions and expected outputs
        self.tasks = [
            Task(
                description='Process newsletter content and extract key information including main topics, key points, and call-to-actions',
                agent=self.newsletter_agent,
                expected_output='Structured content with extracted sections, key points, and metadata',
                async_execution=True,
                output_file='processed_newsletter.json'  # Optional: save output for debugging
            ),
            Task(
                description='Format extracted content for different social media platforms (X, LinkedIn)',
                agent=self.formatting_agent,
                expected_output='Platform-specific posts with appropriate formatting, hashtags, and character limits',
                context=[self.tasks[0]],
                output_file='formatted_posts.json'  # Optional: save output for debugging
            ),
            Task(
                description='Schedule and post the formatted content to respective platforms',
                agent=self.posting_agent,
                expected_output='Confirmation of successful posts or scheduled posts with timestamps',
                context=[self.tasks[1]],
                output_file='posting_results.json'  # Optional: save output for debugging
            )
        ]
        
        # Create crew
        self.crew = Crew(
            agents=[self.newsletter_agent, self.formatting_agent, self.posting_agent],
            tasks=self.tasks,
            process=Process.sequential,
            verbose=2
        )
    
    async def run(self) -> Dict[str, Any]:
        """Run the social media posting workflow."""
        logger.info("Starting SocialCrew workflow")
        try:
            # Initialize all agents
            await asyncio.gather(
                self.newsletter_processor.initialize(),
                self.post_formatter.initialize(),
                self.social_poster.initialize()
            )
            
            # Connect to social media platforms
            platforms = self.config.get('social_platforms', [])
            for platform in platforms:
                await self.social_poster.connect_platform(
                    platform=platform['name'],
                    credentials=platform.get('credentials', {})
                )
            
            # Execute the crew
            result = await self.crew.kickoff()
            logger.info("SocialCrew workflow completed successfully")
            return {"status": "success", "result": result}
            
        except Exception as e:
            logger.error(f"Error in SocialCrew workflow: {e}")
            return {"status": "error", "error": str(e)}


async def run_orchestration(config: Optional[Dict] = None) -> Dict:
    """Run the complete orchestration workflow.
    
    Args:
        config: Configuration dictionary for the orchestrator and agents.
        
    Returns:
        Dictionary containing the results of both crews.
    """
    import asyncio
    from datetime import datetime
    
    logger.info("Starting orchestration workflow")
    start_time = datetime.utcnow()
    
    try:
        # Initialize crews
        email_crew = EmailCrew(config)
        social_crew = SocialCrew(config)
        
        # Initialize agents
        logger.info("Initializing agents...")
        await asyncio.gather(
            email_crew.email_fetcher.initialize(),
            email_crew.email_analyzer.initialize(),
            email_crew.reply_generator.initialize(),
            social_crew.newsletter_processor.initialize(),
            social_crew.post_formatter.initialize(),
            social_crew.social_poster.initialize()
        )
        
        # Run email processing
        logger.info("Running email processing crew...")
        email_results = await email_crew.run()
        logger.info(f"Email processing completed. Processed {len(email_results.get('processed_emails', []))} emails.")
        
        # Only proceed with social media if we have content to post
        if email_results.get('has_newsletter_content', False):
            # Run social media processing
            logger.info("Running social media processing crew...")
            social_results = await social_crew.run()
            logger.info(f"Social media processing completed. Posted to {len(social_results.get('posted_content', []))} platforms.")
        else:
            social_results = {'status': 'skipped', 'reason': 'No newsletter content found'}
            logger.info("Skipping social media processing - no newsletter content to post.")
        
        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(f"Orchestration completed in {duration:.2f} seconds")
        return {
            'status': 'success',
            'duration_seconds': duration,
            'email_processing': email_results,
            'social_media_processing': social_results,
            'completed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error during orchestration: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'error': str(e),
            'completed_at': datetime.utcnow().isoformat()
        }


# Example usage
if __name__ == "__main__":
    import asyncio
    import os
    from dotenv import load_dotenv
    
    async def main():
        # Load environment variables
        load_dotenv()
        
        # Configuration
        config = {
            "email_crew": {
                "email_fetcher": {
                    "credentials": {
                        "token": os.getenv("GMAIL_ACCESS_TOKEN"),
                        "refresh_token": os.getenv("GMAIL_REFRESH_TOKEN"),
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    }
                }
            },
            "social_crew": {
                "social_platforms": [
                    {
                        "name": "twitter",
                        "credentials": {
                            "api_key": os.getenv("TWITTER_API_KEY"),
                            "api_secret": os.getenv("TWITTER_API_SECRET"),
                            "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
                            "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
                        }
                    },
                    {
                        "name": "linkedin",
                        "credentials": {
                            "client_id": os.getenv("LINKEDIN_CLIENT_ID"),
                            "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET"),
                            "access_token": os.getenv("LINKEDIN_ACCESS_TOKEN")
                        }
                    }
                ]
            }
        }
        
        # Run the orchestration
        result = await run_orchestration(config)
        print("Orchestration result:", result)
    
    asyncio.run(main())
