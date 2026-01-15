"""Error recovery and retry utilities for CREW execution.

This module provides:
1. Retry logic with exponential backoff
2. Partial results saving
3. Error logging and reporting
"""

import logging
import time
import json
from pathlib import Path
from typing import Any, Callable, Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class RecoveryError(Exception):
    """Raised when recovery attempts are exhausted."""
    pass


def save_partial_results(output_dir: Path, crew_name: str, partial_data: Dict[str, Any]) -> None:
    """Save partial results in case of failure.
    
    Args:
        output_dir: Directory to save partial results
        crew_name: Name of the crew (e.g., "crew1")
        partial_data: Dictionary of partial results to save
    """
    try:
        # Create recovery directory if it doesn't exist
        recovery_dir = output_dir / ".recovery"
        recovery_dir.mkdir(exist_ok=True, parents=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recovery_file = recovery_dir / f"{crew_name}_partial_{timestamp}.json"
        
        # Save partial data
        with open(recovery_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'crew': crew_name,
                'partial_data': partial_data
            }, f, indent=2)
        
        logger.info(f"💾 Partial results saved to: {recovery_file}")
        
    except Exception as e:
        logger.error(f"Failed to save partial results: {e}")


def run_with_retry(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 5.0,
    backoff_factor: float = 2.0,
    crew_name: Optional[str] = None,
    output_dir: Optional[Path] = None
) -> Any:
    """Execute a function with retry logic and exponential backoff.
    
    Args:
        func: Function to execute
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 5)
        backoff_factor: Multiplier for delay on each retry (default: 2)
        crew_name: Optional name of crew for logging
        output_dir: Optional output directory for saving partial results
        
    Returns:
        Result of the function execution
        
    Raises:
        RecoveryError: If all retry attempts fail
        
    Example:
        result = run_with_retry(
            lambda: crew.kickoff(inputs=inputs),
            max_retries=3,
            crew_name="crew1"
        )
    """
    last_exception = None
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            logger.info(f"🚀 Executing {crew_name or 'function'} (attempt {attempt + 1}/{max_retries})")
            result = func()
            
            if attempt > 0:
                logger.info(f"✅ Success after {attempt + 1} attempt(s)")
            
            return result
            
        except KeyboardInterrupt:
            logger.warning("⚠️ Execution interrupted by user")
            raise
            
        except Exception as e:
            last_exception = e
            logger.error(f"❌ Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            
            # If this is not the last attempt, wait and retry
            if attempt < max_retries - 1:
                logger.info(f"⏳ Waiting {delay:.1f}s before retry...")
                time.sleep(delay)
                delay *= backoff_factor
            else:
                # Last attempt failed - try to save partial results
                logger.error(f"💥 All {max_retries} attempts failed")
                
                if crew_name and output_dir:
                    try:
                        # Try to save any partial outputs that might exist
                        partial_data = {
                            'error': str(last_exception),
                            'attempts': max_retries,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        # Check if any output files were created
                        if output_dir.exists():
                            partial_data['partial_files'] = [
                                str(f) for f in output_dir.glob("*.md")
                            ]
                        
                        save_partial_results(output_dir, crew_name, partial_data)
                    except Exception as save_error:
                        logger.error(f"Failed to save recovery data: {save_error}")
    
    # All retries exhausted
    raise RecoveryError(
        f"Failed after {max_retries} attempts. Last error: {str(last_exception)}"
    ) from last_exception


def run_crew_with_recovery(
    crew_kickoff_func: Callable,
    inputs: Dict[str, Any],
    crew_name: str,
    output_dir: Path,
    max_retries: int = 3
) -> Any:
    """Run a crew with full error recovery support.
    
    This is a convenience wrapper around run_with_retry specifically for CrewAI crews.
    
    Args:
        crew_kickoff_func: The crew.kickoff function to execute
        inputs: Dictionary of inputs to pass to the crew
        crew_name: Name of the crew (for logging)
        output_dir: Directory where outputs will be saved
        max_retries: Maximum retry attempts (default: 3)
        
    Returns:
        Result from crew execution
        
    Raises:
        RecoveryError: If all retry attempts fail
        
    Example:
        from b2b_content_agent.crew import ResearchPlanningCrew
        
        crew = ResearchPlanningCrew().crew()
        result = run_crew_with_recovery(
            crew_kickoff_func=crew.kickoff,
            inputs={'input_sources': 'file.md'},
            crew_name='crew1',
            output_dir=Path('output')
        )
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Starting {crew_name} with error recovery enabled")
    logger.info(f"Max retries: {max_retries}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"{'='*60}\n")
    
    def execute():
        return crew_kickoff_func(inputs=inputs)
    
    try:
        result = run_with_retry(
            func=execute,
            max_retries=max_retries,
            initial_delay=5.0,
            backoff_factor=2.0,
            crew_name=crew_name,
            output_dir=output_dir
        )
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ {crew_name} completed successfully!")
        logger.info(f"{'='*60}\n")
        
        return result
        
    except RecoveryError as e:
        logger.error(f"\n{'='*60}")
        logger.error(f"💥 {crew_name} failed after all retry attempts")
        logger.error(f"Error: {str(e)}")
        logger.error(f"{'='*60}\n")
        raise


def cleanup_recovery_files(output_dir: Path, keep_days: int = 7) -> None:
    """Clean up old recovery files.
    
    Args:
        output_dir: Directory containing .recovery folder
        keep_days: Number of days to keep recovery files (default: 7)
    """
    try:
        recovery_dir = output_dir / ".recovery"
        if not recovery_dir.exists():
            return
        
        cutoff_time = time.time() - (keep_days * 24 * 60 * 60)
        
        for recovery_file in recovery_dir.glob("*.json"):
            if recovery_file.stat().st_mtime < cutoff_time:
                recovery_file.unlink()
                logger.debug(f"Deleted old recovery file: {recovery_file.name}")
                
    except Exception as e:
        logger.warning(f"Failed to cleanup recovery files: {e}")
