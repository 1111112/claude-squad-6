"""
Claude Squad 5 - Event-Driven Observability
Lightweight event system for tracking all team activities
"""
import json
import asyncio
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import logging

class EventType(Enum):
    # Task lifecycle
    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    
    # Wave execution
    WAVE_STARTED = "wave.started"
    WAVE_COMPLETED = "wave.completed"
    
    # Team coordination
    HANDOFF_INITIATED = "handoff.initiated"
    REVIEW_REQUESTED = "review.requested"
    APPROVAL_GIVEN = "approval.given"
    
    # Quality gates
    GATE_PASSED = "gate.passed"
    GATE_FAILED = "gate.failed"
    
    # System health
    TOKEN_USAGE_HIGH = "system.token_usage_high"
    CONTEXT_COMPRESSED = "system.context_compressed"

@dataclass
class Event:
    id: str
    type: EventType
    timestamp: datetime
    source: str  # Which component emitted
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    
    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "data": self.data,
            "metadata": self.metadata or {}
        })

class EventBus:
    """Central event bus for all team coordination"""
    
    def __init__(self):
        self.handlers: Dict[EventType, List[Callable]] = {}
        self.event_log: List[Event] = []
        self.metrics = EventMetrics()
        
        # Setup default logging handler
        self.subscribe(EventType.TASK_FAILED, self._log_failure)
        self.subscribe(EventType.GATE_FAILED, self._log_gate_failure)
        
    def subscribe(self, event_type: EventType, handler: Callable) -> None:
        """Subscribe to specific event type"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        
    def subscribe_all(self, handler: Callable) -> None:
        """Subscribe to all events"""
        for event_type in EventType:
            self.subscribe(event_type, handler)
            
    async def emit(self, event: Event) -> None:
        """Emit an event to all subscribers"""
        # Log event
        self.event_log.append(event)
        self.metrics.record(event)
        
        # Notify subscribers
        handlers = self.handlers.get(event.type, [])
        
        # Execute handlers concurrently
        if handlers:
            await asyncio.gather(
                *[self._safe_handle(handler, event) for handler in handlers],
                return_exceptions=True
            )
            
    async def _safe_handle(self, handler: Callable, event: Event) -> None:
        """Safely execute handler with error catching"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            logging.error(f"Handler {handler.__name__} failed for {event.type}: {e}")
            
    def _log_failure(self, event: Event) -> None:
        """Default handler for task failures"""
        logging.error(f"Task failed: {event.data.get('task_id')} - {event.data.get('error')}")
        
    def _log_gate_failure(self, event: Event) -> None:
        """Default handler for gate failures"""
        logging.warning(f"Quality gate failed: {event.data.get('gate')} - {event.data.get('reason')}")
        
    def get_events_by_type(self, event_type: EventType, limit: int = 100) -> List[Event]:
        """Get recent events of specific type"""
        return [e for e in self.event_log if e.type == event_type][-limit:]
        
    def get_events_by_source(self, source: str, limit: int = 100) -> List[Event]:
        """Get recent events from specific source"""
        return [e for e in self.event_log if e.source == source][-limit:]
        
    def export_metrics(self) -> Dict[str, Any]:
        """Export current metrics"""
        return self.metrics.export()

class EventMetrics:
    """Track metrics from events"""
    
    def __init__(self):
        self.counts: Dict[str, int] = {}
        self.durations: Dict[str, List[float]] = {}
        self.errors: List[Dict[str, Any]] = []
        
    def record(self, event: Event) -> None:
        """Record metrics from event"""
        # Count events
        self.counts[event.type.value] = self.counts.get(event.type.value, 0) + 1
        
        # Track durations for completed tasks
        if event.type == EventType.TASK_COMPLETED:
            duration = event.data.get("duration_seconds")
            if duration:
                task_type = event.data.get("task_type", "unknown")
                if task_type not in self.durations:
                    self.durations[task_type] = []
                self.durations[task_type].append(duration)
                
        # Track errors
        if event.type in [EventType.TASK_FAILED, EventType.GATE_FAILED]:
            self.errors.append({
                "timestamp": event.timestamp,
                "type": event.type.value,
                "error": event.data.get("error", "Unknown error")
            })
            
    def export(self) -> Dict[str, Any]:
        """Export metrics summary"""
        return {
            "event_counts": self.counts,
            "average_durations": {
                task: sum(times) / len(times) if times else 0
                for task, times in self.durations.items()
            },
            "error_rate": len(self.errors) / sum(self.counts.values()) if self.counts else 0,
            "recent_errors": self.errors[-10:]  # Last 10 errors
        }

class EventLogger:
    """Structured logging for events"""
    
    def __init__(self, log_file: str = "claude_squad.log"):
        self.logger = logging.getLogger("claude_squad")
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
    def log_event(self, event: Event) -> None:
        """Log event in structured format"""
        self.logger.info(event.to_json())

# Global event bus instance
event_bus = EventBus()

# Helper function for easy event emission
async def emit_event(
    event_type: EventType,
    source: str,
    data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """Convenience function to emit events"""
    import uuid
    event = Event(
        id=str(uuid.uuid4()),
        type=event_type,
        timestamp=datetime.now(),
        source=source,
        data=data,
        metadata=metadata
    )
    await event_bus.emit(event)