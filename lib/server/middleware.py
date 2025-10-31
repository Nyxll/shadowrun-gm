"""
Middleware Components for FastAPI
"""

import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from .logging_setup import trace_logger, trace_id_var


class TraceIDMiddleware(BaseHTTPMiddleware):
    """Middleware to handle trace ID for distributed tracing"""
    
    async def dispatch(self, request: Request, call_next):
        # Extract trace ID from header or generate new one
        trace_id = request.headers.get('X-Trace-ID') or str(uuid.uuid4())
        
        # Set in context variable for use throughout request
        trace_id_var.set(trace_id)
        
        # Log request with trace ID using structured logger
        trace_logger.info(f"{request.method} {request.url.path}")
        
        try:
            # Process request
            response = await call_next(request)
            
            # Log response status
            trace_logger.info(f"{request.method} {request.url.path} - {response.status_code}")
            
            # Add trace ID to response headers
            response.headers['X-Trace-ID'] = trace_id
            
            return response
            
        except Exception as e:
            # Log errors with trace ID
            trace_logger.error(f"{request.method} {request.url.path} - Error: {str(e)}")
            raise
