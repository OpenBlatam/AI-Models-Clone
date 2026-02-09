from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Any, Dict, List, Optional
import logging
from datetime import datetime
from typing import Any, List, Dict, Optional
import asyncio
"""
Core utility functions for the Onyx backend.
"""

logger = logging.getLogger(__name__)

async def process_document(document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a document and extract relevant information.
    
    Args:
        document: Dictionary containing document data
        
    Returns:
        Processed document with extracted information
    """
    try:
        # Add processing timestamp
        document['processed_at'] = datetime.utcnow().isoformat()
        
        # Extract basic metadata
        metadata = {
            'title': document.get('title', ''),
            'type': document.get('type', 'unknown'),
            'size': document.get('size', 0),
            'created_at': document.get('created_at'),
            'updated_at': document.get('updated_at')
        }
        
        document['metadata'] = metadata
        return document
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise

async def validate_user_access(user_id: str, resource_id: str) -> bool:
    """
    Validate if a user has access to a specific resource.
    
    Args:
        user_id: The ID of the user
        resource_id: The ID of the resource to check access for
        
    Returns:
        Boolean indicating if access is granted
    """
    try:
        # TODO: Implement actual access control logic
        return True
    except Exception as e:
        logger.error(f"Error validating user access: {str(e)}")
        return False

async def format_response(data: Any, status: str = "success", message: Optional[str] = None) -> Dict[str, Any]:
    """
    Format a standardized API response.
    
    Args:
        data: The data to include in the response
        status: Status of the response (success/error)
        message: Optional message to include
        
    Returns:
        Formatted response dictionary
    """
    response = {
        "status": status,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if message:
        response["message"] = message
        
    return response

async def handle_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Handle and format error responses.
    
    Args:
        error: The exception that occurred
        context: Optional context information
        
    Returns:
        Formatted error response
    """
    error_response = {
        "status": "error",
        "error": {
            "type": error.__class__.__name__,
            "message": str(error)
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if context:
        error_response["context"] = context
        
    logger.error(f"Error occurred: {str(error)}", extra={"context": context})
    return error_response 