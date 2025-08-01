"""
Claude Squad 6 - Parallel Orchestrator with TechLead
Enhanced with 6-person team support and hooks integration
"""
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    id: str
    role: str
    action: str
    dependencies: List[str] = None
    params: Dict[str, Any] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.params is None:
            self.params = {}

class ParallelOrchestrator:
    """Orchestrates parallel execution of tasks across 6-person team"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.event_handlers = []
        self.hooks_runner = None  # Will be set by CLI
        
    def add_task(self, task: Task) -> None:
        """Add a task to the execution queue"""
        self.tasks[task.id] = task
        self._emit_event("task.added", task)
        
    def calculate_waves(self, tasks: List[Task]) -> List[List[Task]]:
        """Group tasks into waves based on dependencies"""
        waves = []
        completed_ids = set()
        remaining_tasks = tasks.copy()
        
        while remaining_tasks:
            wave = []
            for task in remaining_tasks:
                # Task can run if all dependencies are completed
                if all(dep in completed_ids for dep in task.dependencies):
                    wave.append(task)
            
            if not wave:
                # Circular dependency or impossible state
                raise ValueError("Circular dependency detected")
                
            waves.append(wave)
            completed_ids.update(task.id for task in wave)
            remaining_tasks = [t for t in remaining_tasks if t not in wave]
            
        return waves
    
    async def execute_task(self, task: Task) -> Task:
        """Execute a single task"""
        task.status = TaskStatus.RUNNING
        self._emit_event("task.started", task)
        
        try:
            # Run pre-task hooks if TechLead task
            if task.role == "tech_lead" and self.hooks_runner:
                hook_result = await self.hooks_runner.run_hooks(task.action)
                if not hook_result['success']:
                    task.error = f"Hook failed: {hook_result['error']}"
                    task.status = TaskStatus.FAILED
                    return task
            
            # Simulate task execution (in real impl, would call Claude API)
            await asyncio.sleep(0.1)  # Placeholder
            
            # Task-specific logic based on role and action
            result = await self._execute_by_role(task)
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            self._emit_event("task.completed", task)
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            self._emit_event("task.failed", task, error=str(e))
            
        return task
    
    async def _execute_by_role(self, task: Task) -> Any:
        """Execute task based on role (simplified for demo)"""
        role_handlers = {
            "product_owner": self._handle_product_owner,
            "backend_dev": self._handle_backend_dev,
            "frontend_dev": self._handle_frontend_dev,
            "devops_eng": self._handle_devops,
            "qa_engineer": self._handle_qa,
            "tech_lead": self._handle_tech_lead  # NEW
        }
        
        handler = role_handlers.get(task.role)
        if handler:
            return await handler(task)
        else:
            raise ValueError(f"Unknown role: {task.role}")
    
    async def _handle_product_owner(self, task: Task) -> Dict:
        """Product owner task handler"""
        return {
            "vision": "Feature vision document",
            "acceptance_criteria": ["AC1", "AC2", "AC3"],
            "success_metrics": {"metric1": "value1"}
        }
    
    async def _handle_backend_dev(self, task: Task) -> Dict:
        """Backend developer task handler"""
        return {
            "api_endpoints": ["/api/v1/feature"],
            "data_models": ["Model1", "Model2"],
            "tests_written": 15
        }
    
    async def _handle_frontend_dev(self, task: Task) -> Dict:
        """Frontend developer task handler"""
        return {
            "components": ["Component1", "Component2"],
            "ui_tests": 10,
            "accessibility_score": 98
        }
    
    async def _handle_devops(self, task: Task) -> Dict:
        """DevOps engineer task handler"""
        return {
            "deployment_ready": True,
            "ci_pipeline": "configured",
            "monitoring": "enabled"
        }
    
    async def _handle_qa(self, task: Task) -> Dict:
        """QA engineer task handler"""
        return {
            "test_coverage": 85,
            "bugs_found": 3,
            "performance_baseline": "established"
        }
    
    async def _handle_tech_lead(self, task: Task) -> Dict:
        """Tech lead task handler - quality enforcement"""
        action_handlers = {
            "run_quality_checks": self._run_quality_checks,
            "perform_review": self._perform_code_review,
            "execute_hooks": self._execute_hooks
        }
        
        handler = action_handlers.get(task.action, self._default_tech_lead_action)
        return await handler(task)
    
    async def _run_quality_checks(self, task: Task) -> Dict:
        """Run quality checks via hooks"""
        if self.hooks_runner:
            result = await self.hooks_runner.run_hooks("pre-push")
            return {
                "quality_passed": result['success'],
                "issues_found": result.get('issues', []),
                "auto_fixed": result.get('fixed', 0)
            }
        return {"quality_passed": True, "message": "No hooks configured"}
    
    async def _perform_code_review(self, task: Task) -> Dict:
        """Perform automated code review"""
        return {
            "review_status": "approved",
            "suggestions": ["Consider using type hints", "Add docstrings"],
            "security_check": "passed"
        }
    
    async def _execute_hooks(self, task: Task) -> Dict:
        """Execute hooks based on task params"""
        hook_type = task.params.get('hook_type', 'pre-commit')
        if self.hooks_runner:
            result = await self.hooks_runner.run_hooks(hook_type)
            return result
        return {"success": True, "message": "No hooks configured"}
    
    async def _default_tech_lead_action(self, task: Task) -> Dict:
        """Default tech lead action"""
        return {
            "action": task.action,
            "status": "completed",
            "quality_score": 95
        }
    
    async def execute_wave(self, tasks: List[Task]) -> List[Task]:
        """Execute all tasks in a wave in parallel"""
        waves = self.calculate_waves(tasks)
        all_results = []
        
        for i, wave in enumerate(waves):
            self._emit_event("wave.started", wave_number=i+1, tasks=len(wave))
            
            # Execute all tasks in this wave in parallel
            wave_results = await asyncio.gather(
                *[self.execute_task(task) for task in wave],
                return_exceptions=True
            )
            
            all_results.extend(wave_results)
            self._emit_event("wave.completed", wave_number=i+1)
            
        return all_results
    
    def synthesize_results(self, results: List[Task]) -> Dict[str, Any]:
        """Synthesize results from all tasks"""
        synthesis = {
            "summary": {},
            "by_role": {},
            "metrics": {
                "total_tasks": len(results),
                "completed": sum(1 for r in results if r.status == TaskStatus.COMPLETED),
                "failed": sum(1 for r in results if r.status == TaskStatus.FAILED)
            }
        }
        
        for task in results:
            role = task.role
            if role not in synthesis["by_role"]:
                synthesis["by_role"][role] = []
            synthesis["by_role"][role].append({
                "action": task.action,
                "status": task.status.value,
                "result": task.result
            })
        
        return synthesis
    
    def _emit_event(self, event_type: str, *args, **kwargs):
        """Emit an event for observability"""
        event = {
            "type": event_type,
            "data": {"args": args, "kwargs": kwargs}
        }
        for handler in self.event_handlers:
            handler(event)
    
    def on_event(self, handler):
        """Register an event handler"""
        self.event_handlers.append(handler)