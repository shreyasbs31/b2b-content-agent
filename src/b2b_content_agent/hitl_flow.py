"""HITL (Human-in-the-Loop) Flow Orchestration

This module orchestrates the full content generation pipeline with approval gates:
CREW 1 → Gate 1 → Gate 2 → Gate 3 → CREW 2 → Gate 4 → CREW 3 → Gate 5

Gates allow human review and approval before proceeding to the next stage.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Literal
from dataclasses import dataclass, asdict

from b2b_content_agent.crew import ResearchPlanningCrew
from b2b_content_agent.content_generation_crew import ContentGenerationCrew
from b2b_content_agent.review_polish_crew import ReviewPolishCrew
from b2b_content_agent.rate_limiter import (
    RateLimiter,
    RateLimitConfig,
    get_rate_limiter
)

logger = logging.getLogger(__name__)


@dataclass
class HITLSession:
    """Tracks the state of a HITL session"""
    session_id: str
    started_at: str
    input_sources: str
    auto_approve: bool
    
    # Crew outputs
    product_analysis: Optional[str] = None
    persona_library: Optional[str] = None
    content_strategy: Optional[str] = None
    generated_content: Optional[str] = None
    final_content: Optional[str] = None
    
    # Gate approval status
    gate1_approved: bool = False  # Product Analysis
    gate2_approved: bool = False  # Persona Library
    gate3_approved: bool = False  # Content Strategy
    gate4_approved: bool = False  # Generated Content
    gate5_approved: bool = False  # Final Review
    
    # Iteration tracking
    crew1_iterations: int = 0
    crew2_iterations: int = 0
    crew3_iterations: int = 0
    
    completed_at: Optional[str] = None
    
    def save(self, output_dir: Path):
        """Save session state to JSON"""
        output_dir.mkdir(parents=True, exist_ok=True)
        session_file = output_dir / f"hitl_session_{self.session_id}.json"
        
        with open(session_file, 'w') as f:
            json.dump(asdict(self), f, indent=2)
        
        return session_file


class HITLOrchestrator:
    """Orchestrates the full pipeline with human approval gates"""
    
    def __init__(
        self,
        auto_approve: bool = False,
        output_dir: str = "output/hitl",
        session_id: Optional[str] = None,
        rate_limit_config: Optional[RateLimitConfig] = None
    ):
        """
        Initialize HITL orchestrator
        
        Args:
            auto_approve: If True, automatically approve all gates (for testing)
            output_dir: Directory to save outputs and session state
            session_id: Resume existing session (if provided)
            rate_limit_config: Rate limiting configuration (uses defaults if None)
        """
        self.auto_approve = auto_approve
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize rate limiter
        self.rate_limiter = get_rate_limiter(rate_limit_config)
        
        # Generate or load session
        if session_id:
            self.session = self._load_session(session_id)
        else:
            self.session = HITLSession(
                session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
                started_at=datetime.now().isoformat(),
                input_sources="",
                auto_approve=auto_approve
            )
        
        self.crews_initialized = False
    
    def _load_session(self, session_id: str) -> HITLSession:
        """Load existing session from JSON"""
        session_file = self.output_dir / f"hitl_session_{session_id}.json"
        
        if not session_file.exists():
            raise FileNotFoundError(f"Session {session_id} not found at {session_file}")
        
        with open(session_file) as f:
            data = json.load(f)
        
        session = HITLSession(**data)
        
        # CRITICAL: Validate session state
        if not session.input_sources or not session.input_sources.strip():
            raise ValueError(f"Session {session_id} has invalid/empty input_sources")
        
        # Warn if session is incomplete
        if not session.gate5_approved:
            print(f"ℹ️  Resuming incomplete session. Current state:")
            print(f"   Gate 1 (Product Analysis): {'✅' if session.gate1_approved else '❌'}")
            print(f"   Gate 2 (Persona Library): {'✅' if session.gate2_approved else '❌'}")
            print(f"   Gate 3 (Content Strategy): {'✅' if session.gate3_approved else '❌'}")
            print(f"   Gate 4 (Generated Content): {'✅' if session.gate4_approved else '❌'}")
            print(f"   Gate 5 (Final Review): {'✅' if session.gate5_approved else '❌'}")
        
        return session
    
    def _check_file_staleness(self, filepath: str, max_age_hours: int = 24) -> bool:
        """
        Check if an output file is stale (older than session start)
        
        Returns True if file is stale, False if fresh
        """
        file_path = Path(filepath)
        if not file_path.exists():
            return False
        
        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        session_start = datetime.fromisoformat(self.session.started_at)
        
        age_hours = (datetime.now() - file_mtime).total_seconds() / 3600
        is_before_session = file_mtime < session_start
        
        if is_before_session or age_hours > max_age_hours:
            return True
        return False
    
    def _warn_stale_outputs(self):
        """Warn user about stale output files"""
        stale_files = []
        critical_outputs = [
            "output/01_product_analysis.md",
            "output/02_persona_library.md", 
            "output/03_content_strategy.md"
        ]
        
        for filepath in critical_outputs:
            full_path = Path(filepath)
            if full_path.exists() and self._check_file_staleness(str(full_path)):
                file_mtime = datetime.fromtimestamp(full_path.stat().st_mtime)
                age_hours = (datetime.now() - file_mtime).total_seconds() / 3600
                stale_files.append((filepath, age_hours))
        
        if stale_files:
            print("\n" + "⚠️ " * 20)
            print("⚠️  WARNING: Found stale output files from previous runs!")
            print("⚠️ " * 20)
            for filepath, age_hours in stale_files:
                if age_hours < 24:
                    age_str = f"{age_hours:.1f} hours ago"
                else:
                    age_str = f"{age_hours/24:.1f} days ago"
                print(f"   📁 {filepath} (created {age_str})")
            print("\n💡 These files may be from a different product/test run!")
            print("   Consider cleaning outputs with: rm -rf output/*.md output/*/*.md\n")
            
            response = input("Continue anyway? (y/n): ").strip().lower()
            if response != 'y':
                print("🛑 Stopping. Please clean outputs and restart.")
                sys.exit(0)
            print()
    
    def _initialize_crews(self):
        """Lazy initialization of crews"""
        if not self.crews_initialized:
            print("\n🔧 Initializing crews...")
            self.crew1 = ResearchPlanningCrew()
            self.crew2 = ContentGenerationCrew()
            self.crew3 = ReviewPolishCrew()
            self.crews_initialized = True
            print("✅ Crews initialized\n")
    
    def _print_separator(self, char: str = "=", length: int = 80):
        """Print a separator line"""
        print(char * length)
    
    def _print_gate_header(self, gate_num: int, gate_name: str):
        """Print approval gate header"""
        self._print_separator()
        print(f"🚪 APPROVAL GATE {gate_num}: {gate_name}")
        self._print_separator()
    
    def _show_content_preview(self, content: str, max_lines: int = 20):
        """Show a preview of content"""
        lines = content.split('\n')
        
        print("\n📄 Content Preview:")
        print("-" * 80)
        
        if len(lines) <= max_lines:
            print(content)
        else:
            preview_lines = lines[:max_lines]
            print('\n'.join(preview_lines))
            print(f"\n... ({len(lines) - max_lines} more lines)")
        
        print("-" * 80)
    
    def _get_approval(
        self,
        gate_num: int,
        gate_name: str,
        content: str,
        allow_edit: bool = True
    ) -> tuple[Literal["approve", "reject", "edit", "feedback"], Optional[str]]:
        """
        Get approval decision from user
        
        Returns:
            (decision, feedback): decision is "approve"/"reject"/"edit"/"feedback",
                                 feedback is additional text for reject/feedback
        """
        if self.auto_approve:
            print(f"\n✅ AUTO-APPROVED (Gate {gate_num}: {gate_name})")
            return ("approve", None)
        
        self._print_gate_header(gate_num, gate_name)
        self._show_content_preview(content)
        
        print("\n🤔 Review Options:")
        print("  [a] Approve - Continue to next stage")
        print("  [r] Reject - Stop pipeline and provide feedback")
        if allow_edit:
            print("  [e] Edit - Make changes and re-run this stage")
            print("  [f] Feedback - Provide feedback and re-run with modifications")
        print("  [v] View Full - See complete content")
        print("  [s] Save - Save content to file for review")
        
        while True:
            choice = input("\nYour decision [a/r/e/f/v/s]: ").lower().strip()
            
            if choice == 'a':
                print(f"✅ Approved: {gate_name}")
                return ("approve", None)
            
            elif choice == 'r':
                feedback = input("\n💬 Why are you rejecting? (optional): ").strip()
                print(f"❌ Rejected: {gate_name}")
                return ("reject", feedback)
            
            elif choice == 'e' and allow_edit:
                print("\n✏️  Edit mode:")
                print("Enter your modifications (or press Ctrl+D when done):")
                
                try:
                    lines = []
                    while True:
                        line = input()
                        lines.append(line)
                except EOFError:
                    modifications = '\n'.join(lines)
                    if modifications.strip():
                        return ("edit", modifications)
                    else:
                        print("⚠️  No modifications provided, try again")
                        continue
            
            elif choice == 'f' and allow_edit:
                feedback = input("\n💬 What feedback would you like to provide? ").strip()
                if feedback:
                    return ("feedback", feedback)
                else:
                    print("⚠️  No feedback provided, try again")
                    continue
            
            elif choice == 'v':
                print("\n" + "=" * 80)
                print("📄 FULL CONTENT:")
                print("=" * 80)
                print(content)
                print("=" * 80)
                continue
            
            elif choice == 's':
                filename = f"gate{gate_num}_{gate_name.lower().replace(' ', '_')}_{int(time.time())}.txt"
                filepath = self.output_dir / filename
                
                with open(filepath, 'w') as f:
                    f.write(content)
                
                print(f"💾 Saved to: {filepath}")
                continue
            
            else:
                print("⚠️  Invalid choice. Please choose a/r/e/f/v/s")
    
    def run_crew1(
        self,
        input_sources: str,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run CREW 1: Research & Planning
        
        Returns dict with product_analysis, persona_library, content_strategy
        """
        self._initialize_crews()
        
        self.session.crew1_iterations += 1
        iteration = self.session.crew1_iterations
        
        print(f"\n{'='*80}")
        print(f"🚀 RUNNING CREW 1: Research & Planning (Iteration {iteration})")
        print(f"{'='*80}\n")
        
        if feedback:
            print(f"💬 Applying feedback: {feedback}\n")
        
        # Prepare inputs
        inputs = {
            "input_sources": input_sources,
            "product_name": "Product",  # Will be extracted
            "product_description": input_sources,
            "target_content_type": "case_study"
        }
        
        if feedback:
            inputs["additional_guidance"] = feedback
        
        # Run crew with rate limiting and retry logic
        start_time = time.time()
        
        try:
            result = self.rate_limiter.execute_with_retry(
                self.crew1.crew().kickoff,
                inputs=inputs,
                context="CREW 1: Research & Planning"
            )
        except RuntimeError as e:
            # Check if it's a quota exhaustion error
            if "quota exhausted" in str(e).lower():
                logger.error(
                    f"\n{'='*80}\n"
                    f"❌ API QUOTA EXHAUSTED\n"
                    f"{'='*80}\n"
                    f"Your current LLM provider has run out of quota.\n\n"
                    f"SOLUTIONS:\n"
                    f"1. Add a fallback provider API key to .env:\n"
                    f"   - GROQ_API_KEY (recommended, free, 14,400 req/day)\n"
                    f"   - OPENAI_API_KEY (paid, reliable)\n"
                    f"   - ANTHROPIC_API_KEY (paid, high quality)\n\n"
                    f"2. Wait for quota to reset (Gemini: midnight Pacific)\n\n"
                    f"3. Upgrade to paid tier for current provider\n"
                    f"{'='*80}\n"
                )
            # Save session before raising
            self.session.save(self.output_dir)
            logger.info(f"Session saved. Resume with: --resume {self.session.session_id}")
            raise
        except Exception as e:
            logger.error(f"CREW 1 failed after retries: {e}")
            # Save session before raising
            self.session.save(self.output_dir)
            logger.info(f"Session saved. Resume with: --resume {self.session.session_id}")
            raise
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ CREW 1 completed in {elapsed/60:.1f} minutes")
        
        # Parse result (result contains all three task outputs)
        result_str = result.raw if hasattr(result, 'raw') else str(result)
        
        # Try to read from output files - these should exist if tasks completed successfully
        product_analysis = self._read_output_file("01_product_analysis.md")
        persona_library = self._read_output_file("02_persona_library.md")
        content_strategy = self._read_output_file("03_content_strategy.md")
        
        # CRITICAL: If files don't exist, we have a problem - don't use result_str as fallback
        # because result_str only contains the LAST task output (content strategy)
        if not product_analysis or not persona_library or not content_strategy:
            error_msg = "CREW 1 output files missing or empty!\n"
            if not product_analysis:
                error_msg += "  ❌ 01_product_analysis.md not found\n"
            if not persona_library:
                error_msg += "  ❌ 02_persona_library.md not found\n"
            if not content_strategy:
                error_msg += "  ❌ 03_content_strategy.md not found\n"
            error_msg += "This usually means CREW 1 tasks didn't write output files properly."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Update session with ALL outputs (CRITICAL: ensures Gate 2/3 re-runs update data)
        self.session.product_analysis = product_analysis
        self.session.persona_library = persona_library
        self.session.content_strategy = content_strategy
        
        return {
            "product_analysis": product_analysis,
            "persona_library": persona_library,
            "content_strategy": content_strategy,
            "raw_result": result_str
        }
    
    def _truncate_large_input(self, content: str, max_chars: int = 50000, name: str = "input") -> str:
        """
        Truncate large inputs to prevent LLM context window issues.
        
        Args:
            content: The content to potentially truncate
            max_chars: Maximum characters to keep (default 50K)
            name: Name of the input for logging
            
        Returns:
            Truncated content with message if truncation occurred
        """
        if len(content) <= max_chars:
            return content
        
        logger.warning(f"{name} is {len(content):,} chars, truncating to {max_chars:,} chars")
        print(f"⚠️  {name} is large ({len(content):,} chars), truncating to {max_chars:,} chars for API limits")
        
        # Keep first part and add truncation message
        truncated = content[:max_chars]
        truncated += f"\n\n[... Content truncated. Original size: {len(content):,} chars. Showing first {max_chars:,} chars ...]"
        
        return truncated
    
    def run_crew2(
        self,
        product_analysis: str,
        persona_library: str,
        content_strategy: str,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run CREW 2: Content Generation
        
        Returns dict with generated content from all 4 writers
        """
        self._initialize_crews()
        
        self.session.crew2_iterations += 1
        iteration = self.session.crew2_iterations
        
        print(f"\n{'='*80}")
        print(f"🚀 RUNNING CREW 2: Content Generation (Iteration {iteration})")
        print(f"{'='*80}\n")
        
        if feedback:
            print(f"💬 Applying feedback: {feedback}\n")
        
        # Truncate large inputs to prevent LLM context issues
        product_analysis_safe = self._truncate_large_input(product_analysis, max_chars=30000, name="Product Analysis")
        persona_library_safe = self._truncate_large_input(persona_library, max_chars=50000, name="Persona Library")
        content_strategy_safe = self._truncate_large_input(content_strategy, max_chars=50000, name="Content Strategy")
        
        # Prepare inputs
        inputs = {
            "persona_profile": persona_library_safe,
            "content_strategy": content_strategy_safe,
            "product_analysis": product_analysis_safe,
            "content_type": "case_study",
            "word_count_target": 1500
        }
        
        if feedback:
            inputs["additional_guidance"] = feedback
        
        # Run crew with rate limiting and retry logic
        start_time = time.time()
        
        try:
            result = self.rate_limiter.execute_with_retry(
                self.crew2.crew().kickoff,
                inputs=inputs,
                context="CREW 2: Content Generation"
            )
        except Exception as e:
            logger.error(f"CREW 2 failed after retries: {e}")
            # Save session before raising
            self.session.save(self.output_dir)
            logger.info(f"Session saved. Resume with: --resume {self.session.session_id}")
            raise
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ CREW 2 completed in {elapsed/60:.1f} minutes")
        
        # Parse result
        result_str = result.raw if hasattr(result, 'raw') else str(result)
        
        # Try to read from output files
        case_study = self._read_output_file("case_studies/case_study_001.md") or result_str
        white_paper = self._read_output_file("white_papers/white_paper_001.md") or ""
        pitch_deck = self._read_output_file("pitch_decks/pitch_deck_001.md") or ""
        social_media = self._read_output_file("social_media/social_post_001.md") or ""
        
        return {
            "case_study": case_study,
            "white_paper": white_paper,
            "pitch_deck": pitch_deck,
            "social_media": social_media,
            "raw_result": result_str
        }
    
    def run_crew3(
        self,
        generated_content: str,
        content_type: str = "case_study",
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run CREW 3: Review & Polish
        
        Returns dict with reviewed and polished content
        """
        self._initialize_crews()
        
        self.session.crew3_iterations += 1
        iteration = self.session.crew3_iterations
        
        print(f"\n{'='*80}")
        print(f"🚀 RUNNING CREW 3: Review & Polish (Iteration {iteration})")
        print(f"{'='*80}\n")
        
        if feedback:
            print(f"💬 Applying feedback: {feedback}\n")
        
        # Prepare inputs
        inputs = {
            "content": generated_content,
            "content_type": content_type,
            "target_keywords": "productivity, automation, sales, efficiency",
            "brand_guidelines": "Professional, data-driven, results-oriented"
        }
        
        if feedback:
            inputs["additional_guidance"] = feedback
        
        # Run crew with rate limiting and retry logic
        start_time = time.time()
        
        try:
            result = self.rate_limiter.execute_with_retry(
                self.crew3.crew().kickoff,
                inputs=inputs,
                context="CREW 3: Review & Polish"
            )
        except Exception as e:
            logger.error(f"CREW 3 failed after retries: {e}")
            # Save session before raising
            self.session.save(self.output_dir)
            logger.info(f"Session saved. Resume with: --resume {self.session.session_id}")
            raise
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ CREW 3 completed in {elapsed/60:.1f} minutes")
        
        # Parse result
        result_str = result.raw if hasattr(result, 'raw') else str(result)
        
        # Try to read review files
        qa_review = self._read_output_file("reviews/qa_review.md") or result_str
        brand_review = self._read_output_file("reviews/brand_review.md") or ""
        seo_review = self._read_output_file("reviews/seo_optimization.md") or ""
        
        return {
            "qa_review": qa_review,
            "brand_review": brand_review,
            "seo_review": seo_review,
            "polished_content": result_str,
            "raw_result": result_str
        }
    
    def _read_output_file(self, relative_path: str) -> Optional[str]:
        """Try to read an output file from the project's output directory
        
        Args:
            relative_path: Path relative to project root output/ directory
                          e.g., "01_product_analysis.md" or "case_studies/case_study_001.md"
        
        Returns:
            File content as string, or None if file not found
        """
        # CRITICAL: CrewAI tasks write to project_root/output/, not to output/hitl/
        # The output_file in YAML is relative to project root (e.g., "output/01_product_analysis.md")
        # So we need to read from Path("output") / relative_path, not self.output_dir / relative_path
        filepath = Path("output") / relative_path
        
        if filepath.exists():
            try:
                with open(filepath) as f:
                    content = f.read()
                    logger.debug(f"✓ Read {len(content)} bytes from {filepath}")
                    return content
            except Exception as e:
                logger.warning(f"⚠️  Could not read {filepath}: {e}")
        else:
            logger.debug(f"✗ File not found: {filepath}")
        
        return None
    
    def run_full_pipeline(
        self,
        input_sources: str,
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """
        Run the complete HITL pipeline with all approval gates
        
        Args:
            input_sources: Initial product information
            max_iterations: Maximum iterations per crew before forcing continuation
        
        Returns:
            Final outputs from all crews
        """
        # CRITICAL: Input validation
        if not input_sources or not input_sources.strip():
            raise ValueError("input_sources cannot be empty")
        
        if max_iterations < 1:
            raise ValueError(f"max_iterations must be >= 1, got {max_iterations}")
        
        if max_iterations > 10:
            print(f"⚠️  Warning: max_iterations={max_iterations} is very high. Consider using <= 5")
        
        self.session.input_sources = input_sources
        
        # Warn about stale output files (unless resuming session)
        if self.session.crew1_iterations == 0:
            self._warn_stale_outputs()
        
        print("\n" + "="*80)
        print("🎯 STARTING HITL PIPELINE")
        print("="*80)
        print(f"Session ID: {self.session.session_id}")
        print(f"Auto-approve: {self.auto_approve}")
        print(f"Output directory: {self.output_dir}")
        print("="*80 + "\n")
        
        # ===================================================================
        # CREW 1: Research & Planning (Skip if already approved)
        # ===================================================================
        
        if self.session.gate3_approved:
            print("✅ CREW 1 already completed (Gates 1-3 approved) - SKIPPING\n")
        else:
            crew1_feedback = None
            
            while True:
                # Check if we've hit max iterations BEFORE running crew
                if self.session.crew1_iterations >= max_iterations:
                    print(f"\n🛑 Max iterations ({max_iterations}) reached at Gate 1 without approval")
                    return {"status": "max_iterations_gate1"}
                
                # Run CREW 1
                crew1_output = self.run_crew1(input_sources, crew1_feedback)
                # Note: run_crew1() already updates session.product_analysis, persona_library, content_strategy
                
                # GATE 1: Product Analysis Approval
                decision, feedback = self._get_approval(
                    gate_num=1,
                    gate_name="Product Analysis",
                    content=self.session.product_analysis
                )
                
                if decision == "reject":
                    print("\n🛑 Pipeline stopped at Gate 1")
                    return {"status": "rejected_at_gate1", "feedback": feedback}
                elif decision in ["edit", "feedback"]:
                    crew1_feedback = feedback
                    continue
                else:
                    self.session.gate1_approved = True
                    self.session.save(self.output_dir)  # Save after approval
                    break
            
            # GATE 2: Persona Library Approval
            gate2_iterations = 0
            while True:
                decision, feedback = self._get_approval(
                    gate_num=2,
                    gate_name="Persona Library",
                    content=self.session.persona_library
                )
                
                if decision == "reject":
                    print("\n🛑 Pipeline stopped at Gate 2")
                    return {"status": "rejected_at_gate2", "feedback": feedback}
                elif decision in ["edit", "feedback"]:
                    if gate2_iterations >= max_iterations:
                        print(f"\n🛑 Max iterations ({max_iterations}) reached at Gate 2 without approval")
                        return {"status": "max_iterations_gate2"}
                    # Re-run CREW 1 with feedback (updates ALL outputs)
                    crew1_output = self.run_crew1(input_sources, feedback)
                    gate2_iterations += 1
                    # Session already updated in run_crew1, re-loop for approval
                    continue
                else:
                    self.session.gate2_approved = True
                    self.session.save(self.output_dir)  # Save after approval
                    break
            
            # GATE 3: Content Strategy Approval
            gate3_iterations = 0
            while True:
                decision, feedback = self._get_approval(
                    gate_num=3,
                    gate_name="Content Strategy",
                    content=self.session.content_strategy
                )
                
                if decision == "reject":
                    print("\n🛑 Pipeline stopped at Gate 3")
                    return {"status": "rejected_at_gate3", "feedback": feedback}
                elif decision in ["edit", "feedback"]:
                    if gate3_iterations >= max_iterations:
                        print(f"\n🛑 Max iterations ({max_iterations}) reached at Gate 3 without approval")
                        return {"status": "max_iterations_gate3"}
                    # Re-run CREW 1 with feedback (updates ALL outputs)
                    crew1_output = self.run_crew1(input_sources, feedback)
                    gate3_iterations += 1
                    # Session already updated in run_crew1, re-loop for approval
                    continue
                else:
                    self.session.gate3_approved = True
                    self.session.save(self.output_dir)  # Save after approval
                    break
        
        # ===================================================================
        # CREW 2: Content Generation (Skip if already approved)
        # ===================================================================
        
        if self.session.gate4_approved:
            print("✅ CREW 2 already completed (Gate 4 approved) - SKIPPING\n")
        else:
            crew2_feedback = None
            
            while True:
                # Check if we've hit max iterations BEFORE running crew
                if self.session.crew2_iterations >= max_iterations:
                    print(f"\n🛑 Max iterations ({max_iterations}) reached at Gate 4 without approval")
                    return {"status": "max_iterations_gate4"}
                
                # Run CREW 2
                crew2_output = self.run_crew2(
                    product_analysis=self.session.product_analysis,
                    persona_library=self.session.persona_library,
                    content_strategy=self.session.content_strategy,
                    feedback=crew2_feedback
                )
                
                self.session.generated_content = crew2_output["raw_result"]
                
                # GATE 4: Generated Content Approval
                decision, feedback = self._get_approval(
                    gate_num=4,
                    gate_name="Generated Content",
                    content=self.session.generated_content
                )
                
                if decision == "reject":
                    print("\n🛑 Pipeline stopped at Gate 4")
                    return {"status": "rejected_at_gate4", "feedback": feedback}
                elif decision in ["edit", "feedback"]:
                    crew2_feedback = feedback
                    continue
                else:
                    self.session.gate4_approved = True
                    self.session.save(self.output_dir)  # Save after approval
                    break
        
        # ===================================================================
        # CREW 3: Review & Polish (Skip if already approved)
        # ===================================================================
        
        if self.session.gate5_approved:
            print("✅ CREW 3 already completed (Gate 5 approved) - SKIPPING\n")
        else:
            crew3_feedback = None
            
            while True:
                # Check if we've hit max iterations BEFORE running crew
                if self.session.crew3_iterations >= max_iterations:
                    print(f"\n🛑 Max iterations ({max_iterations}) reached at Gate 5 without approval")
                    return {"status": "max_iterations_gate5"}
                
                # Run CREW 3
                crew3_output = self.run_crew3(
                    generated_content=self.session.generated_content,
                    feedback=crew3_feedback
                )
                
                self.session.final_content = crew3_output["polished_content"]
                
                # GATE 5: Final Review Approval
                decision, feedback = self._get_approval(
                    gate_num=5,
                    gate_name="Final Review",
                    content=self.session.final_content
                )
                
                if decision == "reject":
                    print("\n🛑 Pipeline stopped at Gate 5")
                    return {"status": "rejected_at_gate5", "feedback": feedback}
                elif decision in ["edit", "feedback"]:
                    crew3_feedback = feedback
                    continue
                else:
                    self.session.gate5_approved = True
                    self.session.save(self.output_dir)  # Save after approval
                    break
        
        # ===================================================================
        # PIPELINE COMPLETE
        # ===================================================================
        
        self.session.completed_at = datetime.now().isoformat()
        self.session.save(self.output_dir)
        
        # Show rate limiting statistics
        self.rate_limiter.stats.log_summary()
        
        print("\n" + "="*80)
        print("🎉 HITL PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*80)
        print(f"Session ID: {self.session.session_id}")
        print(f"Total CREW 1 iterations: {self.session.crew1_iterations}")
        print(f"Total CREW 2 iterations: {self.session.crew2_iterations}")
        print(f"Total CREW 3 iterations: {self.session.crew3_iterations}")
        print(f"Session saved to: {self.output_dir}/hitl_session_{self.session.session_id}.json")
        print("="*80 + "\n")
        
        return {
            "status": "completed",
            "session_id": self.session.session_id,
            "product_analysis": self.session.product_analysis,
            "persona_library": self.session.persona_library,
            "content_strategy": self.session.content_strategy,
            "generated_content": self.session.generated_content,
            "final_content": self.session.final_content
        }


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run HITL content generation pipeline with rate limiting"
    )
    parser.add_argument(
        "--input-sources",
        "-i",
        required=True,
        help="Product information (text, file path, or URL)"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="output/hitl",
        help="Output directory (default: output/hitl)"
    )
    parser.add_argument(
        "--resume",
        help="Resume existing session by ID"
    )
    
    # Rate limiting options
    parser.add_argument(
        "--rate-limit",
        type=int,
        default=50,
        help="Maximum requests per minute (default: 50 for free tier)"
    )
    parser.add_argument(
        "--request-gap",
        type=float,
        default=1.2,
        help="Minimum seconds between requests (default: 1.2)"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=5,
        help="Maximum retry attempts for rate limit errors (default: 5)"
    )
    parser.add_argument(
        "--max-api-calls",
        type=int,
        help="Maximum total API calls budget (optional)"
    )
    parser.add_argument(
        "--verbose-rate-limit",
        action="store_true",
        help="Show detailed rate limiting information"
    )
    
    args = parser.parse_args()
    
    # Read input sources
    input_sources = args.input_sources
    
    # Check if it's a file
    if Path(input_sources).exists():
        with open(input_sources) as f:
            input_sources = f.read()
    
    # Configure rate limiting
    rate_config = RateLimitConfig(
        requests_per_minute=args.rate_limit,
        min_request_gap=args.request_gap,
        max_retries=args.max_retries,
        max_api_calls=args.max_api_calls,
        verbose=args.verbose_rate_limit
    )
    
    # Create orchestrator with HITL (Human-in-the-Loop) mode ALWAYS enabled
    orchestrator = HITLOrchestrator(
        auto_approve=False,  # HITL mode - always require human approval
        output_dir=args.output_dir,
        session_id=args.resume,
        rate_limit_config=rate_config
    )
    
    # Run pipeline
    try:
        result = orchestrator.run_full_pipeline(input_sources)
        
        if result["status"] == "completed":
            print(f"\n✅ Success! Final content saved to {args.output_dir}")
            sys.exit(0)
        else:
            print(f"\n⚠️  Pipeline stopped: {result['status']}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        print(f"Session saved - resume with: --resume {orchestrator.session.session_id}")
        sys.exit(130)
    except FileNotFoundError as e:
        print(f"\n❌ File Error: {e}")
        print("   Check that the input file path is correct and the file exists")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ Validation Error: {e}")
        print("   Check your input parameters (input_sources, max_iterations)")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"\n❌ Session Load Error: {e}")
        print(f"   Session file may be corrupted: {args.resume}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        print(f"   Session ID: {orchestrator.session.session_id}")
        print(f"   Output directory: {args.output_dir}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
