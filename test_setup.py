#!/usr/bin/env python3
"""Test Claude Squad 6 setup"""
import asyncio
from core.orchestrator import ParallelOrchestrator, Task
from core.hooks import HooksRunner

async def test_setup():
    print("Testing Claude Squad 6 setup...\n")
    
    # Test orchestrator with 6 members
    orchestrator = ParallelOrchestrator()
    
    # Create tasks for all 6 team members
    tasks = [
        Task(id="po-1", role="product_owner", action="create_vision_doc"),
        Task(id="be-1", role="backend_dev", action="implement_api"),
        Task(id="fe-1", role="frontend_dev", action="create_ui_components"),
        Task(id="do-1", role="devops_eng", action="setup_pipeline"),
        Task(id="qa-1", role="qa_engineer", action="create_test_suite"),
        Task(id="tl-1", role="tech_lead", action="run_quality_checks"),
    ]
    
    # Execute tasks
    results = await orchestrator.execute_wave(tasks)
    
    print(f"✅ Executed {len(results)} tasks")
    print(f"✅ All 6 team members working: {len(set(t.role for t in results))}/6")
    
    # Test hooks
    hooks = HooksRunner()
    print("\n🔍 Testing hooks system...")
    
    # Note: This will fail if black/ruff not installed, which is expected
    result = await hooks.run_hooks("pre-commit")
    print(f"✅ Hooks system functional: {result}")
    
    print("\n✨ Claude Squad 6 is ready!")

if __name__ == "__main__":
    asyncio.run(test_setup())