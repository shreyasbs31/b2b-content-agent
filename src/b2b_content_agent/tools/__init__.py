"""Tools package for B2B Content Agent System."""

from .product_analysis_tools import (
    DocumentParserTool,
    WebScraperTool,
    ProductAnalyzerTool,
    CompetitorAnalyzerTool,
)

from .persona_research_tools import (
    IndustryAnalyzerTool,
    JobRoleAnalyzerTool,
    DemographicsMapperTool,
)

from .content_strategy_tools import (
    ContentTypeMatcherTool,
    PersonaContentMapperTool,
    StrategyTemplateGeneratorTool,
)

__all__ = [
    # Product Analysis Tools (Agent #1)
    "DocumentParserTool",
    "WebScraperTool",
    "ProductAnalyzerTool",
    "CompetitorAnalyzerTool",
    # Persona Research Tools (Agent #2)
    "IndustryAnalyzerTool",
    "JobRoleAnalyzerTool",
    "DemographicsMapperTool",
    # Content Strategy Tools (Agent #3)
    "ContentTypeMatcherTool",
    "PersonaContentMapperTool",
    "StrategyTemplateGeneratorTool",
]
