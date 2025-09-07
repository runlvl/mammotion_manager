"""Redis-based session management with proper persistence."""

import json
import secrets
import time
from typing import Any, Dict, Optional

import redis.asyncio as redis
import structlog

from ..config import get_settings
from .exceptions import SessionError

logger = structlog.get_logger(__name__)


class SessionManager:
    """Redis-based session manager with automatic expiration."""
    
    def __init__(self) -> None:
        self.settings = get_settings()
        self._redis: Optional[redis.Redis] = None
        self._session_prefix = "mammotion:session:"
        self._user_sessions_prefix = "mammotion:user_sessions:"
    
    async def _get_redis(self) -> redis.Redis:
        """Get Redis connection with lazy initialization."""
        if self._redis is None:
            try:
                config = self.settings.get_redis_config()
                self._redis = redis.from_url(**config)
                # Test connection
                await self._redis.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.error("Failed to connect to Redis", error=str(e))
                raise SessionError(f"Redis connection failed: {e}")
        
        return self._redis
    
    async def create_session(self, user_email: str, session_data: Dict[str, Any]) -> str:
        """Create a new session with automatic expiration."""
        session_id = secrets.token_urlsafe(32)
        redis_client = await self._get_redis()
        
        # Prepare session data
        session_info = {
            "user_email": user_email,
            "created_at": time.time(),
            "last_accessed": time.time(),
            **session_data
        }
        
        try:
            # Store session data
            session_key = f"{self._session_prefix}{session_id}"
            expire_seconds = self.settings.SESSION_EXPIRE_HOURS * 3600
            
            await redis_client.setex(
                session_key,
                expire_seconds,
                json.dumps(session_info)
            )
            
            # Track user sessions for cleanup
            user_sessions_key = f"{self._user_sessions_prefix}{user_email}"
            await redis_client.sadd(user_sessions_key, session_id)
            await redis_client.expire(user_sessions_key, expire_seconds)
            
            logger.info("Session created", session_id=session_id, user=user_email)
            return session_id
            
        except Exception as e:
            logger.error("Failed to create session", error=str(e), user=user_email)
            raise SessionError(f"Session creation failed: {e}")
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data and update last accessed time."""
        if not session_id:
            return None
        
        redis_client = await self._get_redis()
        session_key = f"{self._session_prefix}{session_id}"
        
        try:
            session_data = await redis_client.get(session_key)
            if not session_data:
                return None
            
            session_info = json.loads(session_data)
            
            # Update last accessed time
            session_info["last_accessed"] = time.time()
            expire_seconds = self.settings.SESSION_EXPIRE_HOURS * 3600
            
            await redis_client.setex(
                session_key,
                expire_seconds,
                json.dumps(session_info)
            )
            
            return session_info
            
        except Exception as e:
            logger.error("Failed to get session", error=str(e), session_id=session_id)
            return None
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data."""
        if not session_id:
            return False
        
        redis_client = await self._get_redis()
        session_key = f"{self._session_prefix}{session_id}"
        
        try:
            session_data = await redis_client.get(session_key)
            if not session_data:
                return False
            
            session_info = json.loads(session_data)
            session_info.update(updates)
            session_info["last_accessed"] = time.time()
            
            expire_seconds = self.settings.SESSION_EXPIRE_HOURS * 3600
            await redis_client.setex(
                session_key,
                expire_seconds,
                json.dumps(session_info)
            )
            
            return True
            
        except Exception as e:
            logger.error("Failed to update session", error=str(e), session_id=session_id)
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a specific session."""
        if not session_id:
            return False
        
        redis_client = await self._get_redis()
        session_key = f"{self._session_prefix}{session_id}"
        
        try:
            # Get session info to clean up user sessions tracking
            session_data = await redis_client.get(session_key)
            if session_data:
                session_info = json.loads(session_data)
                user_email = session_info.get("user_email")
                
                if user_email:
                    user_sessions_key = f"{self._user_sessions_prefix}{user_email}"
                    await redis_client.srem(user_sessions_key, session_id)
            
            # Delete the session
            deleted = await redis_client.delete(session_key)
            
            if deleted:
                logger.info("Session deleted", session_id=session_id)
            
            return bool(deleted)
            
        except Exception as e:
            logger.error("Failed to delete session", error=str(e), session_id=session_id)
            return False
    
    async def delete_user_sessions(self, user_email: str) -> int:
        """Delete all sessions for a user."""
        redis_client = await self._get_redis()
        user_sessions_key = f"{self._user_sessions_prefix}{user_email}"
        
        try:
            # Get all session IDs for the user
            session_ids = await redis_client.smembers(user_sessions_key)
            
            if not session_ids:
                return 0
            
            # Delete all sessions
            session_keys = [f"{self._session_prefix}{sid}" for sid in session_ids]
            deleted = await redis_client.delete(*session_keys, user_sessions_key)
            
            logger.info("User sessions deleted", user=user_email, count=len(session_ids))
            return len(session_ids)
            
        except Exception as e:
            logger.error("Failed to delete user sessions", error=str(e), user=user_email)
            return 0
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions (called by background task)."""
        redis_client = await self._get_redis()
        
        try:
            # Redis automatically handles expiration, but we can clean up orphaned user session sets
            pattern = f"{self._user_sessions_prefix}*"
            keys = []
            
            async for key in redis_client.scan_iter(match=pattern):
                keys.append(key)
            
            cleaned = 0
            for key in keys:
                # Check if the set is empty (all sessions expired)
                if await redis_client.scard(key) == 0:
                    await redis_client.delete(key)
                    cleaned += 1
            
            if cleaned > 0:
                logger.info("Cleaned up orphaned user session sets", count=cleaned)
            
            return cleaned
            
        except Exception as e:
            logger.error("Failed to cleanup expired sessions", error=str(e))
            return 0
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            logger.info("Redis connection closed")


# Global session manager instance
_session_manager: Optional[SessionManager] = None


async def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
