# mcp-server/storage.py
import json
import hashlib
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import redis.asyncio as redis
from redis.asyncio import Redis

from .models import ContextData, ContextMetadata, ContextStatus
from .config import settings

logger = logging.getLogger(__name__)

class ContextStorage:
    """Redis-based context storage with advanced features."""
    
    def __init__(self):
        self.redis: Optional[Redis] = None
        self.context_prefix = "mcp:context:"
        self.index_prefix = "mcp:index:"
        self.stats_key = "mcp:stats"
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis = redis.from_url(
                settings.redis_url,
                password=settings.redis_password,
                decode_responses=True,
                encoding='utf-8'
            )
            await self.redis.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
    
    def _get_context_key(self, context_id: str) -> str:
        """Get Redis key for context."""
        return f"{self.context_prefix}{context_id}"
    
    def _get_index_key(self, index_type: str, value: str) -> str:
        """Get Redis key for index."""
        return f"{self.index_prefix}{index_type}:{value}"
    
    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate MD5 checksum of context data."""
        content = json.dumps(data, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    async def store_context(
        self, 
        context_id: UUID, 
        context_data: ContextData,
        ttl: Optional[int] = None
    ) -> bool:
        """Store context in Redis with indexing."""
        try:
            key = self._get_context_key(str(context_id))
            
            # Calculate checksum
            context_data.checksum = self._calculate_checksum(context_data.content)
            
            # Store context
            context_json = context_data.json()
            
            if ttl:
                await self.redis.setex(key, ttl, context_json)
            else:
                await self.redis.set(key, context_json)
                if settings.context_ttl > 0:
                    await self.redis.expire(key, settings.context_ttl)
            
            # Update indexes
            await self._update_indexes(str(context_id), context_data.metadata)
            
            # Update stats
            await self.redis.hincrby(self.stats_key, "contexts_created", 1)
            
            logger.debug(f"Stored context {context_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store context {context_id}: {e}")
            return False
    
    async def get_context(self, context_id: UUID) -> Optional[ContextData]:
        """Retrieve context from Redis."""
        try:
            key = self._get_context_key(str(context_id))
            context_json = await self.redis.get(key)
            
            if not context_json:
                return None
            
            context_data = ContextData.parse_raw(context_json)
            
            # Update access time
            context_data.metadata.accessed_at = datetime.utcnow()
            await self.redis.set(key, context_data.json())
            
            # Update stats
            await self.redis.hincrby(self.stats_key, "contexts_accessed", 1)
            
            return context_data
            
        except Exception as e:
            logger.error(f"Failed to get context {context_id}: {e}")
            return None
    
    async def update_context(
        self, 
        context_id: UUID, 
        updates: Dict[str, Any],
        increment_version: bool = True
    ) -> Optional[ContextData]:
        """Update context data."""
        try:
            context_data = await self.get_context(context_id)
            if not context_data:
                return None
            
            # Update metadata
            context_data.metadata.updated_at = datetime.utcnow()
            
            # Update content if provided
            if 'data' in updates and updates['data']:
                context_data.content.update(updates['data'])
                if increment_version:
                    context_data.version += 1
            
            # Update metadata fields
            for field in ['tags', 'description', 'priority', 'status']:
                if field in updates and updates[field] is not None:
                    setattr(context_data.metadata, field, updates[field])
            
            # Store updated context
            await self.store_context(context_id, context_data)
            
            return context_data
            
        except Exception as e:
            logger.error(f"Failed to update context {context_id}: {e}")
            return None
    
    async def delete_context(self, context_id: UUID) -> bool:
        """Delete context from Redis."""
        try:
            key = self._get_context_key(str(context_id))
            
            # Get context for index cleanup
            context_data = await self.get_context(context_id)
            
            # Delete context
            deleted = await self.redis.delete(key)
            
            if deleted and context_data:
                # Clean up indexes
                await self._cleanup_indexes(str(context_id), context_data.metadata)
                
                # Update stats
                await self.redis.hincrby(self.stats_key, "contexts_deleted", 1)
            
            return bool(deleted)
            
        except Exception as e:
            logger.error(f"Failed to delete context {context_id}: {e}")
            return False
    
    async def search_contexts(
        self,
        agent_id: Optional[str] = None,
        agent_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        status: Optional[ContextStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[UUID]:
        """Search contexts by criteria."""
        try:
            # Build search keys
            search_keys = []
            
            if agent_id:
                search_keys.append(self._get_index_key("agent_id", agent_id))
            if agent_type:
                search_keys.append(self._get_index_key("agent_type", agent_type))
            if status:
                search_keys.append(self._get_index_key("status", status.value))
            
            # Tag search
            if tags:
                tag_keys = [self._get_index_key("tag", tag) for tag in tags]
                search_keys.extend(tag_keys)
            
            if not search_keys:
                # Get all contexts if no search criteria
                pattern = f"{self.context_prefix}*"
                keys = await self.redis.keys(pattern)
                context_ids = [key.replace(self.context_prefix, "") for key in keys]
            else:
                # Intersect sets for AND search
                if len(search_keys) == 1:
                    context_ids = await self.redis.smembers(search_keys[0])
                else:
                    # Create temporary key for intersection
                    temp_key = f"temp:search:{uuid4()}"
                    await self.redis.sinterstore(temp_key, *search_keys)
                    context_ids = await self.redis.smembers(temp_key)
                    await self.redis.delete(temp_key)
            
            # Convert to UUIDs and apply pagination
            result_ids = []
            for i, context_id in enumerate(sorted(context_ids)):
                if i < offset:
                    continue
                if len(result_ids) >= limit:
                    break
                try:
                    result_ids.append(UUID(context_id))
                except ValueError:
                    continue
            
            return result_ids
            
        except Exception as e:
            logger.error(f"Failed to search contexts: {e}")
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            stats = await self.redis.hgetall(self.stats_key)
            
            # Count active contexts
            pattern = f"{self.context_prefix}*"
            active_count = len(await self.redis.keys(pattern))
            
            return {
                "contexts_active": active_count,
                "contexts_created": int(stats.get("contexts_created", 0)),
                "contexts_accessed": int(stats.get("contexts_accessed", 0)),
                "contexts_deleted": int(stats.get("contexts_deleted", 0)),
                "redis_memory": await self._get_redis_memory()
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
    
    async def _update_indexes(self, context_id: str, metadata: ContextMetadata):
        """Update Redis indexes for fast searching."""
        try:
            # Agent ID index
            await self.redis.sadd(self._get_index_key("agent_id", metadata.agent_id), context_id)
            
            # Agent type index
            await self.redis.sadd(self._get_index_key("agent_type", metadata.agent_type), context_id)
            
            # Status index
            await self.redis.sadd(self._get_index_key("status", metadata.status.value), context_id)
            
            # Tag indexes
            for tag in metadata.tags:
                await self.redis.sadd(self._get_index_key("tag", tag), context_id)
            
            # Session ID index
            if metadata.session_id:
                await self.redis.sadd(self._get_index_key("session", metadata.session_id), context_id)
            
            # User ID index
            if metadata.user_id:
                await self.redis.sadd(self._get_index_key("user", metadata.user_id), context_id)
                
        except Exception as e:
            logger.error(f"Failed to update indexes for {context_id}: {e}")
    
    async def _cleanup_indexes(self, context_id: str, metadata: ContextMetadata):
        """Clean up Redis indexes when deleting context."""
        try:
            # Remove from all relevant indexes
            await self.redis.srem(self._get_index_key("agent_id", metadata.agent_id), context_id)
            await self.redis.srem(self._get_index_key("agent_type", metadata.agent_type), context_id)
            await self.redis.srem(self._get_index_key("status", metadata.status.value), context_id)
            
            for tag in metadata.tags:
                await self.redis.srem(self._get_index_key("tag", tag), context_id)
            
            if metadata.session_id:
                await self.redis.srem(self._get_index_key("session", metadata.session_id), context_id)
            
            if metadata.user_id:
                await self.redis.srem(self._get_index_key("user", metadata.user_id), context_id)
                
        except Exception as e:
            logger.error(f"Failed to cleanup indexes for {context_id}: {e}")
    
    async def _get_redis_memory(self) -> Dict[str, Any]:
        """Get Redis memory usage information."""
        try:
            info = await self.redis.info("memory")
            return {
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "peak_memory": info.get("used_memory_peak", 0),
                "peak_memory_human": info.get("used_memory_peak_human", "0B")
            }
        except Exception as e:
            logger.error(f"Failed to get Redis memory info: {e}")
            return {}

# Global storage instance
storage = ContextStorage()