"""Minimal real tests - tiny inputs, real LLM calls

This test runs the crews with absolute minimal input to validate
the system works without waiting 90+ minutes.

Expected time: 2-5 minutes per crew
"""

import os
import sys
from pathlib import Path
import time

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

# Ensure we have API key
if not os.getenv("GOOGLE_API_KEY"):
    print("❌ ERROR: GOOGLE_API_KEY environment variable not set")
    print("Please set your API key in .env file or: export GOOGLE_API_KEY='your-key-here'")
    sys.exit(1)


def test_crew1_minimal():
    """Test CREW 1 with absolute minimal input
    
    Target: 2-3 minutes (vs 30-40 minutes full run)
    """
    
    print("\n" + "="*70)
    print("🧪 MINIMAL CREW 1 TEST")
    print("="*70)
    print("⏱️  Expected time: 2-3 minutes")
    print("📝 Testing: Research & Planning Crew")
    print("🎯 Strategy: Minimal input (1 sentence, 1 persona)")
    print("="*70 + "\n")
    
    from b2b_content_agent.crew import ResearchPlanningCrew
    
    # Minimal product description (1 sentence!)
    minimal_input = {
        "product_name": "TestAI",
        "product_description": "AI assistant for sales teams that automates follow-ups.",
        "target_content_type": "case_study",
        "input_sources": "Product: TestAI - AI assistant for sales teams that automates follow-ups and improves productivity."
    }
    
    crew = ResearchPlanningCrew()
    
    start_time = time.time()
    
    try:
        print("🚀 Starting CREW 1...")
        result = crew.crew().kickoff(inputs=minimal_input)
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*70)
        print(f"✅ CREW 1 MINIMAL TEST PASSED")
        print(f"⏱️  Time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print("="*70)
        
        # Print summary of result
        print("\n📊 Result Summary:")
        print("-" * 70)
        if hasattr(result, 'raw'):
            result_text = str(result.raw)[:500]  # First 500 chars
            print(result_text)
            if len(str(result.raw)) > 500:
                print("\n... (truncated)")
        else:
            result_text = str(result)[:500]
            print(result_text)
            if len(str(result)) > 500:
                print("\n... (truncated)")
        
        return True, elapsed, result
        
    except Exception as e:
        elapsed = time.time() - start_time
        
        print("\n" + "="*70)
        print(f"❌ CREW 1 MINIMAL TEST FAILED")
        print(f"⏱️  Time before failure: {elapsed:.1f} seconds")
        print(f"❗ Error: {e}")
        print("="*70)
        
        import traceback
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        
        return False, elapsed, None


def test_crew2_minimal(crew1_result=None):
    """Test CREW 2 with minimal input
    
    Target: 3-5 minutes (vs 40-60 minutes full run)
    """
    
    print("\n" + "="*70)
    print("🧪 MINIMAL CREW 2 TEST")
    print("="*70)
    print("⏱️  Expected time: 3-5 minutes")
    print("📝 Testing: Content Generation Crew")
    print("🎯 Strategy: 300-word case study (vs 2000+ words)")
    print("="*70 + "\n")
    
    from b2b_content_agent.content_generation_crew import ContentGenerationCrew
    
    # Use CREW 1 result if available, otherwise use defaults
    if crew1_result:
        result_str = str(crew1_result.raw if hasattr(crew1_result, 'raw') else crew1_result)
        persona_profile = result_str
        content_strategy = "Write one short case study showcasing ROI."
        product_analysis = result_str
    else:
        persona_profile = "VP of Sales at mid-size B2B SaaS company. Wants to improve team productivity and close rates."
        content_strategy = "Write one 300-word case study showing how TestAI helps sales teams."
        product_analysis = "TestAI is an AI assistant that automates follow-ups for sales teams."
    
    minimal_input = {
        "persona_profile": persona_profile,
        "content_strategy": content_strategy,
        "product_analysis": product_analysis,
        "content_type": "case_study",
        "word_count_target": 300  # Super short!
    }
    
    crew = ContentGenerationCrew()
    
    start_time = time.time()
    
    try:
        print("🚀 Starting CREW 2...")
        result = crew.crew().kickoff(inputs=minimal_input)
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*70)
        print(f"✅ CREW 2 MINIMAL TEST PASSED")
        print(f"⏱️  Time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print("="*70)
        
        # Print summary of result
        print("\n📊 Result Summary:")
        print("-" * 70)
        if hasattr(result, 'raw'):
            result_text = str(result.raw)[:500]
            print(result_text)
            if len(str(result.raw)) > 500:
                print("\n... (truncated)")
        else:
            result_text = str(result)[:500]
            print(result_text)
            if len(str(result)) > 500:
                print("\n... (truncated)")
        
        return True, elapsed, result
        
    except Exception as e:
        elapsed = time.time() - start_time
        
        print("\n" + "="*70)
        print(f"❌ CREW 2 MINIMAL TEST FAILED")
        print(f"⏱️  Time before failure: {elapsed:.1f} seconds")
        print(f"❗ Error: {e}")
        print("="*70)
        
        import traceback
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        
        return False, elapsed, None


def test_crew3_minimal(crew2_result=None):
    """Test CREW 3 with minimal input
    
    Target: 2-3 minutes (vs 15-20 minutes full run)
    """
    
    print("\n" + "="*70)
    print("🧪 MINIMAL CREW 3 TEST")
    print("="*70)
    print("⏱️  Expected time: 2-3 minutes")
    print("📝 Testing: Review & Polish Crew")
    print("🎯 Strategy: Quick review of short content")
    print("="*70 + "\n")
    
    from b2b_content_agent.review_polish_crew import ReviewPolishCrew
    
    # Use CREW 2 result if available, otherwise use sample
    if crew2_result:
        content = str(crew2_result.raw if hasattr(crew2_result, 'raw') else crew2_result)
    else:
        content = """
        Case Study: How TestAI Helped SalesForce Inc. Increase Close Rates by 35%
        
        SalesForce Inc., a mid-size B2B SaaS company, struggled with follow-up consistency.
        Their sales team of 25 reps was missing opportunities due to manual processes.
        
        After implementing TestAI's automated follow-up system, they saw:
        - 35% increase in close rates
        - 50% reduction in follow-up time
        - 2x more qualified meetings booked
        
        "TestAI transformed how we work," says John Smith, VP of Sales.
        """
    
    minimal_input = {
        "content": content,
        "content_type": "case_study",
        "target_keywords": "sales, productivity, automation, ROI",
        "brand_guidelines": "Professional, data-driven, concise"
    }
    
    crew = ReviewPolishCrew()
    
    start_time = time.time()
    
    try:
        print("🚀 Starting CREW 3...")
        result = crew.crew().kickoff(inputs=minimal_input)
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*70)
        print(f"✅ CREW 3 MINIMAL TEST PASSED")
        print(f"⏱️  Time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print("="*70)
        
        # Print summary of result
        print("\n📊 Result Summary:")
        print("-" * 70)
        if hasattr(result, 'raw'):
            result_text = str(result.raw)[:500]
            print(result_text)
            if len(str(result.raw)) > 500:
                print("\n... (truncated)")
        else:
            result_text = str(result)[:500]
            print(result_text)
            if len(str(result)) > 500:
                print("\n... (truncated)")
        
        return True, elapsed, result
        
    except Exception as e:
        elapsed = time.time() - start_time
        
        print("\n" + "="*70)
        print(f"❌ CREW 3 MINIMAL TEST FAILED")
        print(f"⏱️  Time before failure: {elapsed:.1f} seconds")
        print(f"❗ Error: {e}")
        print("="*70)
        
        import traceback
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        
        return False, elapsed, None


def main():
    """Run all minimal tests"""
    
    print("\n" + "="*70)
    print("🚀 MINIMAL INTEGRATION TEST SUITE")
    print("="*70)
    print("📋 Testing all 3 crews with minimal inputs")
    print("⏱️  Expected total time: 7-11 minutes (vs 90+ minutes)")
    print("💰 Cost: ~$0.05 (vs ~$0.50 for full runs)")
    print("="*70)
    
    total_start = time.time()
    results = {}
    
    # Test CREW 1
    print("\n" + "🔵"*35)
    crew1_passed, crew1_time, crew1_result = test_crew1_minimal()
    results['crew1'] = {'passed': crew1_passed, 'time': crew1_time}
    
    # Test CREW 2 (use CREW 1 output if available)
    if crew1_passed:
        print("\n" + "🔵"*35)
        crew2_passed, crew2_time, crew2_result = test_crew2_minimal(crew1_result)
        results['crew2'] = {'passed': crew2_passed, 'time': crew2_time}
    else:
        print("\n⚠️  Skipping CREW 2 (CREW 1 failed)")
        crew2_passed = False
        crew2_result = None
        results['crew2'] = {'passed': False, 'time': 0, 'skipped': True}
    
    # Test CREW 3 (use CREW 2 output if available)
    if crew2_passed:
        print("\n" + "🔵"*35)
        crew3_passed, crew3_time, crew3_result = test_crew3_minimal(crew2_result)
        results['crew3'] = {'passed': crew3_passed, 'time': crew3_time}
    else:
        print("\n⚠️  Skipping CREW 3 (CREW 2 failed)")
        results['crew3'] = {'passed': False, 'time': 0, 'skipped': True}
    
    # Final summary
    total_time = time.time() - total_start
    
    print("\n\n" + "="*70)
    print("📊 FINAL RESULTS")
    print("="*70)
    
    for crew_name, result in results.items():
        status = "✅ PASSED" if result['passed'] else ("⏭️  SKIPPED" if result.get('skipped') else "❌ FAILED")
        time_str = f"{result['time']:.1f}s ({result['time']/60:.1f}m)" if result['time'] > 0 else "N/A"
        print(f"{crew_name.upper():8} {status:12} Time: {time_str}")
    
    print("-" * 70)
    print(f"TOTAL    Time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    
    all_passed = all(r['passed'] for r in results.values())
    
    print("="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED - System validated!")
        print("🎉 You can now build HITL with confidence")
    else:
        failed_crews = [name.upper() for name, r in results.items() if not r['passed'] and not r.get('skipped')]
        print(f"❌ SOME TESTS FAILED: {', '.join(failed_crews)}")
        print("🔧 Fix issues before proceeding to HITL")
    print("="*70 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
