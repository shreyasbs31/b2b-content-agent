"""Main entry point for the B2B Content Agent System."""

import asyncio
import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.logging import RichHandler

from config import settings

# Set up logging
logging.basicConfig(
    level=settings.log_level,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger(__name__)
console = Console()
app = typer.Typer(help="B2B Sales Content Generation Agent System")


@app.command()
def setup():
    """Initial setup and configuration check."""
    console.print("\n[bold cyan]🚀 B2B Content Agent System - Setup[/bold cyan]\n")
    
    # Check API keys
    checks = {
        "Google Gemini API": bool(settings.google_api_key),
        "Project structure": settings.project_root.exists(),
        "Data directories": settings.output_dir.exists() and settings.sample_inputs_dir.exists(),
    }
    
    console.print("[bold]Configuration Checks:[/bold]")
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        console.print(f"  {status} {check_name}")
    
    if not all(checks.values()):
        console.print("\n[bold red]⚠️  Some checks failed. Please review your .env file.[/bold red]")
        console.print("Copy .env.example to .env and add your API keys.\n")
        raise typer.Exit(1)
    
    console.print("\n[bold green]✅ Setup complete! Ready to build agents.[/bold green]\n")


@app.command()
def info():
    """Display system information and agent architecture."""
    console.print("\n[bold cyan]📊 B2B Content Agent System - Architecture[/bold cyan]\n")
    
    console.print("[bold]10 Specialized Agents across 3 Crews:[/bold]\n")
    
    console.print("[bold yellow]CREW 1: Research & Planning (3 agents)[/bold yellow]")
    console.print("  1. Product Analyst Agent")
    console.print("  2. Persona Researcher Agent")
    console.print("  3. Content Strategist Agent\n")
    
    console.print("[bold yellow]CREW 2: Content Generation (4 agents)[/bold yellow]")
    console.print("  4. Case Study Writer Agent")
    console.print("  5. White Paper Author Agent")
    console.print("  6. Pitch Deck Designer Agent")
    console.print("  7. Social Media Specialist Agent\n")
    
    console.print("[bold yellow]CREW 3: Review & Polish (3 agents)[/bold yellow]")
    console.print("  8. Quality Assurance Agent")
    console.print("  9. Brand Voice Guardian Agent")
    console.print("  10. SEO Optimizer Agent\n")
    
    console.print(f"[dim]Version: {settings.environment} | Model: {settings.gemini_model_pro}[/dim]\n")


@app.command()
def generate(
    content_type: str = typer.Option(
        "case-study",
        "--type",
        "-t",
        help="Content type: case-study, white-paper, pitch-deck, social"
    ),
    input_path: Path = typer.Option(
        None,
        "--input",
        "-i",
        help="Path to product documentation or data"
    ),
    count: int = typer.Option(
        10,
        "--count",
        "-c",
        help="Number of content pieces to generate"
    ),
    enable_hitl: bool = typer.Option(
        False,
        "--hitl",
        help="Enable human-in-the-loop review gates"
    ),
):
    """Generate B2B sales content."""
    console.print(f"\n[bold cyan]🎯 Generating {count} {content_type}(s)...[/bold cyan]\n")
    
    if not input_path or not input_path.exists():
        console.print("[bold red]❌ Input file not found. Please provide a valid --input path.[/bold red]\n")
        raise typer.Exit(1)
    
    hitl_status = "✅ Enabled" if enable_hitl else "❌ Disabled"
    console.print(f"  📄 Input: {input_path}")
    console.print(f"  📊 Count: {count}")
    console.print(f"  👤 HITL: {hitl_status}\n")
    
    console.print("[bold yellow]⚠️  Agent implementation coming in MILESTONE 1...[/bold yellow]\n")
    
    # TODO: Implement actual generation flow
    # from src.flows.content_generation_flow import B2BSalesContentFlow
    # flow = B2BSalesContentFlow()
    # result = await flow.generate(...)


@app.command()
def test_crew1(
    input_file: Path = typer.Option(
        None,
        "--input",
        "-i",
        help="Path to product documentation or data file"
    ),
    url: str = typer.Option(
        None,
        "--url",
        "-u",
        help="URL to product website or documentation"
    ),
    max_retries: int = typer.Option(
        3,
        "--retries",
        "-r",
        help="Maximum number of retry attempts on failure"
    ),
):
    """Test CREW 1 - Research & Planning agents with validation and error recovery."""
    console.print("\n[bold cyan]🧪 Testing CREW 1 - Research & Planning[/bold cyan]\n")
    
    # Import here to avoid issues if module not ready
    try:
        from b2b_content_agent.crew import ResearchPlanningCrew
        from b2b_content_agent.validators import validate_inputs, validate_crew1_outputs, InputValidationError, OutputValidationError
        from b2b_content_agent.recovery import run_crew_with_recovery, RecoveryError
    except ImportError as e:
        console.print(f"[bold red]❌ Error importing crew: {e}[/bold red]\n")
        console.print("[yellow]Make sure you're running from the project root.[/yellow]\n")
        raise typer.Exit(1)
    
    # STEP 1: Validate inputs before processing
    console.print("[bold cyan]Step 1: Validating inputs...[/bold cyan]")
    try:
        validate_inputs(input_file=input_file, url=url)
        console.print("[green]✓ Input validation passed[/green]\n")
    except InputValidationError as e:
        console.print(f"[bold red]❌ Input validation failed:[/bold red]")
        console.print(f"[red]{str(e)}[/red]\n")
        raise typer.Exit(1)
    
    # Prepare input sources
    input_sources = []
    
    if input_file:
        input_sources.append(f"File: {input_file}")
    
    if url:
        input_sources.append(f"URL: {url}")
    
    if not input_sources:
        console.print("[yellow]No input provided. Using example product...[/yellow]\n")
        input_sources.append(
            "Raw text: AI Meeting Necklace - A hands-free wearable device that automatically "
            "records, transcribes, and summarizes your meetings."
        )
    
    inputs = {
        'input_sources': "\n".join(input_sources)
    }
    
    console.print("[bold cyan]Step 2: Running CREW 1 with error recovery...[/bold cyan]")
    console.print(f"[dim]Max retries: {max_retries}[/dim]")
    console.print("[bold]Inputs:[/bold]")
    for source in input_sources:
        console.print(f"  • {source}")
    console.print()
    
    # STEP 2: Run crew with error recovery
    try:
        crew = ResearchPlanningCrew().crew()
        result = run_crew_with_recovery(
            crew_kickoff_func=crew.kickoff,
            inputs=inputs,
            crew_name="CREW 1",
            output_dir=settings.output_dir,
            max_retries=max_retries
        )
        
        console.print("\n[bold green]✅ CREW 1 Execution Complete![/bold green]\n")
        
        # STEP 3: Validate outputs
        console.print("[bold cyan]Step 3: Validating outputs...[/bold cyan]")
        try:
            validate_crew1_outputs(settings.output_dir)
            console.print("[green]✓ Output validation passed[/green]\n")
        except OutputValidationError as e:
            console.print(f"[bold yellow]⚠️ Output validation warnings:[/bold yellow]")
            console.print(f"[yellow]{str(e)}[/yellow]\n")
            console.print("[dim]The crew completed but some outputs may not meet quality standards.[/dim]\n")
        
        console.print("[bold green]🎉 CREW 1 Test Complete![/bold green]\n")
        console.print("Generated files:")
        console.print("  • output/01_product_analysis.md")
        console.print("  • output/02_persona_library.md")
        console.print("  • output/03_content_strategy.md\n")
        
    except RecoveryError as e:
        console.print(f"\n[bold red]💥 CREW 1 Failed After All Retries[/bold red]")
        console.print(f"[red]{str(e)}[/red]\n")
        console.print("[yellow]Check .recovery/ folder for partial results.[/yellow]\n")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]\n")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def test_crew2(
    crew1_output_dir: Path = typer.Option(
        None,
        "--crew1-dir",
        "-c",
        help="Path to CREW 1 output directory (contains product_analysis, personas, strategy)"
    ),
    output_dir: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to save CREW 2 generated content"
    ),
):
    """Test CREW 2 - Content Generation agents (parallel execution).
    
    Generates 4 types of content in parallel:
    - Case studies
    - White papers
    - Pitch decks
    - Social media posts
    
    Requires outputs from CREW 1 (test-crew1 command).
    """
    console.print("\n[bold cyan]🧪 Testing CREW 2 - Content Generation[/bold cyan]\n")
    
    # Import here to avoid issues if module not ready
    try:
        from b2b_content_agent.content_generation_crew import run_content_generation
    except ImportError as e:
        console.print(f"[bold red]❌ Error importing content generation crew: {e}[/bold red]\n")
        console.print("[yellow]Make sure you're running from the project root.[/yellow]\n")
        raise typer.Exit(1)
    
    # Set defaults
    if crew1_output_dir is None:
        crew1_output_dir = settings.output_dir
    
    if output_dir is None:
        output_dir = settings.output_dir / "content_output"
    
    # STEP 1: Check for CREW 1 outputs
    console.print("[bold cyan]Step 1: Loading CREW 1 outputs...[/bold cyan]")
    
    required_files = {
        'product_analysis': crew1_output_dir / "01_product_analysis.md",
        'persona_library': crew1_output_dir / "02_persona_library.md",
        'content_strategy': crew1_output_dir / "03_content_strategy.md"
    }
    
    missing_files = [name for name, path in required_files.items() if not path.exists()]
    
    if missing_files:
        console.print(f"[bold red]❌ Missing CREW 1 outputs:[/bold red]")
        for name in missing_files:
            console.print(f"  • {name}: {required_files[name]}")
        console.print("\n[yellow]Run 'python main.py test-crew1' first to generate these files.[/yellow]\n")
        raise typer.Exit(1)
    
    console.print("[green]✓ All CREW 1 outputs found[/green]")
    for name, path in required_files.items():
        console.print(f"  • {name}: {path}")
    console.print()
    
    # Load CREW 1 outputs
    crew1_outputs = {}
    for name, path in required_files.items():
        with open(path, 'r') as f:
            crew1_outputs[name] = f.read()
        console.print(f"[dim]Loaded {name}: {len(crew1_outputs[name])} chars[/dim]")
    console.print()
    
    # STEP 2: Run CREW 2 with parallel execution
    console.print("[bold cyan]Step 2: Running CREW 2 (Parallel Execution)...[/bold cyan]")
    console.print("[bold]Processing Mode:[/bold] Hierarchical (4 agents in parallel)")
    console.print("[bold]Expected Duration:[/bold] 10-15 minutes")
    console.print()
    console.print("[bold]Agents Running:[/bold]")
    console.print("  🏃 Agent #4: Case Study Writer")
    console.print("  🏃 Agent #5: White Paper Author")
    console.print("  🏃 Agent #6: Pitch Deck Designer")
    console.print("  🏃 Agent #7: Social Media Specialist")
    console.print()
    console.print("[dim]Press Ctrl+C to cancel (partial results will be saved)[/dim]\n")
    
    try:
        result = run_content_generation(
            product_analysis=crew1_outputs['product_analysis'],
            persona_library=crew1_outputs['persona_library'],
            content_strategy=crew1_outputs['content_strategy'],
            output_dir=str(output_dir)
        )
        
        console.print("\n[bold green]✅ CREW 2 Execution Complete![/bold green]\n")
        
        # STEP 3: Summary
        console.print("[bold cyan]Step 3: Content Generation Summary[/bold cyan]\n")
        
        summary_items = [
            ("Case Studies", result.get('case_studies', '')),
            ("White Papers", result.get('white_papers', '')),
            ("Pitch Decks", result.get('pitch_decks', '')),
            ("Social Posts", result.get('social_posts', ''))
        ]
        
        for content_type, content in summary_items:
            if content:
                word_count = len(str(content).split())
                console.print(f"  ✓ {content_type}: {word_count:,} words generated")
            else:
                console.print(f"  ⚠️  {content_type}: No content generated")
        
        console.print(f"\n[bold]Execution Time:[/bold] {result.get('execution_time', 'N/A')}")
        console.print(f"[bold]Output Directory:[/bold] {output_dir}\n")
        
        console.print("[bold green]🎉 CREW 2 Test Complete![/bold green]\n")
        console.print("[dim]Generated content ready for CREW 3 (Review & Polish)[/dim]\n")
        
    except KeyboardInterrupt:
        console.print("\n\n[bold yellow]⚠️  Generation cancelled by user[/bold yellow]")
        console.print("[dim]Partial results may have been saved to output directory[/dim]\n")
        raise typer.Exit(0)
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]\n")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def test_crew3():
    """Test CREW 3 - Review & Polish agents."""
    console.print("\n[bold cyan]🧪 Testing CREW 3 - Review & Polish[/bold cyan]\n")
    console.print("[bold yellow]⚠️  Coming in MILESTONE 3...[/bold yellow]\n")


if __name__ == "__main__":
    app()
