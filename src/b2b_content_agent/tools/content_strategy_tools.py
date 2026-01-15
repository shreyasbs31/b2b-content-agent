"""Content Strategy Tools for B2B Content Agent System.

Tools for Agent #3 (Content Strategist) to map personas to content types,
generate content briefs, and create comprehensive content strategies.
"""

from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import json


# ============================================================================
# PYDANTIC MODELS FOR STRUCTURED DATA
# ============================================================================

class ContentTypeRecommendation(BaseModel):
    """Recommendation for a specific content type."""
    content_type: str = Field(description="Type of content (e.g., Case Study, White Paper)")
    suitability_score: int = Field(description="How suitable this content type is (1-10)")
    reasoning: str = Field(description="Why this content type fits")
    key_elements: List[str] = Field(description="Essential elements to include")
    typical_length: str = Field(description="Expected length/format")


class PersonaContentMapping(BaseModel):
    """Mapping of a persona to recommended content types."""
    persona_title: str = Field(description="Job title of the persona")
    persona_segment: str = Field(description="Demographic segment")
    primary_content_type: str = Field(description="Best content type for this persona")
    secondary_content_types: List[str] = Field(description="Alternative content types")
    content_focus: str = Field(description="What the content should emphasize")
    tone_and_style: str = Field(description="Appropriate tone for this persona")
    distribution_channels: List[str] = Field(description="Where to distribute")


class ContentBrief(BaseModel):
    """Detailed brief for a specific piece of content."""
    content_id: str = Field(description="Unique identifier")
    content_type: str = Field(description="Type (Case Study, White Paper, etc.)")
    target_persona: str = Field(description="Primary persona this targets")
    title_suggestion: str = Field(description="Suggested title")
    key_messages: List[str] = Field(description="Core messages to convey")
    pain_points_addressed: List[str] = Field(description="Persona pain points to address")
    proof_points: List[str] = Field(description="Evidence/data points to include")
    cta: str = Field(description="Call-to-action")
    success_metrics: List[str] = Field(description="How to measure success")


# ============================================================================
# TOOL 1: CONTENT TYPE MATCHER
# ============================================================================

class ContentTypeMatcherToolInput(BaseModel):
    """Input schema for ContentTypeMatcherTool."""
    persona_profile: str = Field(
        description="Detailed persona profile including role, goals, pain points, buying influence"
    )
    sales_stage: str = Field(
        description="Sales stage this persona is typically at (Awareness/Consideration/Decision)"
    )


class ContentTypeMatcherTool(BaseTool):
    """Matches personas to the most effective content types.
    
    This tool analyzes persona characteristics and recommends which content
    formats will resonate best based on:
    - Seniority level and buying influence
    - Industry and company size
    - Stage in buyer journey
    - Typical content consumption patterns
    
    Returns ranked recommendations for:
    - Case Studies
    - White Papers
    - Pitch Decks
    - Social Media content
    - Other relevant formats
    """
    
    name: str = "Content Type Matcher"
    description: str = (
        "Recommends the best content types for a given persona. Analyzes persona "
        "characteristics and returns ranked content type recommendations with reasoning, "
        "key elements, and format guidelines. Use this to determine what content to create "
        "for each persona."
    )
    args_schema: Type[BaseModel] = ContentTypeMatcherToolInput
    
    def _run(self, persona_profile: str, sales_stage: str) -> str:
        """Match content types to persona."""
        
        profile_lower = persona_profile.lower()
        stage_lower = sales_stage.lower()
        
        # Content type definitions with targeting rules
        content_types = {
            "Case Study": {
                "best_for": ["decision-maker", "influencer", "senior", "vp", "director", "consideration", "decision"],
                "description": "Real customer success story with quantifiable results",
                "suitability_factors": {
                    "executive": 9,
                    "senior": 9,
                    "mid": 7,
                    "consideration": 10,
                    "decision": 10,
                },
                "key_elements": [
                    "Customer profile and challenges",
                    "Solution implementation details",
                    "Quantifiable results and ROI",
                    "Customer quote/testimonial",
                    "Before/after comparison"
                ],
                "typical_length": "1,500-2,500 words, 3-4 pages PDF",
                "tone": "Professional, data-driven, credible"
            },
            "White Paper": {
                "best_for": ["technical", "research", "evaluation", "decision-maker", "consideration", "analyst"],
                "description": "In-depth analysis of industry challenge or solution approach",
                "suitability_factors": {
                    "executive": 7,
                    "senior": 9,
                    "mid": 8,
                    "consideration": 10,
                    "decision": 8,
                },
                "key_elements": [
                    "Industry problem statement",
                    "Research and data",
                    "Solution methodology",
                    "Best practices and frameworks",
                    "Implementation roadmap"
                ],
                "typical_length": "3,000-5,000 words, 8-12 pages PDF",
                "tone": "Authoritative, educational, thought leadership"
            },
            "Pitch Deck": {
                "best_for": ["executive", "ceo", "cfo", "decision-maker", "fast-paced", "decision", "awareness"],
                "description": "Visual presentation of value proposition and ROI",
                "suitability_factors": {
                    "executive": 10,
                    "senior": 8,
                    "mid": 6,
                    "awareness": 8,
                    "decision": 9,
                },
                "key_elements": [
                    "Problem statement (1-2 slides)",
                    "Solution overview (2-3 slides)",
                    "Key benefits and ROI (2-3 slides)",
                    "Customer proof points (1-2 slides)",
                    "Pricing and next steps (1-2 slides)"
                ],
                "typical_length": "10-15 slides, designed for 15-20 min presentation",
                "tone": "Compelling, concise, visual-first"
            },
            "LinkedIn Post": {
                "best_for": ["awareness", "thought leadership", "networking", "all", "social"],
                "description": "Professional social media content for B2B audience",
                "suitability_factors": {
                    "executive": 8,
                    "senior": 9,
                    "mid": 9,
                    "awareness": 10,
                    "consideration": 7,
                },
                "key_elements": [
                    "Hook/attention grabber",
                    "Key insight or stat",
                    "Brief explanation/story",
                    "Call-to-action",
                    "Relevant hashtags"
                ],
                "typical_length": "150-300 words, 1-3 paragraphs",
                "tone": "Conversational, authentic, value-driven"
            },
            "Twitter/X Thread": {
                "best_for": ["awareness", "tech", "startup", "fast-paced", "social", "developer"],
                "description": "Multi-post thread breaking down concepts or insights",
                "suitability_factors": {
                    "executive": 6,
                    "senior": 7,
                    "mid": 8,
                    "awareness": 9,
                    "tech": 10,
                },
                "key_elements": [
                    "Strong opening hook",
                    "Numbered insights/tips",
                    "Actionable takeaways",
                    "Thread conclusion with CTA",
                    "Visual elements (images/charts)"
                ],
                "typical_length": "5-10 tweets, 280 characters each",
                "tone": "Punchy, direct, insightful"
            },
            "Email Nurture Sequence": {
                "best_for": ["consideration", "nurture", "mid", "senior", "education"],
                "description": "Series of educational emails building toward conversion",
                "suitability_factors": {
                    "executive": 7,
                    "senior": 8,
                    "mid": 9,
                    "consideration": 10,
                    "decision": 7,
                },
                "key_elements": [
                    "Welcome/introduction email",
                    "Educational content emails (3-4)",
                    "Case study/social proof email",
                    "Demo/trial invitation email",
                    "Follow-up/urgency email"
                ],
                "typical_length": "5-7 email sequence, 200-400 words each",
                "tone": "Helpful, educational, gradually persuasive"
            },
            "Product Comparison Guide": {
                "best_for": ["decision", "evaluation", "technical", "analyst", "procurement"],
                "description": "Side-by-side comparison with competitors",
                "suitability_factors": {
                    "executive": 7,
                    "senior": 9,
                    "mid": 9,
                    "decision": 10,
                    "consideration": 9,
                },
                "key_elements": [
                    "Feature comparison matrix",
                    "Pricing comparison",
                    "Use case fit analysis",
                    "Customer support comparison",
                    "Implementation comparison"
                ],
                "typical_length": "2,000-3,000 words, interactive table/PDF",
                "tone": "Objective, fact-based, detailed"
            },
            "ROI Calculator/Tool": {
                "best_for": ["decision-maker", "cfo", "finance", "decision", "executive", "roi"],
                "description": "Interactive tool quantifying business impact",
                "suitability_factors": {
                    "executive": 10,
                    "senior": 9,
                    "mid": 7,
                    "decision": 10,
                    "consideration": 8,
                },
                "key_elements": [
                    "Input fields for company metrics",
                    "Calculation methodology",
                    "Results visualization",
                    "Detailed breakdown",
                    "Downloadable report"
                ],
                "typical_length": "Web-based interactive tool with PDF output",
                "tone": "Professional, transparent, data-driven"
            },
        }
        
        # Score each content type based on persona and stage
        scored_content = []
        
        for content_type, data in content_types.items():
            base_score = 5
            
            # Check if persona keywords match
            keyword_matches = sum(1 for keyword in data["best_for"] if keyword in profile_lower or keyword in stage_lower)
            keyword_score = min(5, keyword_matches * 1.5)
            
            # Check stage-specific scoring
            stage_bonus = 0
            if "awareness" in stage_lower and "awareness" in data["suitability_factors"]:
                stage_bonus = data["suitability_factors"]["awareness"] * 0.3
            elif "consideration" in stage_lower and "consideration" in data["suitability_factors"]:
                stage_bonus = data["suitability_factors"]["consideration"] * 0.3
            elif "decision" in stage_lower and "decision" in data["suitability_factors"]:
                stage_bonus = data["suitability_factors"]["decision"] * 0.3
            
            # Check seniority-specific scoring
            seniority_bonus = 0
            if "executive" in profile_lower or "ceo" in profile_lower or "cto" in profile_lower:
                seniority_bonus = data["suitability_factors"].get("executive", 5) * 0.2
            elif "senior" in profile_lower or "vp" in profile_lower or "director" in profile_lower:
                seniority_bonus = data["suitability_factors"].get("senior", 5) * 0.2
            else:
                seniority_bonus = data["suitability_factors"].get("mid", 5) * 0.2
            
            total_score = base_score + keyword_score + stage_bonus + seniority_bonus
            total_score = min(10, total_score)  # Cap at 10
            
            scored_content.append({
                "type": content_type,
                "score": round(total_score, 1),
                "data": data
            })
        
        # Sort by score
        scored_content.sort(key=lambda x: x["score"], reverse=True)
        
        # Generate output
        output = "## CONTENT TYPE RECOMMENDATIONS\n\n"
        output += f"**Target Persona:** {persona_profile[:200]}...\n"
        output += f"**Sales Stage:** {sales_stage}\n\n"
        output += "### Top Content Type Matches:\n\n"
        
        for i, item in enumerate(scored_content[:5], 1):  # Top 5 recommendations
            output += f"#### {i}. {item['type']} (Score: {item['score']}/10)\n\n"
            output += f"**Description:** {item['data']['description']}\n\n"
            output += f"**Why This Works:**\n"
            output += f"This content type scores highly because it aligns with the persona's "
            output += f"characteristics and stage in the buyer journey.\n\n"
            output += f"**Key Elements to Include:**\n"
            for element in item['data']['key_elements']:
                output += f"- {element}\n"
            output += f"\n**Format:** {item['data']['typical_length']}\n"
            output += f"**Tone:** {item['data']['tone']}\n\n"
            output += "---\n\n"
        
        return output


# ============================================================================
# TOOL 2: PERSONA-CONTENT MAPPER
# ============================================================================

class PersonaContentMapperToolInput(BaseModel):
    """Input schema for PersonaContentMapperTool."""
    persona_library: str = Field(
        description="Complete list of personas with their profiles"
    )
    content_goals: str = Field(
        description="Overall content goals (e.g., generate 50 case studies targeting diverse personas)"
    )


class PersonaContentMapperTool(BaseTool):
    """Creates a comprehensive mapping of personas to content assignments.
    
    This tool takes a full persona library and creates a strategic content
    plan that ensures:
    - Every persona has appropriate content
    - Content types are distributed appropriately
    - Demographic diversity is maintained
    - Sales funnel stages are covered
    
    Output is a complete content assignment matrix.
    """
    
    name: str = "Persona-Content Mapper"
    description: str = (
        "Maps all personas to specific content assignments. Takes a persona library and "
        "creates a complete content strategy matrix showing which personas get which content "
        "types, ensuring coverage and diversity. Use this to create the master content plan."
    )
    args_schema: Type[BaseModel] = PersonaContentMapperToolInput
    
    def _run(self, persona_library: str, content_goals: str) -> str:
        """Create persona-to-content mapping."""
        
        # Parse content goals to extract target numbers
        goals_lower = content_goals.lower()
        
        targets = {
            "case_study": 0,
            "white_paper": 0,
            "pitch_deck": 0,
            "social_media": 0,
        }
        
        # Extract numbers from goals
        import re
        if "case stud" in goals_lower:
            match = re.search(r'(\d+).*case stud', goals_lower)
            if match:
                targets["case_study"] = int(match.group(1))
        if "white paper" in goals_lower:
            match = re.search(r'(\d+).*white paper', goals_lower)
            if match:
                targets["white_paper"] = int(match.group(1))
        if "pitch deck" in goals_lower or "deck" in goals_lower:
            match = re.search(r'(\d+).*(pitch deck|deck)', goals_lower)
            if match:
                targets["pitch_deck"] = int(match.group(1))
        if "social media" in goals_lower or "social" in goals_lower:
            match = re.search(r'(\d+).*(social|post)', goals_lower)
            if match:
                targets["social_media"] = int(match.group(1))
        
        # If no specific targets, use defaults
        if sum(targets.values()) == 0:
            targets = {
                "case_study": 20,
                "white_paper": 10,
                "pitch_deck": 10,
                "social_media": 30,
            }
        
        # Parse persona library (simplified - in production would be more sophisticated)
        persona_count = persona_library.count("###") or 10  # Estimate from markdown headers
        
        # Generate mapping strategy
        output = "## PERSONA-CONTENT MAPPING STRATEGY\n\n"
        output += f"**Total Personas Identified:** ~{persona_count}\n"
        output += f"**Content Production Goals:**\n"
        for content_type, count in targets.items():
            if count > 0:
                formatted_type = content_type.replace("_", " ").title()
                output += f"- {formatted_type}: {count} pieces\n"
        
        output += "\n### Content Distribution Strategy:\n\n"
        
        # Case Studies
        if targets["case_study"] > 0:
            output += f"#### Case Studies ({targets['case_study']} total)\n\n"
            output += "**Distribution Approach:**\n"
            output += f"- Target primarily senior decision-makers and influencers\n"
            output += f"- Ensure mix across all company sizes (Enterprise: 40%, Mid-Market: 40%, SMB: 20%)\n"
            output += f"- Cover top 5-7 industries\n"
            output += f"- Balance between early adopters and mainstream buyers\n\n"
            output += "**Persona Priorities:**\n"
            output += "- C-Suite Executives (CEOs, CTOs, CROs) - 30%\n"
            output += "- VPs and Directors - 40%\n"
            output += "- Senior Managers and Champions - 30%\n\n"
            
        # White Papers
        if targets["white_paper"] > 0:
            output += f"#### White Papers ({targets['white_paper']} total)\n\n"
            output += "**Distribution Approach:**\n"
            output += f"- Target technical evaluators and researchers\n"
            output += f"- Focus on consideration stage personas\n"
            output += f"- Address specific industry challenges\n\n"
            output += "**Persona Priorities:**\n"
            output += "- Technical decision-makers (CTOs, Eng Directors) - 40%\n"
            output += "- Product/Operations leaders - 30%\n"
            output += "- Analysts and evaluators - 30%\n\n"
            
        # Pitch Decks
        if targets["pitch_deck"] > 0:
            output += f"#### Pitch Decks ({targets['pitch_deck']} total)\n\n"
            output += "**Distribution Approach:**\n"
            output += f"- Target executive buyers with limited time\n"
            output += f"- One deck per key industry vertical\n"
            output += f"- Adaptable templates for different company sizes\n\n"
            output += "**Persona Priorities:**\n"
            output += "- C-Suite (CEO, CFO, CRO) - 60%\n"
            output += "- Senior VPs - 40%\n\n"
            
        # Social Media
        if targets["social_media"] > 0:
            output += f"#### Social Media Content ({targets['social_media']} total)\n\n"
            output += "**Distribution Approach:**\n"
            output += f"- Cover all personas across buyer journey\n"
            output += f"- Mix of awareness, consideration, and decision content\n"
            output += f"- Platform-specific adaptations (LinkedIn, Twitter, etc.)\n\n"
            output += "**Content Mix:**\n"
            output += "- Thought leadership posts - 30%\n"
            output += "- Customer success highlights - 25%\n"
            output += "- Product tips and use cases - 25%\n"
            output += "- Industry insights and trends - 20%\n\n"
        
        output += "\n### Diversity and Coverage Checklist:\n\n"
        output += "**Ensure content covers:**\n"
        output += "- ✓ All company size segments (Startup → Enterprise)\n"
        output += "- ✓ All target industries (at least top 5)\n"
        output += "- ✓ All buyer journey stages (Awareness → Decision)\n"
        output += "- ✓ All buying roles (User → Decision-maker)\n"
        output += "- ✓ Geographic diversity (North America, EMEA, APAC)\n"
        output += "- ✓ Tech adoption profiles (Early adopter → Late majority)\n\n"
        
        output += "### Next Steps:\n\n"
        output += "Use the Content Brief Generator tool to create detailed briefs for each "
        output += "piece of content, ensuring each brief targets a specific persona from the library.\n"
        
        return output


# ============================================================================
# TOOL 3: STRATEGY TEMPLATE GENERATOR
# ============================================================================

class StrategyTemplateGeneratorToolInput(BaseModel):
    """Input schema for StrategyTemplateGeneratorTool."""
    content_type: str = Field(
        description="Type of content to generate brief for (Case Study, White Paper, etc.)"
    )
    target_persona: str = Field(
        description="Specific persona this content targets, including role, company, challenges"
    )
    product_value_props: str = Field(
        description="Key product value propositions relevant to this persona"
    )


class StrategyTemplateGeneratorTool(BaseTool):
    """Generates detailed content briefs for writers.
    
    This tool creates comprehensive content briefs that give writers everything
    they need to create high-quality, persona-targeted content. Each brief includes:
    - Target persona profile
    - Key messages to convey
    - Pain points to address
    - Proof points and data to include
    - Tone and style guidelines
    - Success metrics
    - Call-to-action
    
    MAX 5 CALLS - Prevents infinite loops by tracking generated briefs.
    """
    
    name: str = "Strategy Template Generator"
    description: str = (
        "Creates detailed content briefs for specific content pieces. Takes a content type "
        "and target persona, generates a comprehensive brief with key messages, pain points, "
        "proof points, tone guidelines, and success metrics. Use this to create actionable "
        "briefs for content writers. LIMIT: Maximum 5 briefs per strategy session."
    )
    args_schema: Type[BaseModel] = StrategyTemplateGeneratorToolInput
    
    # Class variable to track generated briefs (prevents duplicate calls)
    _generated_briefs: set = set()
    _call_count: int = 0
    _MAX_BRIEFS: int = 5
    
    def _run(self, content_type: str, target_persona: str, product_value_props: str) -> str:
        """Generate detailed content brief with duplicate detection."""
        
        # Create unique key for this brief
        import hashlib
        brief_key = hashlib.md5(f"{content_type}{target_persona}".encode()).hexdigest()
        
        # Check if we've already generated this exact brief
        if brief_key in self._generated_briefs:
            return (
                f"⚠️ **DUPLICATE BRIEF DETECTED** ⚠️\n\n"
                f"Already generated brief for:\n"
                f"- Content Type: {content_type}\n"
                f"- Persona: {target_persona[:100]}...\n\n"
                f"**Action:** Move to next persona or content type, or finalize strategy.\n"
                f"**Briefs Created:** {self._call_count}/{self._MAX_BRIEFS}"
            )
        
        # Check if we've hit the maximum
        if self._call_count >= self._MAX_BRIEFS:
            return (
                f"⚠️ **MAXIMUM BRIEFS REACHED** ⚠️\n\n"
                f"Generated {self._call_count} content briefs - this is sufficient for a "
                f"high-quality content strategy.\n\n"
                f"**Action:** Finalize your content strategy document now. Focus on QUALITY "
                f"over QUANTITY. CREW 2 will generate the actual content from these briefs.\n\n"
                f"**Generated Briefs:** {len(self._generated_briefs)}\n"
                f"**Next Step:** Write strategy summary and execution priorities."
            )
        
        # Track this brief
        self._generated_briefs.add(brief_key)
        self._call_count += 1
        
        # Extract key info from inputs
        persona_lower = target_persona.lower()
        
        # Determine seniority and department
        seniority = "Mid-level"
        if any(title in persona_lower for title in ["ceo", "cto", "cfo", "cro", "chief"]):
            seniority = "Executive"
        elif any(title in persona_lower for title in ["vp", "director", "senior"]):
            seniority = "Senior"
        
        department = "General"
        dept_keywords = {
            "Sales": ["sales", "account executive", "sdr", "revenue"],
            "Marketing": ["marketing", "content", "demand gen", "brand"],
            "Product": ["product", "pm", "product manager"],
            "Engineering": ["engineer", "developer", "engineering", "tech"],
            "Operations": ["operations", "ops", "process"],
            "Customer Success": ["customer success", "cs", "account management"],
        }
        
        for dept, keywords in dept_keywords.items():
            if any(kw in persona_lower for kw in keywords):
                department = dept
                break
        
        # Generate unique content ID
        import hashlib
        content_id = hashlib.md5(f"{content_type}{target_persona}".encode()).hexdigest()[:8]
        
        # Generate output
        output = f"# CONTENT BRIEF #{self._call_count}/{self._MAX_BRIEFS}: {content_type}\n\n"
        output += f"**Brief ID:** {content_id}\n"
        output += f"**Created:** [Current Date]\n"
        output += f"**Status:** Draft - Ready for Writer Assignment\n"
        output += f"**Progress:** {self._call_count} of {self._MAX_BRIEFS} briefs created\n\n"
        
        output += "---\n\n"
        output += "## 1. TARGET PERSONA\n\n"
        output += f"**Profile Summary:**\n{target_persona[:500]}...\n\n"
        output += f"**Seniority Level:** {seniority}\n"
        output += f"**Department/Function:** {department}\n"
        output += f"**Buying Influence:** "
        if seniority == "Executive":
            output += "Primary Decision-maker\n"
        elif seniority == "Senior":
            output += "Key Influencer / Budget Owner\n"
        else:
            output += "End User / Champion\n"
        
        output += "\n---\n\n"
        output += "## 2. CONTENT OBJECTIVES\n\n"
        
        # Content-type specific objectives
        if "case study" in content_type.lower():
            output += "**Primary Goal:** Build credibility and demonstrate proven ROI\n\n"
            output += "**Success Criteria:**\n"
            output += "- Showcase quantifiable business results\n"
            output += "- Address persona's specific challenges\n"
            output += "- Provide relatable customer story\n"
            output += "- Include authentic testimonial\n"
            output += "- Drive demo/trial requests\n\n"
            
        elif "white paper" in content_type.lower():
            output += "**Primary Goal:** Establish thought leadership and educate buyer\n\n"
            output += "**Success Criteria:**\n"
            output += "- Position product as solution to industry challenge\n"
            output += "- Provide actionable frameworks/best practices\n"
            output += "- Include credible data and research\n"
            output += "- Demonstrate deep expertise\n"
            output += "- Generate qualified leads\n\n"
            
        elif "pitch deck" in content_type.lower():
            output += "**Primary Goal:** Clearly communicate value and drive decision\n\n"
            output += "**Success Criteria:**\n"
            output += "- Concisely explain problem and solution\n"
            output += "- Show clear ROI and business case\n"
            output += "- Use visual storytelling\n"
            output += "- Address key objections\n"
            output += "- Accelerate sales cycle\n\n"
            
        else:  # Social media
            output += "**Primary Goal:** Build awareness and engagement\n\n"
            output += "**Success Criteria:**\n"
            output += "- Capture attention quickly\n"
            output += "- Provide immediate value/insight\n"
            output += "- Encourage shares and comments\n"
            output += "- Drive profile visits or link clicks\n"
            output += "- Generate conversation\n\n"
        
        output += "---\n\n"
        output += "## 3. KEY MESSAGES\n\n"
        output += "**Core Message:**\n"
        output += f"[Product] helps {department} {seniority.lower()} professionals like you "
        output += "overcome [specific challenge] and achieve [specific outcome].\n\n"
        output += "**Supporting Messages:**\n"
        output += f"1. {product_value_props[:200]}...\n"
        output += f"2. Proven results with customers in similar roles\n"
        output += f"3. Quick time-to-value with minimal disruption\n"
        output += f"4. Comprehensive support and resources\n\n"
        
        output += "---\n\n"
        output += "## 4. PAIN POINTS TO ADDRESS\n\n"
        
        # Generate relevant pain points based on department
        pain_points = {
            "Sales": [
                "Spending too much time on non-selling activities",
                "Difficulty tracking and managing pipeline effectively",
                "Inconsistent deal execution and forecasting accuracy",
                "Limited visibility into what's working"
            ],
            "Marketing": [
                "Difficulty proving marketing ROI and attribution",
                "Challenges creating content at scale",
                "Limited insights into what resonates with audience",
                "Misalignment between marketing and sales"
            ],
            "Product": [
                "Unclear prioritization of features and initiatives",
                "Limited visibility into user behavior and feedback",
                "Cross-functional misalignment",
                "Slow time-to-market"
            ],
            "Engineering": [
                "Too many meetings disrupting deep work",
                "Technical debt slowing development",
                "Poor documentation and knowledge sharing",
                "Difficulty onboarding new team members"
            ],
            "Operations": [
                "Manual, time-consuming processes",
                "Data scattered across multiple systems",
                "Lack of visibility and reporting",
                "Scaling challenges"
            ],
            "Customer Success": [
                "Difficulty predicting and preventing churn",
                "Limited bandwidth to serve all accounts",
                "Challenges demonstrating value to customers",
                "Reactive rather than proactive engagement"
            ],
        }
        
        relevant_pains = pain_points.get(department, pain_points["Sales"])
        for i, pain in enumerate(relevant_pains, 1):
            output += f"{i}. {pain}\n"
        
        output += "\n---\n\n"
        output += "## 5. PROOF POINTS & DATA\n\n"
        output += "**Required Evidence:**\n"
        output += "- Customer success metrics (specific numbers)\n"
        output += "- Time savings or efficiency gains\n"
        output += "- Revenue impact or cost reduction\n"
        output += "- User satisfaction scores\n"
        output += "- Industry benchmarks for context\n\n"
        output += "**Testimonial/Quote:**\n"
        output += "[Include authentic customer quote from similar persona]\n\n"
        
        output += "---\n\n"
        output += "## 6. TONE & STYLE GUIDELINES\n\n"
        
        if seniority == "Executive":
            output += "**Tone:** Professional, strategic, results-focused\n"
            output += "**Voice:** Authoritative but conversational\n"
            output += "**Style Notes:**\n"
            output += "- Lead with business outcomes, not features\n"
            output += "- Use executive-level language\n"
            output += "- Be concise - respect their time\n"
            output += "- Include high-level strategic implications\n\n"
        elif seniority == "Senior":
            output += "**Tone:** Knowledgeable, practical, solution-oriented\n"
            output += "**Voice:** Expert peer-to-peer\n"
            output += "**Style Notes:**\n"
            output += "- Balance strategy with tactical details\n"
            output += "- Show understanding of their challenges\n"
            output += "- Include implementation considerations\n"
            output += "- Provide actionable insights\n\n"
        else:
            output += "**Tone:** Helpful, empowering, relatable\n"
            output += "**Voice:** Supportive colleague\n"
            output += "**Style Notes:**\n"
            output += "- Focus on day-to-day impact\n"
            output += "- Use specific, practical examples\n"
            output += "- Show how it makes their job easier\n"
            output += "- Include step-by-step guidance\n\n"
        
        output += "---\n\n"
        output += "## 7. CALL-TO-ACTION\n\n"
        output += "**Primary CTA:**\n"
        
        if "case study" in content_type.lower() or "white paper" in content_type.lower():
            output += "\"See how [Product] can deliver similar results for your team. Schedule a personalized demo.\"\n\n"
        elif "pitch deck" in content_type.lower():
            output += "\"Let's discuss how [Product] can address your specific needs. Book a consultation.\"\n\n"
        else:
            output += "\"Learn more about [specific feature/use case]. Visit [link] or drop a comment below.\"\n\n"
        
        output += "**Secondary CTA:**\n"
        output += "\"Download our [related resource] for more insights.\"\n\n"
        
        output += "---\n\n"
        output += "## 8. DISTRIBUTION & PROMOTION\n\n"
        output += "**Primary Channels:**\n"
        
        if "social" in content_type.lower():
            output += "- LinkedIn (personal + company page)\n"
            output += "- Twitter/X\n"
            output += "- Industry communities and forums\n\n"
        else:
            output += "- Website resource library\n"
            output += "- Email nurture campaigns\n"
            output += "- Sales enablement (shared with AEs)\n"
            output += "- Paid promotion (LinkedIn, Google)\n\n"
        
        output += "**Target Audience:**\n"
        output += f"- Job titles: {department} roles at {seniority.lower()} level\n"
        output += "- Company size: [Based on persona segment]\n"
        output += "- Industries: [Top 3-5 relevant industries]\n\n"
        
        output += "---\n\n"
        output += "## 9. SUCCESS METRICS\n\n"
        output += "**Quantitative Metrics:**\n"
        output += "- Views/Downloads: [Target number]\n"
        output += "- Conversion rate: [Target %]\n"
        output += "- Demo requests generated: [Target number]\n"
        output += "- Engagement rate: [Target %]\n\n"
        output += "**Qualitative Metrics:**\n"
        output += "- Sales team feedback and usage\n"
        output += "- Prospect/customer comments\n"
        output += "- Content quality score (internal review)\n\n"
        
        output += "---\n\n"
        output += "## 10. WRITER NOTES\n\n"
        output += "**Additional Context:**\n"
        output += "- Research similar content in our library\n"
        output += "- Interview customer success team for real examples\n"
        output += "- Review persona research document for deeper insights\n"
        output += "- Coordinate with product marketing for latest messaging\n\n"
        output += "**Timeline:**\n"
        output += "- First draft due: [Date]\n"
        output += "- Review cycle: [Date range]\n"
        output += "- Final version due: [Date]\n"
        output += "- Publication date: [Date]\n\n"
        
        return output
