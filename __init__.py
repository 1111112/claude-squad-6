"""
Claude Squad 5 - Your 5-Person Dev Team in a Box
"""

__version__ = "1.0.0"
__author__ = "Claude Squad Team"

# Export main components for easy importing
from .core.orchestrator import ParallelOrchestrator, Task, TaskStatus
from .core.context import ContextManager
from .core.events import event_bus, EventType, emit_event
from .tools.requirements.ears_generator import EARSGenerator, Requirement

__all__ = [
    "ParallelOrchestrator",
    "Task",
    "TaskStatus",
    "ContextManager",
    "event_bus",
    "EventType",
    "emit_event",
    "EARSGenerator",
    "Requirement"
]