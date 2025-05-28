 mcp-server/extensions/example_extension.py
"""
Example MCP Extension - Context Analytics

This extension demonstrates how to create MCP extensions by tracking
context usage analytics and providing insights.
"""

import logging
from datetime import datetime
from typing import Dict, Any
from ..extensions import Extension
from ..storage import storage

logger = logging.getLogger(__name__)

class ContextAnalyticsExtension(Extension):
    """Extension that tracks context usage analytics."""
    
    def __init__(self):
        super().__init__(
            name="context_analytics",
            version="1.0.0",
            description="Tracks context usage analytics and provides insights"
        )
        
        # Analytics data
        self.analytics = {
            "contexts_created": 0,
            "contexts_accessed": 0,
            "contexts_updated": 0,
            "contexts_deleted": 0,
            "agent_usage": {},
            "popular_tags": {},
            "daily_usage": {}
        }
    
    async def initialize(self):
        """Initialize the extension."""
        logger.info("Context Analytics Extension initialized")
        
        # Register hooks
        self.register_hook("context_created", self._on_context_created)
        self.register_hook("context_updated", self._on_context_updated)
        self.register_hook("context_deleted", self._on_context_deleted)
    
    async def _on_context_created(self, context_id: str, context_data: Any):
        """Handle context creation."""
        self.analytics["contexts_created"] += 1
        
        # Track agent usage
        agent_id = context_data.metadata.agent_id
        if agent_id not in self.analytics["agent_usage"]:
            self.analytics["agent_usage"][agent_id] = {"created": 0, "updated": 0}
        self.analytics["agent_usage"][agent_id]["created"] += 1
        
        # Track tag popularity
        for tag in context_data.metadata.tags:
            if tag not in self.analytics["popular_tags"]:
                self.analytics["popular_tags"][tag] = 0
            self.analytics["popular_tags"][tag] += 1
        
        # Track daily usage
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.analytics["daily_usage"]:
            self.analytics["daily_usage"][today] = 0
        self.analytics["daily_usage"][today] += 1
        
        logger.debug(f"Tracked context creation: {context_id}")
    
    async def _on_context_updated(self, context_id: str, context_data: Any):
        """Handle context update."""
        self.analytics["contexts_updated"] += 1
        
        # Track agent updates
        agent_id = context_data.metadata.agent_id
        if agent_id in self.analytics["agent_usage"]:
            self.analytics["agent_usage"][agent_id]["updated"] += 1
        
        logger.debug(f"Tracked context update: {context_id}")
    
    async def _on_context_deleted(self, context_id: str, context_data: Any):
        """Handle context deletion."""
        self.analytics["contexts_deleted"] += 1
        
        logger.debug(f"Tracked context deletion: {context_id}")
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get analytics data."""
        return self.analytics.copy()
    
    async def get_top_agents(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top agents by usage."""
        agents = []
        for agent_id, stats in self.analytics["agent_usage"].items():
            total_activity = stats["created"] + stats["updated"]
            agents.append({
                "agent_id": agent_id,
                "contexts_created": stats["created"],
                "contexts_updated": stats["updated"],
                "total_activity": total_activity
            })
        
        return sorted(agents, key=lambda x: x["total_activity"], reverse=True)[:limit]
    
    async def get_popular_tags(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular tags."""
        tags = []
        for tag, count in self.analytics["popular_tags"].items():
            tags.append({"tag": tag, "usage_count": count})
        
        return sorted(tags, key=lambda x: x["usage_count"], reverse=True)[:limit]

async def setup_extension():
    """Setup function called by extension manager."""
    return ContextAnalyticsExtension()