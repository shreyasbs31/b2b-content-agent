"""Content Generation Crew (CREW 2)

This crew handles sequential content generation using 4 specialized writer agents:
- Agent #4: Case Study Writer
- Agent #5: White Paper Author
- Agent #6: Pitch Deck Designer
- Agent #7: Social Media Specialist

Uses Process.sequential for reliable execution with rate limit management.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import Dict, Any
import os

from b2b_content_agent.llm_manager import get_llm_manager
# Import CREW 2 tools
from b2b_content_agent.tools.case_study_tools import (
    StoryStructureBuilder,
    DataPointExtractor,
    QuoteGenerator,
    CaseStudyFormatter
)
from b2b_content_agent.tools.white_paper_tools import (
    ResearchSynthesizer,
    FrameworkBuilder,
    ChapterStructurer,
    WhitePaperFormatter
)
from b2b_content_agent.tools.pitch_deck_tools import (
    SlideOutlineGenerator,
    ValuePropCrafter,
    DataVisualizationMapper,
    PitchDeckFormatter
)
from b2b_content_agent.tools.social_media_tools import (
    HookGenerator,
    StoryAngleIdentifier,
    HashtagResearcher,
    SocialPostFormatter
)


@CrewBase
class ContentGenerationCrew:
    """CREW 2: Content Generation with sequential execution.
    
    Takes outputs from CREW 1 (product analysis, personas, content strategy)
    and generates 4 types of content sequentially:
    - Case studies (1,500-2,500 words)
    - White papers (3,000-5,000 words)
    - Pitch decks (10-15 slides)
    - Social media posts (5-10 per persona)
    
    Uses sequential process for reliable execution with rate limit management.
    """
    
    agents_config = 'config/crew2_agents.yaml'
    tasks_config = 'config/crew2_tasks.yaml'
    
    def __init__(self):
        """Initialize the crew with LLM manager for multi-provider support."""
        # Initialize LLM manager
        self.llm_manager = get_llm_manager()
        
        # All agents use flash model (fast, reliable)
        self.llm_flash = self.llm_manager.get_llm("flash", temperature=0.7)
    
    # =====================================================
    # AGENT DEFINITIONS (4 Writer Agents)
    # =====================================================
    
    @agent
    def case_study_writer(self) -> Agent:
        """Agent #4: Case Study Content Specialist.
        
        Creates compelling B2B case studies with quantifiable results.
        """
        config = self.agents_config['case_study_writer']
        
        return Agent(
            config=config,
            tools=[
                StoryStructureBuilder(),
                DataPointExtractor(),
                QuoteGenerator(),
                CaseStudyFormatter()
            ],
            llm=self.llm_flash,
            verbose=False,
            allow_delegation=False
        )
    
    @agent
    def white_paper_author(self) -> Agent:
        """Agent #5: Thought Leadership Content Author.
        
        Writes authoritative white papers with frameworks and best practices.
        """
        config = self.agents_config['white_paper_author']
        
        return Agent(
            config=config,
            tools=[
                ResearchSynthesizer(),
                FrameworkBuilder(),
                ChapterStructurer(),
                WhitePaperFormatter()
            ],
            llm=self.llm_flash,
            verbose=False,
            allow_delegation=False
        )
    
    @agent
    def pitch_deck_designer(self) -> Agent:
        """Agent #6: Sales Pitch Deck Content Architect.
        
        Designs compelling pitch decks with slide-by-slide content.
        """
        config = self.agents_config['pitch_deck_designer']
        
        return Agent(
            config=config,
            tools=[
                SlideOutlineGenerator(),
                ValuePropCrafter(),
                DataVisualizationMapper(),
                PitchDeckFormatter()
            ],
            llm=self.llm_flash,
            verbose=False,
            allow_delegation=False
        )
    
    @agent
    def social_media_specialist(self) -> Agent:
        """Agent #7: B2B Social Media Content Strategist.
        
        Creates engaging social media content tailored to each persona.
        """
        config = self.agents_config['social_media_specialist']
        
        return Agent(
            config=config,
            tools=[
                HookGenerator(),
                StoryAngleIdentifier(),
                HashtagResearcher(),
                SocialPostFormatter()
            ],
            llm=self.llm_flash,
            verbose=False,
            allow_delegation=False
        )
    
    # =====================================================
    # TASK DEFINITIONS (4 Parallel Tasks)
    # =====================================================
    
    @task
    def case_study_generation_task(self) -> Task:
        """Task #4: Generate compelling case studies.
        
        Creates 2-3 case studies per persona with realistic metrics.
        """
        config = self.tasks_config['case_study_generation_task']
        
        return Task(
            config=config,
            agent=self.case_study_writer()
        )
    
    @task
    def white_paper_generation_task(self) -> Task:
        """Task #5: Generate thought leadership white papers.
        
        Creates 1-2 white papers addressing key industry challenges.
        """
        config = self.tasks_config['white_paper_generation_task']
        
        return Task(
            config=config,
            agent=self.white_paper_author()
        )
    
    @task
    def pitch_deck_generation_task(self) -> Task:
        """Task #6: Generate sales pitch decks.
        
        Creates 1-2 pitch decks targeting different personas.
        """
        config = self.tasks_config['pitch_deck_generation_task']
        
        return Task(
            config=config,
            agent=self.pitch_deck_designer()
        )
    
    @task
    def social_media_generation_task(self) -> Task:
        """Task #7: Generate social media content.
        
        Creates 5-10 social posts per persona for LinkedIn/Twitter.
        """
        config = self.tasks_config['social_media_generation_task']
        
        return Task(
            config=config,
            agent=self.social_media_specialist()
        )
    
    # =====================================================
    # CREW DEFINITION
    # =====================================================
    
    @crew
    def crew(self) -> Crew:
        """Creates the Content Generation Crew.
        
        Uses Process.sequential to run tasks one after another.
        All 4 agents generate content sequentially.
        
        Expected execution time: 40-60 minutes (sequential processing)
        """
        return Crew(
            agents=self.agents,  # All 4 writer agents
            tasks=self.tasks,    # All 4 generation tasks (sequential)
            process=Process.sequential,
            verbose=False,
            memory=False,  # Will add mem0 integration later
            full_output=True,
        )


def run_content_generation(
    product_analysis: str,
    persona_library: str,
    content_strategy: str,
    output_dir: str = "content_output"
) -> Dict[str, Any]:
    """
    Run CREW 2 (Content Generation) with outputs from CREW 1.
    
    Args:
        product_analysis: Output from CREW 1 Agent #1
        persona_library: Output from CREW 1 Agent #2
        content_strategy: Output from CREW 1 Agent #3
        output_dir: Directory to save generated content
        
    Returns:
        Dictionary containing all generated content:
        - case_studies: List of case studies
        - white_papers: List of white papers
        - pitch_decks: List of pitch decks
        - social_posts: List of social media posts
        
    Example:
        >>> from b2b_content_agent.content_generation_crew import run_content_generation
        >>> 
        >>> result = run_content_generation(
        ...     product_analysis=crew1_output['product_analysis'],
        ...     persona_library=crew1_output['persona_library'],
        ...     content_strategy=crew1_output['content_strategy']
        ... )
        >>> 
        >>> print(f"Generated {len(result['case_studies'])} case studies")
        >>> print(f"Generated {len(result['white_papers'])} white papers")
        >>> print(f"Generated {len(result['pitch_decks'])} pitch decks")
        >>> print(f"Generated {len(result['social_posts'])} social posts")
    """
    import os
    from datetime import datetime
    
    print("\n" + "="*80)
    print("CREW 2: CONTENT GENERATION")
    print("="*80)
    print(f"\nStarting sequential content generation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nProcessing Mode: Sequential (4 agents one after another)")
    print(f"Expected Duration: 40-60 minutes")
    print("\nGenerating:")
    print("  - Case Studies (Agent #4)")
    print("  - White Papers (Agent #5)")
    print("  - Pitch Decks (Agent #6)")
    print("  - Social Media Posts (Agent #7)")
    print("\n" + "-"*80 + "\n")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Initialize crew
    crew = ContentGenerationCrew().crew()
    
    # Prepare inputs for all tasks
    inputs = {
        'product_analysis': product_analysis,
        'persona_library': persona_library,
        'content_strategy': content_strategy
    }
    
    # Run crew with sequential execution
    print("\n🚀 Starting sequential content generation...")
    print("⏱️  This typically takes 40-60 minutes with 4 agents running one after another\n")
    
    try:
        result = crew.kickoff(inputs=inputs)
        
        print("\n" + "="*80)
        print("✅ CONTENT GENERATION COMPLETE")
        print("="*80)
        
        # Parse results (hierarchical process returns combined output)
        output = {
            'case_studies': result.get('case_study_generation_task', ''),
            'white_papers': result.get('white_paper_generation_task', ''),
            'pitch_decks': result.get('pitch_deck_generation_task', ''),
            'social_posts': result.get('social_media_generation_task', ''),
            'timestamp': timestamp,
            'execution_time': result.get('execution_time', 'N/A')
        }
        
        # Save individual outputs
        for content_type, content in output.items():
            if content_type not in ['timestamp', 'execution_time']:
                filename = f"{output_dir}/{content_type}_{timestamp}.txt"
                with open(filename, 'w') as f:
                    f.write(str(content))
                print(f"  ✓ {content_type}: {filename}")
        
        print(f"\nAll content saved to: {output_dir}/")
        print(f"Execution time: {output.get('execution_time', 'N/A')}")
        print("\n" + "="*80 + "\n")
        
        return output
        
    except Exception as e:
        print(f"\n❌ Error during content generation: {str(e)}")
        print("\nPartial results may have been saved.")
        raise


if __name__ == "__main__":
    """Test the Content Generation Crew"""
    print("Content Generation Crew initialized successfully!")
    print("\nTo use this crew, call run_content_generation() with CREW 1 outputs:")
    print("  - product_analysis")
    print("  - persona_library")
    print("  - content_strategy")
