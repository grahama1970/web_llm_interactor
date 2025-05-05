#!/usr/bin/env python3
"""
Perplexity Stealth Agent CLI

A Python CLI wrapper for the Perplexity Stealth Automation JavaScript project.
Designed for AI agents to interact with Perplexity.ai through a structured interface.
"""

import os
import sys
import json
import subprocess
from typing import List, Optional, Dict, Any
from pathlib import Path
from enum import Enum

import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from pydantic import BaseModel, Field
from loguru import logger
from dotenv import load_dotenv

# Set up app and console
app = typer.Typer(
    name="perplexity-agent",
    help="CLI for AI agents to interact with Perplexity.ai stealth automation",
    add_completion=False,
)
console = Console()

# Load environment variables
load_dotenv()

# Get project root directory (parent of python_cli)
PROJECT_ROOT = Path(__file__).parent.parent.absolute()


class ProxyType(str, Enum):
    """Types of proxies supported by the system"""
    NONE = "none"
    CUSTOM = "custom"
    BRIGHTDATA = "brightdata"


class TaskList(BaseModel):
    """Task list structure for agent processing"""
    tasks: List[Dict[str, Any]] = Field(default_factory=list)
    title: Optional[str] = None
    description: Optional[str] = None


def run_js_command(cmd: List[str], show_output: bool = True) -> subprocess.CompletedProcess:
    """Run a JavaScript command with proper output handling"""
    logger.debug(f"Running command: {' '.join(cmd)}")
    
    try:
        # Change directory to project root before running command
        process = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=not show_output,
            text=True,
            check=True,
        )
        return process
    except subprocess.CalledProcessError as e:
        if not show_output:
            console.print(f"[bold red]Error running command:[/] {' '.join(cmd)}")
            console.print(e.stderr)
        raise typer.Exit(code=1)


def display_banner():
    """Display the CLI banner"""
    console.print(Panel.fit(
        "[bold cyan]Perplexity Stealth Agent CLI[/]",
        subtitle="[bold]v1.0.0[/]",
        border_style="cyan",
    ))


@app.command("query")
def query(
    prompt: str = typer.Argument(..., help="Prompt to send to Perplexity.ai"),
    headless: bool = typer.Option(False, "--headless", "-h", help="Run in headless mode"),
    proxy: ProxyType = typer.Option(ProxyType.NONE, "--proxy", "-p", help="Proxy type to use"),
    wait_time: int = typer.Option(60000, "--wait-time", "-w", help="Response wait time in ms"),
    output_dir: Optional[str] = typer.Option(None, "--output-dir", "-o", help="Directory to save responses"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
):
    """
    Send a single query to Perplexity.ai and capture the response
    """
    display_banner()
    
    # Prepare command arguments
    cmd = ["node", "run.js"]
    
    # Add command-line options
    if headless:
        cmd.append("--headless")
    
    if proxy != ProxyType.NONE:
        cmd.append(f"--proxy={proxy.value}")
    
    if output_dir:
        cmd.append(f"--output-dir={output_dir}")
    
    if debug:
        cmd.append("--log-level=DEBUG")
    
    cmd.append(f"--timeout={wait_time}")
    cmd.append(f"--prompt={prompt}")
    
    # Display progress spinner while running command
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Querying Perplexity.ai...[/]"),
        transient=True,
    ) as progress:
        progress.add_task("query", total=None)
        result = run_js_command(cmd, show_output=True)
    
    # Note: The actual response output is already displayed by the JavaScript code
    
    logger.info(f"Query completed with exit code: {result.returncode}")
    return result.returncode


@app.command("tasks")
def execute_tasks(
    tasks_file: Path = typer.Argument(..., help="JSON file containing tasks to execute"),
    headless: bool = typer.Option(True, "--headless/--no-headless", help="Run in headless mode"),
    proxy: ProxyType = typer.Option(ProxyType.NONE, "--proxy", "-p", help="Proxy type to use"),
    output_dir: str = typer.Option("./responses", "--output-dir", "-o", help="Directory to save responses"),
):
    """
    Execute a list of tasks defined in a JSON file
    """
    display_banner()
    
    # Load tasks file
    try:
        with open(tasks_file, "r") as f:
            task_data = json.load(f)
            tasks = TaskList(**task_data)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        console.print(f"[bold red]Error loading tasks file:[/] {e}")
        raise typer.Exit(code=1)
    
    if tasks.title:
        console.print(f"[bold]Executing task list:[/] {tasks.title}")
    
    if tasks.description:
        console.print(f"[italic]{tasks.description}[/]")
    
    console.print(f"[bold]Found {len(tasks.tasks)} tasks to execute[/]")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Execute each task
    for i, task in enumerate(tasks.tasks):
        prompt = task.get("prompt")
        if not prompt:
            console.print(f"[yellow]Skipping task {i+1} - No prompt specified[/]")
            continue
            
        task_output_dir = os.path.join(output_dir, f"task_{i+1}")
        os.makedirs(task_output_dir, exist_ok=True)
        
        console.print(f"[bold green]Task {i+1}/{len(tasks.tasks)}:[/] {task.get('title', prompt[:50] + '...')}")
        
        # Prepare command arguments
        cmd = ["node", "run.js"]
        
        # Add command-line options
        if headless:
            cmd.append("--headless")
        
        if proxy != ProxyType.NONE:
            cmd.append(f"--proxy={proxy.value}")
            
        wait_time = task.get("wait_time", 60000)
        cmd.append(f"--timeout={wait_time}")
        
        cmd.append(f"--output-dir={task_output_dir}")
        cmd.append(f"--prompt={prompt}")
        
        # Display progress spinner while running command
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[bold green]Executing task {i+1}/{len(tasks.tasks)}...[/]"),
            transient=True,
        ) as progress:
            progress.add_task("query", total=None)
            result = run_js_command(cmd, show_output=True)
        
        # Save task status
        with open(os.path.join(task_output_dir, "task_info.json"), "w") as f:
            task_info = {
                "task_id": i+1,
                "title": task.get("title"),
                "prompt": prompt,
                "exit_code": result.returncode,
                "status": "completed" if result.returncode == 0 else "failed"
            }
            json.dump(task_info, f, indent=2)
        
        console.print(f"[bold]Task {i+1} completed with exit code {result.returncode}[/]")
    
    console.print(f"\n[bold green]All tasks completed. Responses saved to: {output_dir}[/]")


@app.command("security")
def security_check(
    full: bool = typer.Option(False, "--full", help="Run a full security assessment"),
    code_only: bool = typer.Option(False, "--code-only", help="Only analyze code for security issues"),
    deps_only: bool = typer.Option(False, "--deps-only", help="Only check dependencies for vulnerabilities"),
    output: str = typer.Option("./security-report.md", "--output", "-o", help="Path to save the security report"),
):
    """
    Run a security assessment on the codebase
    """
    display_banner()
    
    console.print("[bold]Running security assessment...[/]")
    
    # Prepare command
    cmd = ["node", "security-eval.js"]
    
    if full:
        cmd.append("--full")
    elif code_only:
        cmd.append("--analyze-code")
    elif deps_only:
        cmd.append("--check-deps")
    else:
        # Default to full if no specific option is provided
        cmd.append("--full")
    
    cmd.append(f"--output={output}")
    cmd.append("--yes")  # Skip confirmation prompt
    
    # Run security evaluation
    run_js_command(cmd, show_output=True)
    
    # Check if the report was generated
    if os.path.exists(os.path.join(PROJECT_ROOT, output)):
        console.print(f"[bold green]Security report generated:[/] {output}")
    else:
        console.print("[bold red]Failed to generate security report[/]")


@app.command("create-tasks")
def create_tasks_file(
    output: str = typer.Argument("./tasks.json", help="Output file path"),
):
    """
    Create a template task list file
    """
    display_banner()
    
    template = {
        "title": "Example Task List",
        "description": "A list of tasks to execute on Perplexity.ai",
        "tasks": [
            {
                "title": "Basic Query",
                "prompt": "What is the capital of France?",
                "wait_time": 60000
            },
            {
                "title": "Desktop Commander Example",
                "prompt": "Use the local MCP tool desktop-commander to read the file located at ~/Downloads/example.txt. Return the file's contents. Then summarize it.",
                "wait_time": 90000
            }
        ]
    }
    
    with open(output, "w") as f:
        json.dump(template, f, indent=2)
    
    console.print(f"[bold green]Task template created:[/] {output}")
    console.print("Edit this file to define your own sequence of tasks.")


if __name__ == "__main__":
    app()