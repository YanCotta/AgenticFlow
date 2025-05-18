"""
Social Media API Endpoints

This module contains FastAPI endpoints for social media operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

# Import agents
from agents.post_formatter import PostFormatter, Platform
from agents.social_poster import SocialPoster

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/social", tags=["social"])

# OAuth2 scheme for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Initialize agents
post_formatter = PostFormatter()
social_poster = SocialPoster()

# Models
class SocialPost(BaseModel):
    """Social media post model."""
    platform: str
    content: str
    media_urls: Optional[List[str]] = None
    scheduled_time: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class SocialPostResponse(SocialPost):
    """Response model for social media posts."""
    id: str
    status: str
    url: Optional[str] = None
    created_at: datetime

class BatchPostRequest(BaseModel):
    """Request model for batch posting."""
    posts: List[SocialPost]
    publish_immediately: bool = False

class BatchPostResponse(BaseModel):
    """Response model for batch posting."""
    results: List[Dict[str, Any]]
    success_count: int
    failure_count: int

# Routes
@router.get("/newsletters", response_model=List[Dict[str, Any]])
async def get_newsletters(
    skip: int = 0,
    limit: int = 10,
    token: str = Depends(oauth2_scheme)
):
    """
    Get a list of newsletters with their status.
    
    Args:
        skip: Number of items to skip
        limit: Maximum number of items to return
        
    Returns:
        List of newsletters with basic information
    """
    try:
        # In a real implementation, this would fetch from the database
        # and include actual newsletter data
        logger.info(f"Fetching newsletters (skip={skip}, limit={limit})")
        
        # Mock data for demonstration
        newsletters = [
            {
                "id": f"newsletter_{i}",
                "title": f"Newsletter {i+1}",
                "status": "draft" if i % 3 == 0 else "published",
                "created_at": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                "platforms": ["linkedin", "twitter"] if i % 2 == 0 else ["linkedin"]
            }
            for i in range(1, limit + 1)
        ]
        
        return newsletters
        
    except Exception as e:
        logger.error(f"Error fetching newsletters: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching newsletters"
        )

@router.post("/posts/approve/{post_id}", response_model=Dict[str, Any])
async def approve_post(
    post_id: str,
    platform: str,
    scheduled_time: Optional[datetime] = None,
    token: str = Depends(oauth2_scheme)
):
    """
    Approve a social media post.
    
    Args:
        post_id: ID of the post to approve
        platform: Target platform (e.g., 'linkedin', 'twitter')
        scheduled_time: When to schedule the post (if None, post immediately)
        
    Returns:
        Confirmation of approval
    """
    try:
        logger.info(f"Approving post {post_id} for platform {platform}")
        
        # In a real implementation, this would update the post status
        # and trigger the actual posting or scheduling
        
        return {
            "status": "approved",
            "post_id": post_id,
            "platform": platform,
            "scheduled_time": scheduled_time.isoformat() if scheduled_time else None,
            "approved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error approving post {post_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error approving post: {str(e)}"
        )

@router.post("/posts", response_model=SocialPostResponse)
async def create_post(
    post: SocialPost,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme)
):
    """
    Create a new social media post.
    
    This endpoint creates a post on the specified social media platform.
    The post can be published immediately or scheduled for later.
    """
    try:
        # Format the post if needed
        formatted_post = await post_formatter.format_post(
            content={"content": post.content},
            platform=post.platform,
            style="professional"
        )
        
        # Schedule or post immediately
        if post.scheduled_time:
            # Schedule the post
            result = {
                "id": f"scheduled_{post.platform}_{int(datetime.utcnow().timestamp())}",
                "platform": post.platform,
                "content": formatted_post["content"],
                "scheduled_time": post.scheduled_time,
                "status": "scheduled",
                "created_at": datetime.utcnow()
            }
            
            # In a real app, you would schedule a background task here
            background_tasks.add_task(
                social_poster.post,
                platform=post.platform,
                content=formatted_post["content"],
                media_urls=post.media_urls,
                schedule_time=post.scheduled_time
            )
            
            return result
        else:
            # Post immediately
            post_result = await social_poster.post(
                platform=post.platform,
                content=formatted_post["content"],
                media_urls=post.media_urls
            )
            
            return {
                "id": post_result["post_id"],
                "platform": post.platform,
                "content": formatted_post["content"],
                "status": post_result["status"],
                "url": post_result.get("url"),
                "created_at": post_result["timestamp"]
            }
            
    except Exception as e:
        logger.error(f"Error creating social media post: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create social media post: {str(e)}"
        )

@router.post("/posts/batch", response_model=BatchPostResponse)
async def batch_create_posts(
    batch_request: BatchPostRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme)
):
    """
    Create multiple social media posts in a batch.
    
    This endpoint allows creating multiple posts across different platforms
    in a single request. Each post can have its own scheduling.
    """
    results = []
    success_count = 0
    failure_count = 0
    
    for post in batch_request.posts:
        try:
            # Format the post
            formatted_post = await post_formatter.format_post(
                content={"content": post.content},
                platform=post.platform,
                style="professional"
            )
            
            # Prepare post data
            post_data = {
                "platform": post.platform,
                "content": formatted_post["content"],
                "media_urls": post.media_urls or [],
                "schedule_time": post.scheduled_time if not batch_request.publish_immediately else None,
                "metadata": post.metadata or {}
            }
            
            # Add to background tasks
            background_tasks.add_task(
                social_poster.post,
                **post_data
            )
            
            result = {
                "status": "scheduled" if post.scheduled_time and not batch_request.publish_immediately else "queued",
                "platform": post.platform,
                "content_preview": formatted_post["content"][:100] + "...",
                "scheduled_time": post.scheduled_time,
                "success": True
            }
            success_count += 1
            
        except Exception as e:
            logger.error(f"Error adding post to batch: {str(e)}", exc_info=True)
            result = {
                "status": "failed",
                "platform": post.platform,
                "error": str(e),
                "success": False
            }
            failure_count += 1
            
        results.append(result)
    
    return BatchPostResponse(
        results=results,
        success_count=success_count,
        failure_count=failure_count
    )

@router.get("/platforms")
async def get_supported_platforms(token: str = Depends(oauth2_scheme)):
    """
    Get a list of supported social media platforms.
    
    This endpoint returns the list of platforms that the API can post to.
    """
    return {
        "platforms": [
            {"id": "twitter", "name": "Twitter", "max_post_length": 280},
            {"id": "linkedin", "name": "LinkedIn", "max_post_length": 3000},
            {"id": "facebook", "name": "Facebook", "max_post_length": 63206},
            {"id": "instagram", "name": "Instagram", "max_post_length": 2200}
        ]
    }

@router.get("/posts/{post_id}")
async def get_post_status(
    post_id: str,
    platform: str,
    token: str = Depends(oauth2_scheme)
):
    """
    Get the status of a social media post.
    
    This endpoint returns the current status and metrics of a previously
    created social media post.
    """
    try:
        # In a real app, this would fetch from the database
        # For now, return a mock response
        return {
            "id": post_id,
            "platform": platform,
            "status": "posted",
            "url": f"https://{platform}.com/posts/{post_id}",
            "metrics": {
                "likes": 42,
                "shares": 7,
                "comments": 3,
                "impressions": 1000
            },
            "created_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching post status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch post status: {str(e)}"
        )
