"""
If-Return Pattern Implementation: Avoid Unnecessary Else Statements

This module demonstrates how to replace unnecessary else statements with
early return statements after if conditions for cleaner, more readable code.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_error_response(error_code: str, message: str, field: str = None) -> Dict[str, Any]:
    """Create standardized error response"""
    response = {
        "status": "failed",
        "error": {
            "code": error_code,
            "message": message
        }
    }
    if field:
        response["error"]["field"] = field
    return response

def create_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create standardized success response"""
    return {
        "status": "success",
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# MOCK DATABASE FUNCTIONS
# ============================================================================

async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Mock function to get user by ID"""
    await asyncio.sleep(0.01)
    if user_id == "valid_user":
        return {
            "id": user_id,
            "name": "John Doe",
            "is_active": True,
            "email": "john@example.com",
            "role": "user"
        }
    elif user_id == "inactive_user":
        return {
            "id": user_id,
            "name": "Jane Doe",
            "is_active": False,
            "email": "jane@example.com",
            "role": "user"
        }
    elif user_id == "admin_user":
        return {
            "id": user_id,
            "name": "Admin User",
            "is_active": True,
            "email": "admin@example.com",
            "role": "admin"
        }
    return None

async def get_post_by_id(post_id: str) -> Optional[Dict[str, Any]]:
    """Mock function to get post by ID"""
    await asyncio.sleep(0.01)
    if post_id == "valid_post":
        return {
            "id": post_id,
            "user_id": "valid_user",
            "content": "Original content",
            "created_at": datetime.now() - timedelta(hours=2),
            "is_deleted": False,
            "is_public": True,
            "status": "published"
        }
    elif post_id == "private_post":
        return {
            "id": post_id,
            "user_id": "valid_user",
            "content": "Private content",
            "created_at": datetime.now() - timedelta(hours=1),
            "is_deleted": False,
            "is_public": False,
            "status": "published"
        }
    elif post_id == "deleted_post":
        return {
            "id": post_id,
            "user_id": "valid_user",
            "content": "Deleted content",
            "created_at": datetime.now() - timedelta(days=1),
            "is_deleted": True,
            "is_public": True,
            "status": "deleted"
        }
    return None

async def get_order_by_id(order_id: str) -> Optional[Dict[str, Any]]:
    """Mock function to get order by ID"""
    await asyncio.sleep(0.01)
    if order_id == "pending_order":
        return {
            "id": order_id,
            "user_id": "valid_user",
            "status": "pending",
            "total": 99.99,
            "created_at": datetime.now() - timedelta(hours=1)
        }
    elif order_id == "confirmed_order":
        return {
            "id": order_id,
            "user_id": "valid_user",
            "status": "confirmed",
            "total": 149.99,
            "created_at": datetime.now() - timedelta(days=1)
        }
    return None

async def check_payment(order_id: str) -> bool:
    """Mock function to check payment status"""
    await asyncio.sleep(0.01)
    return order_id == "pending_order"  # Mock: only pending order has payment

async def has_user_liked_post(user_id: str, post_id: str) -> bool:
    """Mock function to check if user has liked a post"""
    await asyncio.sleep(0.01)
    return False  # Mock: user hasn't liked the post

async def is_duplicate_content(content: str, user_id: str) -> bool:
    """Mock function to check for duplicate content"""
    await asyncio.sleep(0.01)
    return False  # Mock: not duplicate

async def check_rate_limit(user_id: str, action: str) -> bool:
    """Mock function to check rate limit"""
    await asyncio.sleep(0.01)
    return True  # Mock: rate limit not exceeded

# ============================================================================
# MOCK BUSINESS LOGIC FUNCTIONS
# ============================================================================

async def create_post_in_database(user_id: str, content: str, hashtags: List[str] = None) -> Dict[str, Any]:
    """Mock function to create post in database"""
    await asyncio.sleep(0.05)
    return {
        "id": f"post_{uuid.uuid4().hex[:8]}",
        "user_id": user_id,
        "content": content,
        "hashtags": hashtags or [],
        "created_at": datetime.now(),
        "status": "published"
    }

async def update_post_in_database(post_id: str, new_content: str) -> Dict[str, Any]:
    """Mock function to update post in database"""
    await asyncio.sleep(0.05)
    return {
        "id": post_id,
        "content": new_content,
        "updated_at": datetime.now()
    }

async def update_order_status(order_id: str, status: str) -> None:
    """Mock function to update order status"""
    await asyncio.sleep(0.02)
    logger.info(f"Order {order_id} status updated to {status}")

async def add_like_to_post(user_id: str, post_id: str) -> None:
    """Mock function to add like to post"""
    await asyncio.sleep(0.02)
    logger.info(f"User {user_id} liked post {post_id}")

async def add_share_to_post(user_id: str, post_id: str) -> None:
    """Mock function to add share to post"""
    await asyncio.sleep(0.02)
    logger.info(f"User {user_id} shared post {post_id}")

async def add_comment_to_post(user_id: str, post_id: str, comment_text: str) -> None:
    """Mock function to add comment to post"""
    await asyncio.sleep(0.02)
    logger.info(f"User {user_id} commented on post {post_id}: {comment_text}")

async def update_user_profile(user_id: str, data: Dict[str, Any]) -> None:
    """Mock function to update user profile"""
    await asyncio.sleep(0.02)
    logger.info(f"User {user_id} profile updated with {data}")

async def delete_user_account(user_id: str) -> None:
    """Mock function to delete user account"""
    await asyncio.sleep(0.02)
    logger.info(f"User account {user_id} deleted")

async def upload_file(file) -> str:
    """Mock function to upload file"""
    await asyncio.sleep(0.1)
    return f"https://storage.example.com/files/{uuid.uuid4().hex[:8]}"

# ============================================================================
# IF-RETURN PATTERN IMPLEMENTATIONS
# ============================================================================

class PostService:
    """Service class demonstrating if-return pattern"""
    
    @staticmethod
    async def create_post_if_return(user_id: str, content: str, hashtags: List[str] = None) -> Dict[str, Any]:
        """
        Create a new post using if-return pattern.
        
        All validations use early returns, eliminating unnecessary else statements.
        """
        # Input validation with early returns
        if not user_id:
            return create_error_response("MISSING_USER_ID", "User ID is required", "user_id")
        
        if not content:
            return create_error_response("MISSING_CONTENT", "Content is required", "content")
        
        # Content validation with early returns
        content = content.strip()
        if len(content) < 10:
            return create_error_response("CONTENT_TOO_SHORT", "Content too short (minimum 10 characters)", "content")
        
        if len(content) > 3000:
            return create_error_response("CONTENT_TOO_LONG", "Content too long (maximum 3000 characters)", "content")
        
        # User validation with early returns
        user = await get_user_by_id(user_id)
        if not user:
            return create_error_response("USER_NOT_FOUND", "User not found", "user_id")
        
        if not user["is_active"]:
            return create_error_response("USER_INACTIVE", "Account is deactivated", "user_id")
        
        # Business rule validation with early returns
        if await is_duplicate_content(content, user_id):
            return create_error_response("DUPLICATE_CONTENT", "Duplicate content detected", "content")
        
        if not await check_rate_limit(user_id, "post_creation"):
            return create_error_response("RATE_LIMIT_EXCEEDED", "Rate limit exceeded", "user_id")
        
        # Happy path (no else needed)
        try:
            post_data = await create_post_in_database(user_id, content, hashtags)
            return create_success_response({
                "post_id": post_data["id"],
                "message": "Post created successfully",
                "created_at": post_data["created_at"].isoformat()
            })
        except Exception as e:
            logger.error(f"Error creating post: {e}")
            return create_error_response("CREATION_FAILED", f"Failed to create post: {str(e)}")
    
    @staticmethod
    async def process_post_engagement_if_return(post_id: str, user_id: str, action: str, comment_text: str = None) -> Dict[str, Any]:
        """
        Process post engagement using if-return pattern.
        
        Eliminates nested if-else statements with early returns.
        """
        # Input validation with early returns
        if not post_id:
            return create_error_response("MISSING_POST_ID", "Post ID is required", "post_id")
        
        if not user_id:
            return create_error_response("MISSING_USER_ID", "User ID is required", "user_id")
        
        if not action:
            return create_error_response("MISSING_ACTION", "Action is required", "action")
        
        # Action validation with early returns
        valid_actions = ['like', 'share', 'comment']
        if action not in valid_actions:
            return create_error_response("INVALID_ACTION", f"Invalid action. Must be one of: {', '.join(valid_actions)}", "action")
        
        # Comment validation with early returns
        if action == 'comment' and not comment_text:
            return create_error_response("MISSING_COMMENT", "Comment text is required for comment action", "comment_text")
        
        if action == 'comment' and comment_text and len(comment_text) > 1000:
            return create_error_response("COMMENT_TOO_LONG", "Comment too long (maximum 1000 characters)", "comment_text")
        
        # User validation with early returns
        user = await get_user_by_id(user_id)
        if not user:
            return create_error_response("USER_NOT_FOUND", "User not found", "user_id")
        
        if not user["is_active"]:
            return create_error_response("USER_INACTIVE", "Account is deactivated", "user_id")
        
        # Post validation with early returns
        post = await get_post_by_id(post_id)
        if not post:
            return create_error_response("POST_NOT_FOUND", "Post not found", "post_id")
        
        if post["is_deleted"]:
            return create_error_response("POST_DELETED", "Post is deleted", "post_id")
        
        # Access validation with early returns
        if post["user_id"] != user_id and not post["is_public"]:
            return create_error_response("ACCESS_DENIED", "Post is private", "post_id")
        
        # Duplicate like validation with early returns
        if action == 'like' and await has_user_liked_post(user_id, post_id):
            return create_error_response("ALREADY_LIKED", "Post already liked", "post_id")
        
        # Process engagement (happy path)
        try:
            if action == 'like':
                await add_like_to_post(user_id, post_id)
                engagement_type = "liked"
            elif action == 'share':
                await add_share_to_post(user_id, post_id)
                engagement_type = "shared"
            else:  # comment
                await add_comment_to_post(user_id, post_id, comment_text)
                engagement_type = "commented"
            
            return create_success_response({
                "action": engagement_type,
                "post_id": post_id,
                "user_id": user_id,
                "message": f"Post {engagement_type} successfully"
            })
        except Exception as e:
            logger.error(f"Error processing engagement: {e}")
            return create_error_response("ENGAGEMENT_FAILED", f"Failed to {action} post: {str(e)}")
    
    @staticmethod
    async def update_post_if_return(post_id: str, user_id: str, new_content: str) -> Dict[str, Any]:
        """
        Update post using if-return pattern.
        
        Eliminates nested validation with early returns.
        """
        # Input validation with early returns
        if not post_id:
            return create_error_response("MISSING_POST_ID", "Post ID is required", "post_id")
        
        if not user_id:
            return create_error_response("MISSING_USER_ID", "User ID is required", "user_id")
        
        if not new_content:
            return create_error_response("MISSING_CONTENT", "New content is required", "new_content")
        
        # Content validation with early returns
        new_content = new_content.strip()
        if len(new_content) < 10:
            return create_error_response("CONTENT_TOO_SHORT", "Content too short (minimum 10 characters)", "new_content")
        
        if len(new_content) > 3000:
            return create_error_response("CONTENT_TOO_LONG", "Content too long (maximum 3000 characters)", "new_content")
        
        # Post validation with early returns
        post = await get_post_by_id(post_id)
        if not post:
            return create_error_response("POST_NOT_FOUND", "Post not found", "post_id")
        
        if post["user_id"] != user_id:
            return create_error_response("UNAUTHORIZED_UPDATE", "Cannot update another user's post", "post_id")
        
        if post["is_deleted"]:
            return create_error_response("POST_DELETED", "Cannot update deleted post", "post_id")
        
        # Business rule validation with early returns
        post_age = datetime.now() - post["created_at"]
        if post_age > timedelta(hours=24):
            return create_error_response("EDIT_TIME_EXPIRED", "Post cannot be edited after 24 hours", "post_id")
        
        # Update post (happy path)
        try:
            updated_post = await update_post_in_database(post_id, new_content)
            return create_success_response({
                "post_id": post_id,
                "message": "Post updated successfully",
                "updated_at": updated_post["updated_at"].isoformat()
            })
        except Exception as e:
            logger.error(f"Error updating post: {e}")
            return create_error_response("UPDATE_FAILED", f"Failed to update post: {str(e)}")

class UserService:
    """Service class demonstrating if-return pattern for user operations"""
    
    @staticmethod
    async def handle_user_action_if_return(user_id: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle user actions using if-return pattern.
        
        Eliminates complex nested if-else structures with early returns.
        """
        # User validation with early returns
        user = await get_user_by_id(user_id)
        if not user:
            return create_error_response("USER_NOT_FOUND", "User not found", "user_id")
        
        if not user["is_active"]:
            return create_error_response("USER_INACTIVE", "Account is deactivated", "user_id")
        
        # Action handling with early returns
        if action == 'create_post':
            if not data.get('content'):
                return create_error_response("MISSING_CONTENT", "Content required for post creation", "content")
            
            post = await create_post_in_database(user_id, data['content'])
            return create_success_response({
                "action": "post_created",
                "post_id": post["id"],
                "message": "Post created successfully"
            })
        
        if action == 'update_profile':
            if not data.get('name'):
                return create_error_response("MISSING_NAME", "Name required for profile update", "name")
            
            await update_user_profile(user_id, data)
            return create_success_response({
                "action": "profile_updated",
                "message": "Profile updated successfully"
            })
        
        if action == 'delete_account':
            await delete_user_account(user_id)
            return create_success_response({
                "action": "account_deleted",
                "message": "Account deleted successfully"
            })
        
        # Invalid action (no else needed)
        return create_error_response("INVALID_ACTION", f"Invalid action: {action}", "action")

class FileService:
    """Service class demonstrating if-return pattern for file operations"""
    
    @staticmethod
    async def process_file_upload_if_return(user_id: str, file) -> Dict[str, Any]:
        """
        Process file upload using if-return pattern.
        
        Eliminates nested validation with early returns.
        """
        # File validation with early returns
        if not file:
            return create_error_response("MISSING_FILE", "File is required", "file")
        
        if not hasattr(file, 'filename') or not file.filename:
            return create_error_response("MISSING_FILENAME", "Filename is required", "file")
        
        if hasattr(file, 'size') and file.size > 5 * 1024 * 1024:  # 5MB
            return create_error_response("FILE_TOO_LARGE", "File too large (maximum 5MB)", "file")
        
        allowed_types = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
        if hasattr(file, 'content_type') and file.content_type not in allowed_types:
            return create_error_response("INVALID_FILE_TYPE", "Invalid file type. Only images are allowed", "file")
        
        # User validation with early returns
        user = await get_user_by_id(user_id)
        if not user:
            return create_error_response("USER_NOT_FOUND", "User not found", "user_id")
        
        if not user["is_active"]:
            return create_error_response("USER_INACTIVE", "Account is deactivated", "user_id")
        
        # Upload file (happy path)
        try:
            file_url = await upload_file(file)
            return create_success_response({
                "file_url": file_url,
                "filename": file.filename,
                "size": getattr(file, 'size', 0),
                "content_type": getattr(file, 'content_type', 'unknown')
            })
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return create_error_response("UPLOAD_FAILED", f"File upload failed: {str(e)}")

class OrderService:
    """Service class demonstrating if-return pattern for order operations"""
    
    @staticmethod
    async def process_order_if_return(order_id: str, user_id: str, action: str) -> Dict[str, Any]:
        """
        Process order using if-return pattern.
        
        Eliminates complex nested business logic with early returns.
        """
        # Order validation with early returns
        order = await get_order_by_id(order_id)
        if not order:
            return create_error_response("ORDER_NOT_FOUND", "Order not found", "order_id")
        
        if order["user_id"] != user_id:
            return create_error_response("UNAUTHORIZED_ORDER", "Cannot modify another user's order", "order_id")
        
        # Action validation based on order status with early returns
        if order["status"] == 'pending':
            if action == 'confirm':
                if not await check_payment(order_id):
                    return create_error_response("PAYMENT_INCOMPLETE", "Payment not completed", "order_id")
                
                await update_order_status(order_id, 'confirmed')
                return create_success_response({
                    "action": "order_confirmed",
                    "message": "Order confirmed successfully"
                })
            
            if action == 'cancel':
                await update_order_status(order_id, 'cancelled')
                return create_success_response({
                    "action": "order_cancelled",
                    "message": "Order cancelled successfully"
                })
            
            return create_error_response("INVALID_ACTION_PENDING", "Invalid action for pending order", "action")
        
        if order["status"] == 'confirmed':
            if action == 'ship':
                await update_order_status(order_id, 'shipped')
                return create_success_response({
                    "action": "order_shipped",
                    "message": "Order shipped successfully"
                })
            
            return create_error_response("INVALID_ACTION_CONFIRMED", "Invalid action for confirmed order", "action")
        
        # Order cannot be modified (no else needed)
        return create_error_response("ORDER_IMMUTABLE", "Order cannot be modified", "order_id")

# ============================================================================
# COMPARISON EXAMPLES: BAD vs GOOD
# ============================================================================

class ComparisonExamples:
    """Examples showing bad vs good patterns"""
    
    @staticmethod
    async def validate_user_bad(user_id: str) -> Dict[str, Any]:
        """❌ Bad: Unnecessary else statements"""
        if not user_id:
            return {"error": "User ID is required"}
        else:
            user = await get_user_by_id(user_id)
            if user:
                if user["is_active"]:
                    return {"status": "valid", "user": user}
                else:
                    return {"error": "Account is deactivated"}
            else:
                return {"error": "User not found"}
    
    @staticmethod
    async def validate_user_good(user_id: str) -> Dict[str, Any]:
        """✅ Good: If-return pattern"""
        if not user_id:
            return {"error": "User ID is required"}
        
        user = await get_user_by_id(user_id)
        if not user:
            return {"error": "User not found"}
        
        if not user["is_active"]:
            return {"error": "Account is deactivated"}
        
        return {"status": "valid", "user": user}
    
    @staticmethod
    async def process_post_bad(post_id: str, user_id: str, action: str) -> Dict[str, Any]:
        """❌ Bad: Nested if-else statements"""
        if post_id:
            if user_id:
                if action in ['like', 'share', 'comment']:
                    post = await get_post_by_id(post_id)
                    if post:
                        if post["user_id"] == user_id or post["is_public"]:
                            if action == 'like':
                                await add_like_to_post(user_id, post_id)
                                return {"status": "success", "action": "liked"}
                            else:
                                if action == 'share':
                                    await add_share_to_post(user_id, post_id)
                                    return {"status": "success", "action": "shared"}
                                else:
                                    await add_comment_to_post(user_id, post_id, "comment")
                                    return {"status": "success", "action": "commented"}
                        else:
                            return {"error": "Access denied"}
                    else:
                        return {"error": "Post not found"}
                else:
                    return {"error": "Invalid action"}
            else:
                return {"error": "User ID required"}
        else:
            return {"error": "Post ID required"}
    
    @staticmethod
    async def process_post_good(post_id: str, user_id: str, action: str) -> Dict[str, Any]:
        """✅ Good: If-return pattern"""
        if not post_id:
            return {"error": "Post ID required"}
        
        if not user_id:
            return {"error": "User ID required"}
        
        if action not in ['like', 'share', 'comment']:
            return {"error": "Invalid action"}
        
        post = await get_post_by_id(post_id)
        if not post:
            return {"error": "Post not found"}
        
        if post["user_id"] != user_id and not post["is_public"]:
            return {"error": "Access denied"}
        
        # Process the action
        if action == 'like':
            await add_like_to_post(user_id, post_id)
            return {"status": "success", "action": "liked"}
        
        if action == 'share':
            await add_share_to_post(user_id, post_id)
            return {"status": "success", "action": "shared"}
        
        # Default case: comment
        await add_comment_to_post(user_id, post_id, "comment")
        return {"status": "success", "action": "commented"}

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

async def demonstrate_if_return_pattern():
    """Demonstrate the if-return pattern with various scenarios"""
    
    post_service = PostService()
    user_service = UserService()
    file_service = FileService()
    order_service = OrderService()
    comparison = ComparisonExamples()
    
    print("=" * 80)
    print("IF-RETURN PATTERN DEMONSTRATION")
    print("=" * 80)
    
    # Test 1: Successful post creation
    print("\n1. SUCCESSFUL POST CREATION (If-Return Pattern):")
    result = await post_service.create_post_if_return(
        user_id="valid_user",
        content="This is a test post with sufficient content length to pass validation.",
        hashtags=["test", "demo"]
    )
    print(f"Result: {result}")
    
    # Test 2: Failed post creation (validation error)
    print("\n2. FAILED POST CREATION (Content too short):")
    result = await post_service.create_post_if_return(
        user_id="valid_user",
        content="Short",
        hashtags=["test"]
    )
    print(f"Result: {result}")
    
    # Test 3: Successful engagement
    print("\n3. SUCCESSFUL ENGAGEMENT (Like):")
    result = await post_service.process_post_engagement_if_return(
        post_id="valid_post",
        user_id="valid_user",
        action="like"
    )
    print(f"Result: {result}")
    
    # Test 4: Failed engagement (invalid action)
    print("\n4. FAILED ENGAGEMENT (Invalid action):")
    result = await post_service.process_post_engagement_if_return(
        post_id="valid_post",
        user_id="valid_user",
        action="invalid_action"
    )
    print(f"Result: {result}")
    
    # Test 5: User action handling
    print("\n5. USER ACTION HANDLING (Create post):")
    result = await user_service.handle_user_action_if_return(
        user_id="valid_user",
        action="create_post",
        data={"content": "Test post content"}
    )
    print(f"Result: {result}")
    
    # Test 6: Order processing
    print("\n6. ORDER PROCESSING (Confirm order):")
    result = await order_service.process_order_if_return(
        order_id="pending_order",
        user_id="valid_user",
        action="confirm"
    )
    print(f"Result: {result}")
    
    # Test 7: Comparison - Bad vs Good
    print("\n7. COMPARISON - BAD vs GOOD PATTERNS:")
    
    print("\n   Bad Pattern (Nested if-else):")
    result_bad = await comparison.validate_user_bad("valid_user")
    print(f"   Result: {result_bad}")
    
    print("\n   Good Pattern (If-return):")
    result_good = await comparison.validate_user_good("valid_user")
    print(f"   Result: {result_good}")
    
    # Test 8: Complex validation chain
    print("\n8. COMPLEX VALIDATION CHAIN (If-return pattern):")
    result = await post_service.update_post_if_return(
        post_id="valid_post",
        user_id="valid_user",
        new_content="This is the updated content with sufficient length to pass all validations."
    )
    print(f"Result: {result}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(demonstrate_if_return_pattern()) 