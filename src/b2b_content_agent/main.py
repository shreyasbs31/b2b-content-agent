"""B2B Content Agent System - Research & Planning Module

Main entry point for running the Research & Planning Crew (CREW 1).
"""

import sys
from pathlib import Path

from b2b_content_agent.crew import ResearchPlanningCrew


def run():
    """
    Run the Research & Planning Crew.
    
    This crew will:
    1. Analyze product information from provided sources
    2. Identify and profile target personas (10-50 personas)
    3. Create a comprehensive content strategy with assignments
    """
    
    # Example inputs - this will be customized based on user input
    inputs = {
        'input_sources': '''
        Please analyze the following product information:
        
        [PLACEHOLDER - User will provide:
         - File paths to documents (PDF, DOCX, TXT)
         - URLs to product website/docs
         - Raw text description of the product]
        
        For testing, you can provide product information directly here.
        '''
    }
    
    print("\n" + "="*70)
    print("🚀 B2B CONTENT AGENT SYSTEM - CREW 1: Research & Planning")
    print("="*70 + "\n")
    
    print("📋 CREW 1 will execute the following tasks:")
    print("  1. Product Analysis (Product Analyst Agent)")
    print("  2. Persona Identification (Persona Researcher Agent)")
    print("  3. Content Strategy Development (Content Strategist Agent)")
    print("\n" + "-"*70 + "\n")
    
    try:
        # Initialize and run the crew
        crew = ResearchPlanningCrew().crew()
        result = crew.kickoff(inputs=inputs)
        
        print("\n" + "="*70)
        print("✅ CREW 1 COMPLETE - Research & Planning Phase Finished!")
        print("="*70 + "\n")
        
        print("📁 Output files generated:")
        print("  - output/01_product_analysis.md")
        print("  - output/02_persona_library.md")
        print("  - output/03_content_strategy.md")
        print("\n")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error running CREW 1: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point."""
    run()


if __name__ == "__main__":
    main()
