"""CREW 1: Research & Planning Crew

This crew handles the initial research and planning phase with 3 specialized agents:
1. Product Analyst - Extracts and analyzes product information
2. Persona Researcher - Identifies and profiles target personas
3. Content Strategist - Creates content strategy and assignments
"""

import os
from typing import List
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from b2b_content_agent.llm_manager import get_llm_manager
from b2b_content_agent.tools import (
    # Product Analysis Tools (Agent #1)
    DocumentParserTool,
    WebScraperTool,
    ProductAnalyzerTool,
    CompetitorAnalyzerTool,
    # Persona Research Tools (Agent #2)
    IndustryAnalyzerTool,
    JobRoleAnalyzerTool,
    DemographicsMapperTool,
    # Content Strategy Tools (Agent #3)
    ContentTypeMatcherTool,
    PersonaContentMapperTool,
    StrategyTemplateGeneratorTool,
)


@CrewBase
class ResearchPlanningCrew:
    """Research & Planning Crew for B2B content generation.
    
    This crew analyzes product information, identifies target personas,
    and creates a comprehensive content strategy.
    """
    
    agents_config = "config/crew1_agents.yaml"
    tasks_config = "config/crew1_tasks.yaml"
    
    # Initialize tools for Agent #1: Product Analyst
    document_parser = DocumentParserTool()
    web_scraper = WebScraperTool()
    product_analyzer = ProductAnalyzerTool()
    competitor_analyzer = CompetitorAnalyzerTool()
    
    # Initialize tools for Agent #2: Persona Researcher
    industry_analyzer = IndustryAnalyzerTool()
    job_role_analyzer = JobRoleAnalyzerTool()
    demographics_mapper = DemographicsMapperTool()
    
    # Initialize tools for Agent #3: Content Strategist
    content_type_matcher = ContentTypeMatcherTool()
    persona_content_mapper = PersonaContentMapperTool()
    strategy_template_generator = StrategyTemplateGeneratorTool()
    
    # Initialize LLM manager for multi-provider support with fallback
    _llm_manager = None
    
    @property
    def llm_manager(self):
        """Get the global LLM manager instance."""
        if self._llm_manager is None:
            self._llm_manager = get_llm_manager()
        return self._llm_manager
    
    @property
    def llm_pro(self):
        """Smart LLM - Use for complex reasoning, strategy, and analysis."""
        return self.llm_manager.get_llm("pro", temperature=0.7)
    
    @property
    def llm_flash(self):
        """Fast LLM - Use for structured extraction and generation."""
        return self.llm_manager.get_llm("flash", temperature=0.7)
    
    @agent
    def product_analyst(self) -> Agent:
        """Create the Product Analyst agent with comprehensive analysis tools.
        
        Uses Gemini 2.0 Flash - optimized for structured data extraction.
        """
        config = self.agents_config['product_analyst'].copy()
        return Agent(
            **config,
            llm=self.llm_flash,  # Use Flash for extraction tasks
            tools=[
                self.document_parser,
                self.web_scraper,
                self.product_analyzer,
                self.competitor_analyzer,
            ],
        )
    
    @agent
    def persona_researcher(self) -> Agent:
        """Create the Persona Researcher agent for identifying target personas.
        
        Uses Gemini 2.5 Flash - TEMPORARY: Switched from Pro due to 503 errors.
        Flash is sufficient for persona generation and more reliable.
        """
        config = self.agents_config['persona_researcher'].copy()
        return Agent(
            **config,
            llm=self.llm_flash,  # Use Flash for persona creation (switched from Pro due to 503)
            tools=[
                self.industry_analyzer,
                self.job_role_analyzer,
                self.demographics_mapper,
            ],
        )
    
    @agent
    def content_strategist(self) -> Agent:
        """Create the Content Strategist agent for planning content generation.
        
        Uses Gemini 2.5 Flash - TEMPORARY: Switched from Pro due to 503 errors.
        Flash is sufficient for strategic planning and more reliable.
        
        MAX_ITER set to 15 to prevent infinite tool calling loops.
        """
        config = self.agents_config['content_strategist'].copy()
        return Agent(
            **config,
            llm=self.llm_flash,  # Use Flash for strategic planning (switched from Pro due to 503)
            tools=[
                self.content_type_matcher,
                self.persona_content_mapper,
                self.strategy_template_generator,
            ],
            max_iter=15,  # Prevent infinite loops - force completion after 15 tool calls
        )
    
    @task
    def product_analysis_task(self) -> Task:
        """Task for comprehensive product analysis."""
        return Task(
            config=self.tasks_config['product_analysis_task'],
            agent=self.product_analyst(),
        )
    
    @task
    def persona_identification_task(self) -> Task:
        """Task for identifying and profiling target personas."""
        return Task(
            config=self.tasks_config['persona_identification_task'],
            agent=self.persona_researcher(),
        )
    
    @task
    def content_strategy_task(self) -> Task:
        """Task for creating comprehensive content strategy."""
        return Task(
            config=self.tasks_config['content_strategy_task'],
            agent=self.content_strategist(),
        )
    
    @crew
    def crew(self) -> Crew:
        """Assemble the Research & Planning Crew.
        
        This crew runs in SEQUENTIAL process due to dependencies:
        1. Product Analyst analyzes product information
        2. Persona Researcher identifies target personas (needs #1 output)
        3. Content Strategist creates content plan (needs #1 and #2 output)
        
        ⚠️ CANNOT USE PARALLEL: Each agent depends on previous agent's output.
        
        📝 For future crews (CREW 2, CREW 3):
        - Use Process.hierarchical for parallel execution where tasks are independent
        - Example: Multiple writers in CREW 2 can work on different content pieces simultaneously
        - Example: Multiple reviewers in CREW 3 can review different content types in parallel
        
        🚀 OPTIMIZATION APPLIED:
        - Agent #1: Gemini 2.5 Flash (fast extraction, ~3-5x faster)
        - Agent #2: Gemini 2.5 Pro (deep persona creation, quality preserved)
        - Agent #3: Gemini 2.5 Pro (strategic planning, quality preserved)
        
        Each agent builds on the work of the previous agent.
        """
        return Crew(
            agents=self.agents,  # Automatically created by @agent decorator
            tasks=self.tasks,    # Automatically created by @task decorator
            process=Process.sequential,
            verbose=False,  # Changed to False to prevent overwhelming terminal output
        )
