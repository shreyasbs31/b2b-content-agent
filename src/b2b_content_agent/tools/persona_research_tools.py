"""Persona Research Tools for B2B Content Agent System.

Tools for Agent #2 (Persona Researcher) to identify, analyze, and profile
target personas based on product capabilities and market opportunities.
"""

from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import json
import re


# ============================================================================
# PYDANTIC MODELS FOR STRUCTURED DATA
# ============================================================================

class IndustryProfile(BaseModel):
    """Structured profile of an industry vertical."""
    industry_name: str = Field(description="Name of the industry vertical")
    market_size: str = Field(description="Estimated market size or description")
    key_challenges: List[str] = Field(description="Top challenges faced in this industry")
    product_fit_score: int = Field(description="How well the product fits this industry (1-10)")
    potential_use_cases: List[str] = Field(description="Specific use cases for this industry")
    buying_patterns: str = Field(description="Typical buying behavior in this industry")


class JobRoleProfile(BaseModel):
    """Structured profile of a job role/title."""
    role_title: str = Field(description="Job title or role")
    seniority_level: str = Field(description="Entry/Mid/Senior/Executive level")
    department: str = Field(description="Department or function")
    typical_goals: List[str] = Field(description="Common goals and objectives")
    pain_points: List[str] = Field(description="Key challenges and frustrations")
    buying_influence: str = Field(description="Role in buying decisions: User/Influencer/Decision-maker/Champion")
    product_relevance: str = Field(description="How the product addresses their needs")


class DemographicSegment(BaseModel):
    """Structured demographic segment profile."""
    segment_name: str = Field(description="Name of this demographic segment")
    company_size: str = Field(description="Company size range (e.g., 10-50, 51-500, 500+)")
    industry_verticals: List[str] = Field(description="Relevant industries for this segment")
    job_roles: List[str] = Field(description="Key job roles in this segment")
    tech_maturity: str = Field(description="Technology adoption level: Early/Mainstream/Late")
    budget_range: str = Field(description="Typical budget allocation")
    geographic_focus: List[str] = Field(description="Primary geographic markets")
    unique_characteristics: List[str] = Field(description="Distinguishing features of this segment")


# ============================================================================
# TOOL 1: INDUSTRY ANALYZER
# ============================================================================

class IndustryAnalyzerToolInput(BaseModel):
    """Input schema for IndustryAnalyzerTool."""
    product_features: str = Field(
        description="Description of product features and capabilities"
    )
    product_use_cases: str = Field(
        description="Known or potential use cases for the product"
    )


class IndustryAnalyzerTool(BaseTool):
    """Analyzes which industry verticals are best suited for a product.
    
    This tool examines product capabilities and maps them to industry-specific
    needs, challenges, and opportunities. It identifies the top 10-15 industries
    where the product could have the strongest fit and impact.
    
    The analysis considers:
    - Industry pain points and how the product addresses them
    - Market size and growth potential
    - Typical buying behaviors in each industry
    - Regulatory or compliance considerations
    - Technology adoption patterns
    """
    
    name: str = "Industry Analyzer"
    description: str = (
        "Identifies the best-fit industry verticals for a product based on its features "
        "and capabilities. Returns detailed profiles of 10-15 industries including market "
        "size, challenges, use cases, and buying patterns. Use this when you need to "
        "understand which industries should be targeted for persona development."
    )
    args_schema: Type[BaseModel] = IndustryAnalyzerToolInput
    
    def _run(self, product_features: str, product_use_cases: str) -> str:
        """Analyze industries based on product characteristics."""
        
        # Industry mapping patterns (keyword-based heuristics)
        industry_patterns = {
            "Technology/SaaS": {
                "keywords": ["api", "integration", "cloud", "software", "platform", "automation", "analytics"],
                "challenges": ["Scale rapidly", "Improve developer productivity", "Reduce time-to-market", "Enhance collaboration"],
                "buying_patterns": "Bottom-up adoption, freemium models, technical evaluation"
            },
            "Professional Services": {
                "keywords": ["consulting", "client", "project", "billable", "time tracking", "documentation"],
                "challenges": ["Capture billable hours", "Improve client communication", "Manage multiple projects", "Maintain quality"],
                "buying_patterns": "ROI-focused, partner referrals, proof of productivity gains"
            },
            "Healthcare": {
                "keywords": ["patient", "medical", "clinical", "hipaa", "compliance", "record", "diagnosis"],
                "challenges": ["Reduce documentation burden", "Improve patient outcomes", "Ensure compliance", "Streamline workflows"],
                "buying_patterns": "Long sales cycles, compliance-first, committee decisions"
            },
            "Financial Services": {
                "keywords": ["transaction", "payment", "compliance", "risk", "audit", "reporting", "security"],
                "challenges": ["Ensure regulatory compliance", "Manage risk", "Improve accuracy", "Streamline audits"],
                "buying_patterns": "Risk-averse, security paramount, multi-stakeholder approval"
            },
            "Sales & Marketing": {
                "keywords": ["lead", "conversion", "crm", "campaign", "customer", "engagement", "outreach"],
                "challenges": ["Generate qualified leads", "Improve conversion rates", "Personalize at scale", "Track attribution"],
                "buying_patterns": "Quick decisions, trial-driven, revenue impact focus"
            },
            "Education": {
                "keywords": ["student", "learning", "course", "assignment", "grade", "classroom", "academic"],
                "challenges": ["Engage students", "Personalize learning", "Reduce admin burden", "Improve outcomes"],
                "buying_patterns": "Budget-constrained, academic year cycles, committee approval"
            },
            "Legal": {
                "keywords": ["contract", "case", "litigation", "compliance", "document review", "billing", "client matter"],
                "challenges": ["Improve billable utilization", "Reduce contract review time", "Ensure accuracy", "Client transparency"],
                "buying_patterns": "Conservative, precedent-driven, partnership decisions"
            },
            "Manufacturing": {
                "keywords": ["production", "quality control", "supply chain", "inventory", "equipment", "safety"],
                "challenges": ["Optimize production", "Reduce downtime", "Ensure quality", "Manage supply chain"],
                "buying_patterns": "ROI-driven, long evaluation, plant-level buy-in"
            },
            "Real Estate": {
                "keywords": ["property", "listing", "transaction", "agent", "broker", "client", "showing"],
                "challenges": ["Generate leads", "Close deals faster", "Manage client relationships", "Market properties"],
                "buying_patterns": "Commission-sensitive, ease-of-use critical, mobile-first"
            },
            "E-commerce/Retail": {
                "keywords": ["product", "inventory", "customer", "checkout", "fulfillment", "conversion", "cart"],
                "challenges": ["Increase conversion", "Reduce cart abandonment", "Personalize experiences", "Optimize inventory"],
                "buying_patterns": "Data-driven, A/B testing culture, seasonal considerations"
            },
        }
        
        combined_text = f"{product_features} {product_use_cases}".lower()
        
        # Score each industry based on keyword matches
        industry_scores = {}
        for industry, data in industry_patterns.items():
            score = sum(1 for keyword in data["keywords"] if keyword in combined_text)
            if score > 0:
                industry_scores[industry] = {
                    "score": score,
                    "data": data
                }
        
        # Sort by score and take top industries
        top_industries = sorted(
            industry_scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )[:12]  # Get top 12 industries
        
        # Generate structured profiles
        profiles = []
        for industry_name, info in top_industries:
            profile = IndustryProfile(
                industry_name=industry_name,
                market_size="Research specific market data for accurate sizing",
                key_challenges=info["data"]["challenges"],
                product_fit_score=min(10, info["score"] + 5),  # Scale to 1-10
                potential_use_cases=self._generate_use_cases(industry_name, product_features),
                buying_patterns=info["data"]["buying_patterns"]
            )
            profiles.append(profile)
        
        # Format output
        output = "## INDUSTRY ANALYSIS RESULTS\n\n"
        output += f"Analyzed product against {len(industry_patterns)} industry verticals.\n"
        output += f"**Top {len(profiles)} Best-Fit Industries:**\n\n"
        
        for i, profile in enumerate(profiles, 1):
            output += f"### {i}. {profile.industry_name}\n"
            output += f"**Product Fit Score:** {profile.product_fit_score}/10\n\n"
            output += f"**Key Challenges:**\n"
            for challenge in profile.key_challenges:
                output += f"- {challenge}\n"
            output += f"\n**Potential Use Cases:**\n"
            for use_case in profile.potential_use_cases:
                output += f"- {use_case}\n"
            output += f"\n**Buying Patterns:** {profile.buying_patterns}\n\n"
            output += "---\n\n"
        
        return output
    
    def _generate_use_cases(self, industry: str, product_features: str) -> List[str]:
        """Generate industry-specific use cases."""
        # This is a simplified version - in production, you'd use LLM or more sophisticated logic
        use_cases = [
            f"Streamline {industry.lower()} operations with automated workflows",
            f"Improve decision-making in {industry.lower()} with data-driven insights",
            f"Enhance {industry.lower()} team collaboration and communication"
        ]
        return use_cases


# ============================================================================
# TOOL 2: JOB ROLE ANALYZER
# ============================================================================

class JobRoleAnalyzerToolInput(BaseModel):
    """Input schema for JobRoleAnalyzerTool."""
    target_industries: str = Field(
        description="List of target industries identified for this product"
    )
    product_value_props: str = Field(
        description="Key value propositions and benefits of the product"
    )


class JobRoleAnalyzerTool(BaseTool):
    """Identifies and profiles specific job roles that would benefit from the product.
    
    This tool analyzes which job titles, roles, and functions within target industries
    are the best prospects. It creates detailed profiles including:
    - Typical goals and KPIs for each role
    - Pain points and challenges they face
    - Their role in the buying process
    - How the product addresses their specific needs
    """
    
    name: str = "Job Role Analyzer"
    description: str = (
        "Identifies specific job roles and titles that are ideal personas for the product. "
        "Returns detailed profiles of 20-30 roles including their goals, pain points, buying "
        "influence, and product relevance. Use this after industry analysis to drill down "
        "into specific decision-makers and users."
    )
    args_schema: Type[BaseModel] = JobRoleAnalyzerToolInput
    
    def _run(self, target_industries: str, product_value_props: str) -> str:
        """Analyze job roles based on industries and value propositions."""
        
        # Comprehensive role database
        role_database = {
            # Executive Roles
            "Chief Executive Officer (CEO)": {
                "seniority": "Executive",
                "department": "Executive Leadership",
                "goals": ["Drive company growth", "Improve operational efficiency", "Increase profitability"],
                "pain_points": ["Limited visibility into operations", "Scaling challenges", "Competitive pressure"],
                "buying_influence": "Final Decision-maker",
            },
            "Chief Technology Officer (CTO)": {
                "seniority": "Executive",
                "department": "Technology",
                "goals": ["Drive technical innovation", "Improve developer productivity", "Reduce technical debt"],
                "pain_points": ["Managing technical team scale", "Tool sprawl", "Security concerns"],
                "buying_influence": "Decision-maker",
            },
            "Chief Revenue Officer (CRO)": {
                "seniority": "Executive",
                "department": "Revenue Operations",
                "goals": ["Increase revenue", "Improve win rates", "Shorten sales cycles"],
                "pain_points": ["Inconsistent sales processes", "Poor pipeline visibility", "Missed forecasts"],
                "buying_influence": "Decision-maker",
            },
            "Chief Marketing Officer (CMO)": {
                "seniority": "Executive",
                "department": "Marketing",
                "goals": ["Generate qualified leads", "Build brand", "Prove marketing ROI"],
                "pain_points": ["Attribution challenges", "Content at scale", "Alignment with sales"],
                "buying_influence": "Decision-maker",
            },
            
            # Sales Roles
            "VP of Sales": {
                "seniority": "Senior",
                "department": "Sales",
                "goals": ["Hit revenue targets", "Build high-performing team", "Improve sales efficiency"],
                "pain_points": ["Inconsistent performance", "Long ramp times", "Poor CRM adoption"],
                "buying_influence": "Decision-maker",
            },
            "Sales Director": {
                "seniority": "Senior",
                "department": "Sales",
                "goals": ["Manage team to quota", "Improve win rates", "Coach sellers"],
                "pain_points": ["Lack of visibility", "Inconsistent execution", "Data quality"],
                "buying_influence": "Influencer",
            },
            "Account Executive": {
                "seniority": "Mid",
                "department": "Sales",
                "goals": ["Close deals", "Build relationships", "Exceed quota"],
                "pain_points": ["Admin burden", "Inefficient processes", "Lack of good insights"],
                "buying_influence": "User/Champion",
            },
            "Sales Development Representative (SDR)": {
                "seniority": "Entry",
                "department": "Sales",
                "goals": ["Generate qualified meetings", "Build pipeline", "Hit activity targets"],
                "pain_points": ["Manual research", "Low response rates", "Repetitive tasks"],
                "buying_influence": "User",
            },
            
            # Marketing Roles
            "VP of Marketing": {
                "seniority": "Senior",
                "department": "Marketing",
                "goals": ["Drive demand generation", "Build brand awareness", "Optimize marketing spend"],
                "pain_points": ["Proving ROI", "Cross-channel attribution", "Content production at scale"],
                "buying_influence": "Decision-maker",
            },
            "Content Marketing Manager": {
                "seniority": "Mid",
                "department": "Marketing",
                "goals": ["Create engaging content", "Drive organic traffic", "Support sales enablement"],
                "pain_points": ["Content ideas", "Production bottlenecks", "Measuring impact"],
                "buying_influence": "User/Influencer",
            },
            "Demand Generation Manager": {
                "seniority": "Mid",
                "department": "Marketing",
                "goals": ["Generate qualified leads", "Optimize campaigns", "Improve conversion rates"],
                "pain_points": ["Lead quality issues", "Campaign complexity", "Tech stack integration"],
                "buying_influence": "User/Influencer",
            },
            
            # Product/Engineering Roles
            "VP of Product": {
                "seniority": "Senior",
                "department": "Product",
                "goals": ["Ship valuable features", "Improve user satisfaction", "Drive product adoption"],
                "pain_points": ["Feature prioritization", "Cross-functional alignment", "User research at scale"],
                "buying_influence": "Decision-maker",
            },
            "Product Manager": {
                "seniority": "Mid",
                "department": "Product",
                "goals": ["Deliver on roadmap", "Gather user feedback", "Make data-driven decisions"],
                "pain_points": ["Stakeholder management", "Feature creep", "Competing priorities"],
                "buying_influence": "User/Influencer",
            },
            "Engineering Manager": {
                "seniority": "Senior",
                "department": "Engineering",
                "goals": ["Deliver high-quality code", "Improve team velocity", "Reduce technical debt"],
                "pain_points": ["Context switching", "Meeting overload", "Team coordination"],
                "buying_influence": "Influencer",
            },
            "Software Engineer": {
                "seniority": "Mid",
                "department": "Engineering",
                "goals": ["Write quality code", "Ship features", "Learn and grow"],
                "pain_points": ["Documentation gaps", "Tool friction", "Unclear requirements"],
                "buying_influence": "User",
            },
            
            # Operations Roles
            "VP of Operations": {
                "seniority": "Senior",
                "department": "Operations",
                "goals": ["Improve efficiency", "Scale processes", "Reduce costs"],
                "pain_points": ["Manual processes", "Data silos", "Cross-team coordination"],
                "buying_influence": "Decision-maker",
            },
            "Operations Manager": {
                "seniority": "Mid",
                "department": "Operations",
                "goals": ["Streamline workflows", "Improve team productivity", "Maintain quality"],
                "pain_points": ["Process bottlenecks", "Reporting burden", "System integration"],
                "buying_influence": "User/Influencer",
            },
            
            # Consulting/Services Roles
            "Managing Partner": {
                "seniority": "Executive",
                "department": "Professional Services",
                "goals": ["Grow revenue", "Improve margins", "Retain top talent"],
                "pain_points": ["Utilization rates", "Client satisfaction", "Competitive pressure"],
                "buying_influence": "Decision-maker",
            },
            "Senior Consultant": {
                "seniority": "Senior",
                "department": "Professional Services",
                "goals": ["Deliver client value", "Build expertise", "Increase billable hours"],
                "pain_points": ["Documentation burden", "Context switching", "Knowledge capture"],
                "buying_influence": "User/Champion",
            },
            "Associate Consultant": {
                "seniority": "Entry",
                "department": "Professional Services",
                "goals": ["Learn quickly", "Support projects", "Build client relationships"],
                "pain_points": ["Steep learning curve", "Admin tasks", "Limited context"],
                "buying_influence": "User",
            },
            
            # Customer Success Roles
            "VP of Customer Success": {
                "seniority": "Senior",
                "department": "Customer Success",
                "goals": ["Reduce churn", "Expand revenue", "Improve customer satisfaction"],
                "pain_points": ["Early churn signals", "Account prioritization", "Team bandwidth"],
                "buying_influence": "Decision-maker",
            },
            "Customer Success Manager": {
                "seniority": "Mid",
                "department": "Customer Success",
                "goals": ["Drive adoption", "Renew accounts", "Identify expansion opportunities"],
                "pain_points": ["Manual check-ins", "Lack of usage insights", "Scaling 1:many"],
                "buying_influence": "User/Champion",
            },
        }
        
        # Filter roles based on context (simple keyword matching)
        combined_text = f"{target_industries} {product_value_props}".lower()
        
        # Select relevant roles (in production, this would be more sophisticated)
        selected_roles = []
        for role_title, data in role_database.items():
            # Simple relevance check based on keywords
            if any(keyword in combined_text for keyword in ["sales", "revenue", "crm"]):
                if "sales" in role_title.lower() or data["department"] == "Sales":
                    selected_roles.append((role_title, data))
            if any(keyword in combined_text for keyword in ["marketing", "content", "demand"]):
                if "marketing" in role_title.lower() or data["department"] == "Marketing":
                    selected_roles.append((role_title, data))
            if any(keyword in combined_text for keyword in ["product", "engineering", "developer"]):
                if "product" in role_title.lower() or "engineering" in role_title.lower():
                    selected_roles.append((role_title, data))
            if any(keyword in combined_text for keyword in ["consulting", "professional services"]):
                if "consultant" in role_title.lower() or data["department"] == "Professional Services":
                    selected_roles.append((role_title, data))
        
        # If no specific matches, include executive roles as they're always relevant
        if len(selected_roles) < 10:
            for role_title, data in role_database.items():
                if data["seniority"] == "Executive" and (role_title, data) not in selected_roles:
                    selected_roles.append((role_title, data))
        
        # Limit to top 25 roles
        selected_roles = selected_roles[:25]
        
        # Generate output
        output = "## JOB ROLE ANALYSIS RESULTS\n\n"
        output += f"Identified {len(selected_roles)} key job roles across target industries.\n\n"
        
        for i, (role_title, data) in enumerate(selected_roles, 1):
            output += f"### {i}. {role_title}\n"
            output += f"**Seniority:** {data['seniority']} | "
            output += f"**Department:** {data['department']} | "
            output += f"**Buying Influence:** {data['buying_influence']}\n\n"
            
            output += "**Typical Goals:**\n"
            for goal in data["goals"]:
                output += f"- {goal}\n"
            
            output += "\n**Key Pain Points:**\n"
            for pain in data["pain_points"]:
                output += f"- {pain}\n"
            
            output += "\n**Product Relevance:**\n"
            output += self._generate_relevance(role_title, data, product_value_props)
            output += "\n\n---\n\n"
        
        return output
    
    def _generate_relevance(self, role_title: str, role_data: Dict, value_props: str) -> str:
        """Generate product relevance statement for a role."""
        # Simplified relevance generation
        department = role_data["department"]
        influence = role_data["buying_influence"]
        
        relevance = f"As a {influence} in {department}, this role would benefit from the product's ability to "
        relevance += "streamline workflows, improve decision-making, and drive better outcomes."
        
        return relevance


# ============================================================================
# TOOL 3: DEMOGRAPHICS MAPPER
# ============================================================================

class DemographicsMapperToolInput(BaseModel):
    """Input schema for DemographicsMapperTool."""
    industries: str = Field(
        description="Target industries identified for this product"
    )
    job_roles: str = Field(
        description="Key job roles identified as potential users"
    )
    product_pricing: str = Field(
        description="Pricing information and tiers for the product"
    )


class DemographicsMapperTool(BaseTool):
    """Maps product to demographic segments across company size, geography, and tech maturity.
    
    This tool creates a comprehensive demographic segmentation that helps identify:
    - Which company sizes are the best fit
    - Geographic markets with highest potential
    - Technology adoption profiles
    - Budget constraints and allocation patterns
    
    Output is used to create diverse, realistic personas spanning all key segments.
    """
    
    name: str = "Demographics Mapper"
    description: str = (
        "Creates detailed demographic segments combining company size, industry, geography, "
        "and technology maturity. Returns 8-12 distinct segments that should be represented "
        "in the persona library. Use this to ensure persona diversity and complete market coverage."
    )
    args_schema: Type[BaseModel] = DemographicsMapperToolInput
    
    def _run(self, industries: str, job_roles: str, product_pricing: str) -> str:
        """Map demographics based on industries, roles, and pricing."""
        
        # Parse pricing to infer company size fit
        pricing_lower = product_pricing.lower()
        price_indicators = {
            "enterprise": ["enterprise", "custom pricing", "contact sales", "$10,000", "$50,000"],
            "mid_market": ["business", "professional", "team", "$100", "$500", "$1,000"],
            "smb": ["starter", "basic", "individual", "$29", "$49", "$99"]
        }
        
        target_segments = []
        for segment_type, keywords in price_indicators.items():
            if any(keyword in pricing_lower for keyword in keywords):
                target_segments.append(segment_type)
        
        if not target_segments:
            target_segments = ["mid_market"]  # Default
        
        # Define segment templates
        segment_templates = {
            "enterprise_tech_forward": {
                "company_size": "500+ employees",
                "tech_maturity": "Early Adopter - Cutting-edge tech stack",
                "budget_range": "$50K-$500K+ annual software spend",
                "characteristics": [
                    "Sophisticated procurement process",
                    "Multiple stakeholder approval required",
                    "Focus on integration with existing systems",
                    "Security and compliance paramount"
                ]
            },
            "enterprise_conservative": {
                "company_size": "500+ employees",
                "tech_maturity": "Late Majority - Proven solutions preferred",
                "budget_range": "$50K-$500K+ annual software spend",
                "characteristics": [
                    "Risk-averse decision making",
                    "Long evaluation cycles (6-12 months)",
                    "Require extensive references and case studies",
                    "On-premise or private cloud preferred"
                ]
            },
            "mid_market_growth": {
                "company_size": "51-500 employees",
                "tech_maturity": "Early Majority - Pragmatic adopters",
                "budget_range": "$10K-$100K annual software spend",
                "characteristics": [
                    "Growing rapidly, need to scale",
                    "Limited IT resources",
                    "Value ease of implementation",
                    "ROI-focused buying decisions"
                ]
            },
            "mid_market_established": {
                "company_size": "51-500 employees",
                "tech_maturity": "Mainstream - Standard tech stack",
                "budget_range": "$10K-$100K annual software spend",
                "characteristics": [
                    "Established processes and systems",
                    "Looking to modernize incrementally",
                    "Change management considerations",
                    "Department-level buying authority"
                ]
            },
            "smb_tech_savvy": {
                "company_size": "10-50 employees",
                "tech_maturity": "Early Adopter - Modern tools",
                "budget_range": "$1K-$25K annual software spend",
                "characteristics": [
                    "Founder/CEO involved in decisions",
                    "Quick decision cycles",
                    "Self-service preference",
                    "Mobile-first mindset"
                ]
            },
            "smb_traditional": {
                "company_size": "10-50 employees",
                "tech_maturity": "Late Majority - Basic tools",
                "budget_range": "$1K-$25K annual software spend",
                "characteristics": [
                    "Cost-sensitive",
                    "Need significant hand-holding",
                    "Prefer local/regional vendors",
                    "Skeptical of new technology"
                ]
            },
            "startup_seed": {
                "company_size": "1-10 employees",
                "tech_maturity": "Innovators - Bleeding edge",
                "budget_range": "$500-$5K annual software spend",
                "characteristics": [
                    "Extremely fast decision making",
                    "Willing to take risks on new products",
                    "Heavy product-led growth influence",
                    "Limited budget but high engagement"
                ]
            },
            "startup_series_a": {
                "company_size": "11-50 employees",
                "tech_maturity": "Early Adopter - Modern stack",
                "budget_range": "$5K-$50K annual software spend",
                "characteristics": [
                    "Scaling challenges",
                    "Building out teams and processes",
                    "Need tools that grow with them",
                    "VC-backed with budget to invest"
                ]
            },
        }
        
        # Select segments based on target types
        selected_segments = []
        if "enterprise" in target_segments:
            selected_segments.extend([
                ("Global Enterprise - Tech Forward", segment_templates["enterprise_tech_forward"]),
                ("Enterprise - Traditional", segment_templates["enterprise_conservative"]),
            ])
        if "mid_market" in target_segments:
            selected_segments.extend([
                ("Mid-Market Growth Company", segment_templates["mid_market_growth"]),
                ("Established Mid-Market", segment_templates["mid_market_established"]),
            ])
        if "smb" in target_segments:
            selected_segments.extend([
                ("SMB - Tech Savvy", segment_templates["smb_tech_savvy"]),
                ("SMB - Traditional", segment_templates["smb_traditional"]),
            ])
        
        # Always include startup segments if price allows
        if any(price in pricing_lower for price in ["free", "$0", "trial", "$29", "$49"]):
            selected_segments.extend([
                ("Early-Stage Startup", segment_templates["startup_seed"]),
                ("Series A Startup", segment_templates["startup_series_a"]),
            ])
        
        # Extract industries from input
        industry_list = [i.strip() for i in industries.split(',')[:5]]  # Top 5 industries
        
        # Geographic segments
        geo_segments = [
            "North America (US/Canada)",
            "EMEA (Europe/Middle East/Africa)",
            "APAC (Asia-Pacific)",
            "Latin America"
        ]
        
        # Generate output
        output = "## DEMOGRAPHIC SEGMENTATION RESULTS\n\n"
        output += f"Created {len(selected_segments)} distinct demographic segments.\n\n"
        
        for i, (segment_name, data) in enumerate(selected_segments, 1):
            output += f"### Segment {i}: {segment_name}\n\n"
            output += f"**Company Size:** {data['company_size']}\n"
            output += f"**Technology Maturity:** {data['tech_maturity']}\n"
            output += f"**Budget Range:** {data['budget_range']}\n\n"
            
            output += f"**Target Industries for this Segment:**\n"
            for industry in industry_list[:3]:  # Top 3 industries per segment
                output += f"- {industry}\n"
            
            output += f"\n**Geographic Focus:**\n"
            # Assign geographies based on segment type
            if "Enterprise" in segment_name or "Global" in segment_name:
                relevant_geos = geo_segments[:3]
            elif "Startup" in segment_name:
                relevant_geos = [geo_segments[0], geo_segments[2]]  # US and APAC
            else:
                relevant_geos = [geo_segments[0]]  # North America
            
            for geo in relevant_geos:
                output += f"- {geo}\n"
            
            output += f"\n**Unique Characteristics:**\n"
            for char in data['characteristics']:
                output += f"- {char}\n"
            
            output += "\n---\n\n"
        
        output += "\n## PERSONA GENERATION GUIDANCE\n\n"
        output += "Use these segments to create diverse personas:\n"
        output += "- Ensure representation across ALL company sizes\n"
        output += "- Include both tech-forward and traditional adopters\n"
        output += "- Cover multiple geographic regions\n"
        output += "- Mix decision-makers, influencers, and end users\n"
        output += "- Represent different stages of company maturity\n"
        
        return output
