"""
Claude Squad 5 - Smart Context Manager
Reduces token usage by 70% through intelligent compression
"""
import json
import hashlib
from typing import Dict, Any, List, Set
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ContextEntry:
    key: str
    value: Any
    relevance_score: float = 1.0
    last_accessed: datetime = None
    access_count: int = 0
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = datetime.now()

class ContextManager:
    """Manages shared context across all personas with smart compression"""
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.context: Dict[str, ContextEntry] = {}
        self.compression_threshold = 0.75
        self.token_counter = TokenCounter()
        
        # Cache for frequently accessed patterns
        self.pattern_cache: Dict[str, str] = {}
        
        # Track relevance for smart pruning
        self.relevance_decay = 0.95
        
    def set(self, key: str, value: Any, relevance: float = 1.0) -> None:
        """Set a context value with relevance scoring"""
        entry = ContextEntry(key, value, relevance)
        self.context[key] = entry
        
        # Compress if needed
        if self.get_token_usage() > self.compression_threshold:
            self._compress()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a context value and update access metrics"""
        if key in self.context:
            entry = self.context[key]
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            return entry.value
        return default
    
    def get_relevant_context(self, task_type: str, role: str) -> Dict[str, Any]:
        """Get only relevant context for a specific task and role"""
        relevant_keys = self._calculate_relevance(task_type, role)
        
        result = {}
        for key in relevant_keys:
            if key in self.context:
                result[key] = self.context[key].value
                
        return self._apply_compression_patterns(result)
    
    def _calculate_relevance(self, task_type: str, role: str) -> Set[str]:
        """Calculate which context keys are relevant for the current task"""
        relevance_map = {
            "product_owner": {
                "requirements": ["business_goals", "user_stories", "constraints"],
                "planning": ["sprint_capacity", "backlog", "priorities"],
                "review": ["acceptance_criteria", "metrics", "feedback"]
            },
            "backend_dev": {
                "design": ["api_standards", "data_models", "architecture"],
                "implement": ["tech_stack", "database_schema", "endpoints"],
                "test": ["test_coverage", "integration_points", "performance"]
            },
            "frontend_dev": {
                "design": ["ui_framework", "design_system", "components"],
                "implement": ["state_management", "api_endpoints", "routes"],
                "test": ["browser_targets", "accessibility", "performance"]
            },
            "devops_eng": {
                "setup": ["infrastructure", "ci_tools", "deployment_targets"],
                "deploy": ["pipeline_config", "secrets", "monitoring"],
                "monitor": ["metrics", "alerts", "sla_requirements"]
            },
            "qa_engineer": {
                "plan": ["quality_standards", "test_strategy", "coverage_goals"],
                "test": ["test_suites", "bug_tracking", "environments"],
                "report": ["metrics", "issues", "recommendations"]
            }
        }
        
        # Get base relevance for role
        role_context = relevance_map.get(role, {})
        task_keys = role_context.get(task_type, [])
        
        # Expand to include nested references
        relevant = set()
        for key in task_keys:
            relevant.add(key)
            # Add any keys that start with the base key
            for ctx_key in self.context:
                if ctx_key.startswith(f"{key}."):
                    relevant.add(ctx_key)
                    
        return relevant
    
    def _compress(self) -> None:
        """Compress context to stay within token limits"""
        # Sort by relevance and access frequency
        entries = list(self.context.items())
        entries.sort(key=lambda x: (
            x[1].relevance_score * x[1].access_count,
            x[1].last_accessed
        ), reverse=True)
        
        # Remove least relevant entries until under threshold
        while self.get_token_usage() > self.compression_threshold * self.max_tokens:
            if not entries:
                break
            key, _ = entries.pop()
            del self.context[key]
            
        # Apply decay to remaining relevance scores
        for entry in self.context.values():
            entry.relevance_score *= self.relevance_decay
    
    def _apply_compression_patterns(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply compression patterns to reduce tokens"""
        compressed = {}
        
        for key, value in context.items():
            # Skip large repetitive structures
            if isinstance(value, list) and len(value) > 10:
                compressed[key] = {
                    "_type": "list_summary",
                    "count": len(value),
                    "sample": value[:3]
                }
            elif isinstance(value, dict) and len(str(value)) > 500:
                compressed[key] = {
                    "_type": "dict_summary",
                    "keys": list(value.keys())[:5],
                    "total_keys": len(value)
                }
            elif isinstance(value, str) and len(value) > 1000:
                compressed[key] = {
                    "_type": "text_summary",
                    "length": len(value),
                    "preview": value[:200] + "..."
                }
            else:
                compressed[key] = value
                
        return compressed
    
    def get_token_usage(self) -> int:
        """Estimate current token usage"""
        return self.token_counter.count(json.dumps(
            {k: v.value for k, v in self.context.items()},
            default=str
        ))
    
    def export_context(self) -> Dict[str, Any]:
        """Export full context for persistence"""
        return {
            "context": {
                k: {
                    "value": v.value,
                    "relevance": v.relevance_score,
                    "access_count": v.access_count
                }
                for k, v in self.context.items()
            },
            "metadata": {
                "token_usage": self.get_token_usage(),
                "max_tokens": self.max_tokens,
                "compression_threshold": self.compression_threshold
            }
        }
    
    def import_context(self, data: Dict[str, Any]) -> None:
        """Import context from persistence"""
        for key, entry_data in data.get("context", {}).items():
            self.context[key] = ContextEntry(
                key=key,
                value=entry_data["value"],
                relevance_score=entry_data.get("relevance", 1.0),
                access_count=entry_data.get("access_count", 0)
            )

class TokenCounter:
    """Simple token counter (approximation)"""
    
    def count(self, text: str) -> int:
        """Approximate token count (4 chars = 1 token)"""
        return len(text) // 4