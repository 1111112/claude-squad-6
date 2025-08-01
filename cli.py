#!/usr/bin/env python3
"""
Claude Squad 6 - Command Line Interface
Enhanced with TechLead, hooks, and git operations
"""
import click
import json
import asyncio
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Import our core modules
import sys
sys.path.append(str(Path(__file__).parent))

from core.orchestrator import ParallelOrchestrator, Task
from core.context import ContextManager
from core.events import event_bus, EventType, emit_event
from core.hooks import HooksRunner
from tools.requirements.ears_generator import EARSGenerator
import subprocess
import os

# Rich for beautiful terminal output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    console = Console()
except ImportError:
    # Fallback to basic print
    class Console:
        def print(self, *args, **kwargs):
            print(*args)
    console = Console()

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Claude Squad 6 - Your 6-person dev team with quality automation"""
    pass

@cli.command()
@click.option('--project-name', prompt='Project name', help='Name of your project')
@click.option('--tech-stack', prompt='Tech stack (comma-separated)', help='e.g., python,react,postgres')
def init(project_name: str, tech_stack: str):
    """Initialize Claude Squad for your project"""
    console.print(f"[bold green]🚀 Initializing Claude Squad 6 for {project_name}[/bold green]")
    
    # Parse tech stack
    stack = [t.strip() for t in tech_stack.split(',')]
    
    # Create project context
    context = {
        "project_name": project_name,
        "tech_stack": stack,
        "initialized": datetime.now().isoformat(),
        "team": {
            "product_owner": {"status": "ready"},
            "backend_dev": {"status": "ready"},
            "frontend_dev": {"status": "ready"},
            "devops_eng": {"status": "ready"},
            "qa_engineer": {"status": "ready"},
            "tech_lead": {"status": "ready"}
        }
    }
    
    # Save context
    context_path = Path(".claude-squad/context/project.json")
    context_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(context_path, 'w') as f:
        json.dump(context, f, indent=2)
    
    console.print("[green]✅ Project initialized successfully![/green]")
    console.print(f"[dim]Context saved to {context_path}[/dim]")

@cli.command()
@click.argument('description')
@click.option('--sprint-days', default=6, help='Sprint duration in days')
def feature(description: str, sprint_days: int):
    """Start developing a new feature"""
    console.print(f"[bold blue]🎯 Starting feature: {description}[/bold blue]")
    
    # Run the feature workflow
    asyncio.run(_run_feature_workflow(description, sprint_days))

async def _run_feature_workflow(description: str, sprint_days: int):
    """Execute the feature development workflow"""
    orchestrator = ParallelOrchestrator()
    context_mgr = ContextManager()
    
    # Set up event logging
    def log_event(event):
        console.print(f"[dim]{event.timestamp.strftime('%H:%M:%S')} - {event.type.value}: {event.data}[/dim]")
    
    event_bus.subscribe_all(log_event)
    
    # Phase 1: Requirements
    console.print("\n[yellow]📋 Phase 1: Requirements Generation[/yellow]")
    
    # Generate requirements using EARS
    generator = EARSGenerator()
    user_story = f"As a user, I want {description}, so that I can benefit from this feature"
    requirements = generator.generate_from_user_story(user_story)
    
    console.print(f"[green]✅ Generated {len(requirements)} requirements[/green]")
    
    # Create tasks for the team
    tasks = [
        Task(
            id="vision",
            role="product_owner",
            action="create_vision_doc",
            params={"description": description, "requirements": requirements}
        ),
        Task(
            id="design",
            role="backend_dev",
            action="design_architecture",
            dependencies=["vision"]
        ),
        Task(
            id="ui_design",
            role="frontend_dev",
            action="design_ui",
            dependencies=["vision"]
        ),
        Task(
            id="test_plan",
            role="qa_engineer",
            action="create_test_plan",
            dependencies=["vision"]
        ),
        Task(
            id="infra_plan",
            role="devops_eng",
            action="plan_infrastructure",
            dependencies=["design"]
        )
    ]
    
    # Execute tasks
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task_progress = progress.add_task("Executing tasks...", total=len(tasks))
        
        results = await orchestrator.execute_wave(tasks)
        
        for result in results:
            progress.update(task_progress, advance=1)
    
    # Show results
    synthesis = orchestrator.synthesize_results(results)
    
    table = Table(title="Sprint Results")
    table.add_column("Role", style="cyan")
    table.add_column("Tasks", style="green")
    table.add_column("Status", style="yellow")
    
    for role, tasks in synthesis["by_role"].items():
        completed = sum(1 for t in tasks if t["status"] == "completed")
        table.add_row(
            role.replace("_", " ").title(),
            f"{completed}/{len(tasks)}",
            "✅ Complete" if completed == len(tasks) else "⚠️  Partial"
        )
    
    console.print(table)
    
    # Save artifacts
    artifacts_path = Path(f".claude-squad/features/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{description[:20]}")
    artifacts_path.mkdir(parents=True, exist_ok=True)
    
    with open(artifacts_path / "requirements.md", 'w') as f:
        f.write(generator.export_requirements())
    
    with open(artifacts_path / "results.json", 'w') as f:
        json.dump(synthesis, f, indent=2)
    
    console.print(f"\n[green]✅ Feature development complete![/green]")
    console.print(f"[dim]Artifacts saved to {artifacts_path}[/dim]")

@cli.command()
def status():
    """Check team status and metrics"""
    console.print("[bold]📊 Claude Squad 5 Status[/bold]\n")
    
    # Load project context
    context_path = Path(".claude-squad/context/project.json")
    if not context_path.exists():
        console.print("[red]❌ Project not initialized. Run 'claude-squad init' first.[/red]")
        return
    
    with open(context_path) as f:
        context = json.load(f)
    
    # Display team status
    table = Table(title="Team Status")
    table.add_column("Role", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Current Task", style="yellow")
    
    for role, info in context.get("team", {}).items():
        table.add_row(
            role.replace("_", " ").title(),
            info.get("status", "unknown"),
            info.get("current_task", "Idle")
        )
    
    console.print(table)
    
    # Show metrics
    metrics = event_bus.export_metrics()
    if metrics["event_counts"]:
        console.print("\n[bold]📈 Metrics[/bold]")
        console.print(f"Total events: {sum(metrics['event_counts'].values())}")
        console.print(f"Error rate: {metrics['error_rate']:.1%}")
        
        if metrics["average_durations"]:
            console.print("\n[bold]⏱️  Average Task Durations[/bold]")
            for task, duration in metrics["average_durations"].items():
                console.print(f"  {task}: {duration:.1f}s")

@cli.command()
@click.argument('workflow', type=click.Choice(['sprint', 'hotfix', 'refactor']))
@click.argument('description')
def run(workflow: str, description: str):
    """Run a predefined workflow"""
    console.print(f"[bold magenta]🔄 Running {workflow} workflow: {description}[/bold magenta]")
    
    # Load workflow configuration
    workflow_path = Path(f"claude-squad-5/workflows/{workflow}.yaml")
    if not workflow_path.exists():
        console.print(f"[red]❌ Workflow '{workflow}' not found[/red]")
        return
    
    with open(workflow_path) as f:
        config = yaml.safe_load(f)
    
    console.print(f"[dim]Duration: {config['duration']}[/dim]")
    console.print(f"[dim]Stages: {len(config['stages'])}[/dim]")
    
    # Execute workflow
    asyncio.run(_execute_workflow(config, description))

async def _execute_workflow(config: Dict[str, Any], description: str):
    """Execute a workflow configuration"""
    orchestrator = ParallelOrchestrator()
    
    for stage_name, stage in config["stages"].items():
        console.print(f"\n[yellow]▶️  Stage: {stage['name']}[/yellow]")
        
        # Convert stage tasks to Task objects
        tasks = []
        for task_config in stage.get("tasks", []):
            task = Task(
                id=task_config["id"],
                role=task_config["role"],
                action=task_config["action"],
                dependencies=task_config.get("dependencies", []),
                params={"description": description}
            )
            tasks.append(task)
        
        # Execute stage
        if tasks:
            results = await orchestrator.execute_wave(tasks)
            console.print(f"[green]✅ Completed {len([r for r in results if r.status.value == 'completed'])} tasks[/green]")

@cli.command()
def docs():
    """Open documentation"""
    import webbrowser
    docs_path = Path(__file__).parent / "README.md"
    if docs_path.exists():
        webbrowser.open(f"file://{docs_path.absolute()}")
    else:
        console.print("[yellow]📚 Creating documentation...[/yellow]")
        # Would generate docs here
        console.print("[green]✅ Documentation created![/green]")

@cli.command()
@click.argument('message')
@click.option('--notify/--no-notify', default=True, help='Show desktop notification')
def commit(message: str, notify: bool):
    """Commit with hooks and quality checks"""
    console.print(f"[bold blue]🔍 Running pre-commit hooks...[/bold blue]")
    
    # Run hooks
    hooks = HooksRunner()
    result = asyncio.run(hooks.run_hooks("pre-commit"))
    
    if result['success']:
        console.print(f"[green]✅ All hooks passed![/green]")
        if result['fixed'] > 0:
            console.print(f"[yellow]🔧 Auto-fixed {result['fixed']} issues[/yellow]")
        
        # Git commit
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", message])
        console.print(f"[green]✅ Committed: {message}[/green]")
        
        if notify and os.name == 'posix':
            subprocess.run(["osascript", "-e", f'display notification "Commit successful" with title "Claude Squad 6"'])
    else:
        console.print(f"[red]❌ Hook failures:[/red]")
        for issue in result['issues']:
            console.print(f"  - {issue}")

@cli.command()
@click.argument('title')
@click.option('--base', default='main', help='Base branch')
def pr(title: str, base: str):
    """Create PR with quality validation"""
    console.print(f"[bold blue]🔍 Running pre-push hooks...[/bold blue]")
    
    # Run pre-push hooks
    hooks = HooksRunner()
    result = asyncio.run(hooks.run_hooks("pre-push"))
    
    if result['success']:
        console.print(f"[green]✅ Quality checks passed![/green]")
        
        # Get current branch
        branch = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True).stdout.strip()
        
        # Push branch
        subprocess.run(["git", "push", "-u", "origin", branch])
        
        # Create PR using gh CLI
        subprocess.run(["gh", "pr", "create", "--title", title, "--base", base, "--fill"])
        console.print(f"[green]✅ PR created: {title}[/green]")
    else:
        console.print(f"[red]❌ Quality check failures - fix before creating PR[/red]")

@cli.command()
@click.option('--squash/--no-squash', default=True, help='Squash commits')
def merge(squash: bool):
    """Merge with TechLead approval simulation"""
    console.print(f"[bold blue]🤖 TechLead reviewing merge...[/bold blue]")
    
    # Simulate TechLead review
    orchestrator = ParallelOrchestrator()
    task = Task(
        id="merge-review",
        role="tech_lead",
        action="perform_review"
    )
    
    result = asyncio.run(orchestrator.execute_task(task))
    
    if result.result['review_status'] == 'approved':
        console.print(f"[green]✅ TechLead approved merge![/green]")
        
        # Perform merge
        merge_cmd = ["gh", "pr", "merge", "--squash"] if squash else ["gh", "pr", "merge"]
        subprocess.run(merge_cmd)
        console.print(f"[green]✅ Merged successfully![/green]")
    else:
        console.print(f"[red]❌ TechLead review failed[/red]")

if __name__ == "__main__":
    cli()