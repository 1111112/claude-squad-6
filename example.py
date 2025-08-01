#!/usr/bin/env python3
"""
Claude Squad 5 - Example Usage
Demonstrates how to use the framework programmatically
"""
import asyncio
from claude_squad_5 import (
    ParallelOrchestrator,
    Task,
    ContextManager,
    event_bus,
    EARSGenerator
)

async def main():
    print("🚀 Claude Squad 5 - Example Feature Development")
    print("=" * 50)
    
    # Initialize components
    orchestrator = ParallelOrchestrator()
    context = ContextManager()
    
    # Set up event logging
    def log_event(event):
        print(f"📌 {event.type.value}: {event.data}")
    
    event_bus.subscribe_all(log_event)
    
    # Generate requirements for a login feature
    print("\n📋 Generating Requirements...")
    generator = EARSGenerator()
    
    # Create requirements
    req1 = generator.create_event_driven(
        system="authentication system",
        trigger="user submits login credentials",
        action="validate credentials and create session"
    )
    
    req2 = generator.create_unwanted_behavior(
        system="authentication system",
        trigger="invalid credentials submitted 3 times",
        action="lock account for 15 minutes"
    )
    
    print(f"✅ Generated {len(generator.requirements)} requirements")
    
    # Create tasks for the team
    print("\n👥 Creating Team Tasks...")
    tasks = [
        Task(
            id="req_analysis",
            role="product_owner",
            action="analyze_requirements",
            params={"requirements": [req1.to_ears(), req2.to_ears()]}
        ),
        Task(
            id="api_design",
            role="backend_dev",
            action="design_login_api",
            dependencies=["req_analysis"]
        ),
        Task(
            id="ui_design",
            role="frontend_dev",
            action="design_login_ui",
            dependencies=["req_analysis"]
        ),
        Task(
            id="test_plan",
            role="qa_engineer",
            action="create_test_plan",
            dependencies=["req_analysis"]
        ),
        Task(
            id="security_review",
            role="devops_eng",
            action="review_security",
            dependencies=["api_design"]
        )
    ]
    
    # Execute tasks
    print("\n🔄 Executing Tasks...")
    results = await orchestrator.execute_wave(tasks)
    
    # Show results
    synthesis = orchestrator.synthesize_results(results)
    
    print("\n📊 Results Summary:")
    print(f"Total tasks: {synthesis['metrics']['total_tasks']}")
    print(f"Completed: {synthesis['metrics']['completed']}")
    print(f"Failed: {synthesis['metrics']['failed']}")
    
    print("\n✅ Feature development simulation complete!")
    
    # Export requirements
    with open("example_requirements.md", "w") as f:
        f.write(generator.export_requirements())
    print("📄 Requirements exported to example_requirements.md")

if __name__ == "__main__":
    asyncio.run(main())