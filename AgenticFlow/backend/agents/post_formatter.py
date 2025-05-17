"""Post Formatter Agent

This agent formats content for social media posts according to platform-specific requirements.
"""
import logging
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)

class Platform(Enum):
    """Supported social media platforms."""
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"

class PostFormatter:
    """Agent responsible for formatting content for social media."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the PostFormatter agent.
        
        Args:
            config: Configuration dictionary for the agent.
        """
        self.config = config or {}
        self.initialized = False
        self.platform_limits = {
            Platform.TWITTER: 280,
            Platform.LINKEDIN: 3000,
            Platform.FACEBOOK: 63206,
            Platform.INSTAGRAM: 2200
        }
    
    async def initialize(self) -> None:
        """Initialize the agent and any required models/services."""
        if self.initialized:
            return
            
        # Initialize any models or services here
        logger.info("Initializing PostFormatter agent")
        self.initialized = True
    
    async def format_post(
        self,
        content: Dict[str, Any],
        platform: Platform,
        style: str = "professional",
        include_hashtags: bool = True,
        include_mentions: bool = False,
        max_length: Optional[int] = None
    ) -> Dict[str, Any]:
        """Format content for a specific social media platform.
        
        Args:
            content: The content to format.
            platform: Target platform for the post.
            style: Desired writing style (e.g., professional, casual).
            include_hashtags: Whether to include relevant hashtags.
            include_mentions: Whether to include @mentions.
            max_length: Maximum length for the post (defaults to platform limit).
            
        Returns:
            Dictionary containing the formatted post and metadata.
        """
        if not self.initialized:
            await self.initialize()
            
        platform_name = platform.value if isinstance(platform, Platform) else platform
        logger.info(f"Formatting post for {platform_name} in {style} style")
        
        # Get platform-specific length limit
        platform_limit = self.platform_limits.get(platform, 1000)
        max_len = min(max_length, platform_limit) if max_length else platform_limit
        
        # Placeholder for post formatting logic
        formatted_post = {
            "platform": platform_name,
            "content": f"{content.get('title', 'Check this out!')}\n\n{content.get('summary', 'Interesting content')}",
            "style": style,
            "length": len(content.get('summary', '')),
            "max_length": max_len,
            "formatted_length": 0,
            "truncated": False,
            "hashtags": ["#tech", "#news"] if include_hashtags else [],
            "mentions": ["@example"] if include_mentions else []
        }
        
        # Truncate if necessary
        if formatted_post["length"] > max_len:
            formatted_post["content"] = formatted_post["content"][:max_len-3] + "..."
            formatted_post["truncated"] = True
            formatted_post["formatted_length"] = max_len
        else:
            formatted_post["formatted_length"] = formatted_post["length"]
        
        return formatted_post
    
    async def batch_format(
        self,
        contents: List[Dict[str, Any]],
        platform: Platform,
        **format_kwargs
    ) -> List[Dict[str, Any]]:
        """Format multiple pieces of content for the same platform.
        
        Args:
            contents: List of content items to format.
            platform: Target platform for the posts.
            **format_kwargs: Additional arguments to pass to format_post.
            
        Returns:
            List of formatted posts.
        """
        if not self.initialized:
            await self.initialize()
            
        formatted_posts = []
        for content in contents:
            post = await self.format_post(content, platform, **format_kwargs)
            formatted_posts.append(post)
            
        return formatted_posts


# Example usage
if __name__ == "__main__":
    import asyncio
    from .post_formatter import Platform
    
    async def main():
        formatter = PostFormatter()
        
        test_content = {
            "title": "Exciting News!",
            "summary": "We're thrilled to announce our latest product that will revolutionize the industry.",
            "url": "https://example.com/new-product"
        }
        
        # Format for Twitter
        twitter_post = await formatter.format_post(
            content=test_content,
            platform=Platform.TWITTER,
            style="engaging",
            include_hashtags=True
        )
        print(f"Twitter post: {twitter_post}")
        
        # Format for LinkedIn
        linkedin_post = await formatter.format_post(
            content=test_content,
            platform=Platform.LINKEDIN,
            style="professional"
        )
        print(f"LinkedIn post: {linkedin_post}")
    
    asyncio.run(main())
