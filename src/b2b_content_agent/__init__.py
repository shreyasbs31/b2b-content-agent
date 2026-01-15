"""B2B Content Agent System

A multi-agent AI system for generating B2B sales and marketing content
with Human-in-the-Loop (HITL) orchestration.

Main Components:
- CREW 1: Research & Planning (Product Analysis, Personas, Content Strategy)
- CREW 2: Content Generation (Case Studies, White Papers, Pitch Decks, Social Media)
- CREW 3: Review & Polish (QA, Brand Alignment, SEO Optimization)
- HITL Orchestration: 5-gate approval system with feedback loops

Usage:
    # Run HITL pipeline
    from b2b_content_agent.hitl_flow import HITLOrchestrator
    
    orchestrator = HITLOrchestrator(auto_approve=False)
    result = orchestrator.run_full_pipeline(
        input_sources="Product description...",
        max_iterations=3
    )

CLI Usage:
    $ hitl-run --input-sources "product.txt"
    $ hitl-run --input-sources "product.txt" --auto-approve
    $ hitl-run --resume 20251104_120000
"""

__version__ = "1.0.0"

# CREW 1: Research & Planning
from .crew import ResearchPlanningCrew

# CREW 2: Content Generation
from .content_generation_crew import ContentGenerationCrew, run_content_generation

# CREW 3: Review & Polish
from .review_polish_crew import ReviewPolishCrew, run_review_polish

# HITL Flow Orchestration
from .hitl_flow import HITLOrchestrator, HITLSession

# Rate Limiting
from .rate_limiter import (
    RateLimiter,
    RateLimitConfig,
    RateLimitStats,
    get_rate_limiter,
    reset_rate_limiter
)

# Validation & Recovery
from .validators import (
    validate_inputs,
    validate_crew1_outputs,
    InputValidationError,
    OutputValidationError
)
from .recovery import (
    run_crew_with_recovery,
    run_with_retry,
    RecoveryError
)

# CREW 1 Tools
from .tools.product_analysis_tools import (
    DocumentParserTool,
    WebScraperTool,
    ProductAnalyzerTool,
    CompetitorAnalyzerTool
)
from .tools.persona_research_tools import (
    IndustryAnalyzerTool,
    JobRoleAnalyzerTool,
    DemographicsMapperTool
)
from .tools.content_strategy_tools import (
    ContentTypeMatcherTool,
    PersonaContentMapperTool,
    StrategyTemplateGeneratorTool
)

# CREW 2 Tools
from .tools.case_study_tools import (
    StoryStructureBuilder,
    DataPointExtractor,
    QuoteGenerator,
    CaseStudyFormatter
)
from .tools.white_paper_tools import (
    ResearchSynthesizer,
    FrameworkBuilder,
    ChapterStructurer,
    WhitePaperFormatter
)
from .tools.pitch_deck_tools import (
    SlideOutlineGenerator,
    ValuePropCrafter,
    DataVisualizationMapper,
    PitchDeckFormatter
)
from .tools.social_media_tools import (
    HookGenerator,
    StoryAngleIdentifier,
    HashtagResearcher,
    SocialPostFormatter
)

# CREW 3 Tools
from .tools.qa_review_tools import (
    AccuracyChecker,
    ConsistencyValidator,
    ReadabilityAnalyzer,
    LinkValidator
)
from .tools.brand_voice_tools import (
    ToneAnalyzer,
    MessagingAligner,
    PersonaValidator,
    ComplianceChecker
)
from .tools.seo_optimization_tools import (
    KeywordOptimizer,
    MetadataGenerator,
    CTAEnhancer,
    FormatOptimizer
)

__all__ = [
    # Crews
    "ResearchPlanningCrew",
    "ContentGenerationCrew",
    "run_content_generation",
    "ReviewPolishCrew",
    "run_review_polish",
    
    # Validation & Recovery
    "validate_inputs",
    "validate_crew1_outputs",
    "InputValidationError",
    "OutputValidationError",
    "run_crew_with_recovery",
    "run_with_retry",
    "RecoveryError",
    
    # CREW 1 Tools
    "DocumentParserTool",
    "WebScraperTool",
    "ProductAnalyzerTool",
    "CompetitorAnalyzerTool",
    "IndustryAnalyzerTool",
    "JobRoleAnalyzerTool",
    "DemographicsMapperTool",
    "ContentTypeMatcherTool",
    "PersonaContentMapperTool",
    "StrategyTemplateGeneratorTool",
    
    # CREW 2 Tools
    "StoryStructureBuilder",
    "DataPointExtractor",
    "QuoteGenerator",
    "CaseStudyFormatter",
    "ResearchSynthesizer",
    "FrameworkBuilder",
    "ChapterStructurer",
    "WhitePaperFormatter",
    "SlideOutlineGenerator",
    "ValuePropCrafter",
    "DataVisualizationMapper",
    "PitchDeckFormatter",
    "HookGenerator",
    "StoryAngleIdentifier",
    "HashtagResearcher",
    "SocialPostFormatter",
    
    # CREW 3 Tools
    "AccuracyChecker",
    "ConsistencyValidator",
    "ReadabilityAnalyzer",
    "LinkValidator",
    "ToneAnalyzer",
    "MessagingAligner",
    "PersonaValidator",
    "ComplianceChecker",
    "KeywordOptimizer",
    "MetadataGenerator",
    "CTAEnhancer",
    "FormatOptimizer",
]
