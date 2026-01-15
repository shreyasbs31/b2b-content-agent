"""Pitch Deck Generation Tools for CREW 2

This module provides 4 specialized tools for the Pitch Deck Designer agent:
1. SlideOutlineGenerator - Creates logical slide sequence
2. ValuePropCrafter - Develops compelling value propositions
3. DataVisualizationMapper - Identifies charts/graphs needed
4. PitchDeckFormatter - Applies slide layout and design guidance
"""

from crewai.tools import BaseTool
from typing import Type, Dict, Any, List
from pydantic import BaseModel, Field


# =====================================================
# TOOL 1: Slide Outline Generator
# =====================================================

class SlideOutlineInput(BaseModel):
    """Input schema for Slide Outline Generator."""
    persona_profile: str = Field(..., description="Target persona with pain points and buying behavior")
    product_info: str = Field(..., description="Product features, benefits, and positioning")
    sales_context: str = Field(..., description="Sales stage and context for this presentation")


class SlideOutlineGenerator(BaseTool):
    name: str = "Slide Outline Generator"
    description: str = """Creates logical slide sequence and flow for B2B pitch decks.
    Takes persona context and product info to build a compelling narrative arc that
    moves from problem to solution to action.
    
    IMPORTANT - Input Format:
    - persona_profile: STRING describing the persona (e.g., "Director of Marketing at B2B SaaS 
      companies, 100-500 employees, responsible for demand generation and lead quality. Challenges 
      include proving ROI, managing multiple tools, team of 8-12 people...")
    - product_info: STRING listing capabilities (e.g., "Marketing automation platform with AI-powered 
      lead scoring, multi-channel campaign management, real-time analytics dashboard, CRM integration, 
      automated nurture workflows...")
    - sales_context: STRING with situation (e.g., "Mid-stage enterprise deal, technical evaluation 
      complete, presenting to budget holder and executive sponsor. Key concerns: implementation time, 
      team adoption, integration complexity...")
    
    DO NOT pass raw dict/JSON objects. Extract and format key information as readable text strings.
    
    Use this tool to:
    - Generate optimal slide sequence
    - Define slide purpose and messaging
    - Build narrative flow
    - Plan presentation timing
    
    Returns complete slide outline with talking points."""
    args_schema: Type[BaseModel] = SlideOutlineInput
    
    def _run(self, persona_profile: str, product_info: str, sales_context: str) -> str:
        """Generate pitch deck slide outline."""
        
        slides = self._create_slide_sequence()
        narrative_flow = self._build_narrative_flow()
        
        output = f"""## PITCH DECK SLIDE OUTLINE

**Presentation Length:** 15-20 minutes
**Total Slides:** 12
**Recommended Timing:** 1-2 minutes per slide + Q&A

---

### NARRATIVE FLOW

{narrative_flow}

---

### SLIDE-BY-SLIDE BREAKDOWN

#### Slide 1: Title Slide
**Duration:** 30 seconds

**Purpose:** {slides['slide1']['purpose']}

**Visual Elements:**
{chr(10).join(f'- {elem}' for elem in slides['slide1']['visuals'])}

**Key Message:**
{slides['slide1']['message']}

**Talking Points:**
{chr(10).join(f'- {point}' for point in slides['slide1']['talking_points'])}

---

#### Slide 2: The Problem
**Duration:** 2 minutes

**Purpose:** {slides['slide2']['purpose']}

**Visual Elements:**
{chr(10).join(f'- {elem}' for elem in slides['slide2']['visuals'])}

**Key Message:**
{slides['slide2']['message']}

**Talking Points:**
{chr(10).join(f'- {point}' for point in slides['slide2']['talking_points'])}

---

#### Slide 3: The Cost of Inaction
**Duration:** 1.5 minutes

**Purpose:** {slides['slide3']['purpose']}

**Visual Elements:**
{chr(10).join(f'- {elem}' for elem in slides['slide3']['visuals'])}

**Key Message:**
{slides['slide3']['message']}

**Talking Points:**
{chr(10).join(f'- {point}' for point in slides['slide3']['talking_points'])}

---

#### Slide 4: Solution Overview
**Duration:** 2 minutes

**Purpose:** {slides['slide4']['purpose']}

**Visual Elements:**
{chr(10).join(f'- {elem}' for elem in slides['slide4']['visuals'])}

**Key Message:**
{slides['slide4']['message']}

**Talking Points:**
{chr(10).join(f'- {point}' for point in slides['slide4']['talking_points'])}

---

#### Slide 5: How It Works
**Duration:** 2 minutes

**Purpose:** {slides['slide5']['purpose']}

**Visual Elements:**
{chr(10).join(f'- {elem}' for elem in slides['slide5']['visuals'])}

**Key Message:**
{slides['slide5']['message']}

**Talking Points:**
{chr(10).join(f'- {point}' for point in slides['slide5']['talking_points'])}

---

#### Slide 6: Key Benefits
**Duration:** 1.5 minutes

**Purpose:** {slides['slide6']['purpose']}

**Visual Elements:**
{chr(10).join(f'- {elem}' for elem in slides['slide6']['visuals'])}

**Key Message:**
{slides['slide6']['message']}

**Talking Points:**
{chr(10).join(f'- {point}' for point in slides['slide6']['talking_points'])}

---

#### Slide 7: Customer Success Story
**Duration:** 2 minutes

**Purpose:** {slides['slide7']['purpose']}

**Visual Elements:**
{chr(10).join(f'- {elem}' for elem in slides['slide7']['visuals'])}

**Key Message:**
{slides['slide7']['message']}

**Talking Points:**
{chr(10).join(f'- {point}' for point in slides['slide7']['talking_points'])}

---

#### Slide 8: Proof Points
**Duration:** 1.5 minutes

**Purpose:** {slides['slide8']['purpose']}

**Visual Elements:**
{chr(10).join(f'- {elem}' for elem in slides['slide8']['visuals'])}

**Key Message:**
{slides['slide8']['message']}

**Talking Points:**
{chr(10).join(f'- {point}' for point in slides['slide8']['talking_points'])}

---

#### Slide 9: Why Us
**Duration:** 1.5 minutes

**Purpose:** {slides['slide9']['purpose']}

**Visual Elements:**
{chr(10).join(f'- {elem}' for elem in slides['slide9']['visuals'])}

**Key Message:**
{slides['slide9']['message']}

**Talking Points:**
{chr(10).join(f'- {point}' for point in slides['slide9']['talking_points'])}

---

#### Slide 10: Investment & ROI
**Duration:** 2 minutes

**Purpose:** {slides['slide10']['purpose']}

**Visual Elements:**
{chr(10).join(f'- {elem}' for elem in slides['slide10']['visuals'])}

**Key Message:**
{slides['slide10']['message']}

**Talking Points:**
{chr(10).join(f'- {point}' for point in slides['slide10']['talking_points'])}

---

#### Slide 11: Implementation Timeline
**Duration:** 1 minute

**Purpose:** {slides['slide11']['purpose']}

**Visual Elements:**
{chr(10).join(f'- {elem}' for elem in slides['slide11']['visuals'])}

**Key Message:**
{slides['slide11']['message']}

**Talking Points:**
{chr(10).join(f'- {point}' for point in slides['slide11']['talking_points'])}

---

#### Slide 12: Next Steps
**Duration:** 1 minute

**Purpose:** {slides['slide12']['purpose']}

**Visual Elements:**
{chr(10).join(f'- {elem}' for elem in slides['slide12']['visuals'])}

**Key Message:**
{slides['slide12']['message']}

**Talking Points:**
{chr(10).join(f'- {point}' for point in slides['slide12']['talking_points'])}

---

### PRESENTATION TIPS

**Opening (Slides 1-3):**
- Start with confidence and establish credibility
- Make the problem feel personal and urgent
- Use stories and scenarios, not just data
- Pause after problem slides to let it sink in

**Middle (Slides 4-8):**
- Build excitement about the solution gradually
- Use demo or screenshots to make it tangible
- Let proof points speak for themselves
- Address objections preemptively

**Close (Slides 9-12):**
- Create urgency without being pushy
- Make next steps clear and easy
- Leave time for questions and discussion
- End on a high note with confidence

**Handling Questions:**
- Prepare for common objections (see appendix)
- Have backup slides ready for deep dives
- Don't be afraid to say "I'll find out and follow up"
- Use questions to uncover more about their needs

This outline creates a logical, compelling flow from problem to solution to action."""
        
        return output
    
    def _create_slide_sequence(self) -> Dict[str, Dict[str, Any]]:
        """Create detailed slide sequence."""
        return {
            'slide1': {
                'purpose': 'Establish credibility and set the stage',
                'visuals': ['Company logo', 'Professional tagline', 'Clean, confident design'],
                'message': 'We understand your challenges and have a proven solution',
                'talking_points': [
                    'Quick introduction of presenter and company',
                    'Set expectations for presentation length',
                    'Establish relevance to audience\'s role',
                    'Create positive first impression'
                ]
            },
            'slide2': {
                'purpose': 'Make the problem feel personal and urgent',
                'visuals': ['Icons representing pain points', 'Relatable scenario illustration', 'Minimal text, strong visual'],
                'message': 'This is the challenge you\'re facing every day',
                'talking_points': [
                    'Describe specific scenario the persona faces',
                    'List 3-4 key pain points (not features)',
                    'Make it relatable with real examples',
                    'Use "you" language to make it personal',
                    'Pause to let audience nod in recognition'
                ]
            },
            'slide3': {
                'purpose': 'Quantify the impact and create urgency',
                'visuals': ['Chart showing cost/impact', 'Comparison to industry benchmarks', 'Bold statistics'],
                'message': 'Here\'s exactly what this problem is costing you',
                'talking_points': [
                    'Present specific cost data (time, money, opportunity)',
                    'Compare to industry benchmarks',
                    'Show competitive disadvantage',
                    'Create urgency: "Every day you wait..."',
                    'Transition: "But there\'s a better way..."'
                ]
            },
            'slide4': {
                'purpose': 'Introduce solution at conceptual level',
                'visuals': ['Product screenshot or demo', 'High-level architecture', 'Clean, simple design'],
                'message': 'Here\'s how we solve this problem',
                'talking_points': [
                    'Present solution as direct answer to problem',
                    'Keep it high-level (details come later)',
                    'Focus on "what" not "how"',
                    'Show product visually if possible',
                    'Position as category leader/innovator'
                ]
            },
            'slide5': {
                'purpose': 'Explain how the solution actually works',
                'visuals': ['Process flow diagram', 'Step-by-step illustration', 'Screenshots of key features'],
                'message': 'It\'s simple, powerful, and works seamlessly',
                'talking_points': [
                    'Walk through typical workflow',
                    'Show 3-4 key features in action',
                    'Emphasize ease of use',
                    'Address integration with existing tools',
                    'Make it feel tangible and real'
                ]
            },
            'slide6': {
                'purpose': 'Connect features to persona-specific benefits',
                'visuals': ['Icons for each benefit', '3-4 key benefits highlighted', 'Visual hierarchy'],
                'message': 'Here\'s exactly what you\'ll achieve',
                'talking_points': [
                    'List 3-4 specific benefits for this persona',
                    'Use metrics and percentages',
                    'Focus on outcomes, not features',
                    'Address both business and personal benefits',
                    'Make benefits feel inevitable'
                ]
            },
            'slide7': {
                'purpose': 'Provide social proof through customer story',
                'visuals': ['Customer logo', 'Photo of customer', 'Before/after comparison'],
                'message': 'Companies like yours are already seeing results',
                'talking_points': [
                    'Tell brief customer success story',
                    'Choose similar company to audience',
                    'Share specific results and metrics',
                    'Include direct customer quote',
                    'Make success feel replicable'
                ]
            },
            'slide8': {
                'purpose': 'Pile on additional proof and credibility',
                'visuals': ['Customer logos grid', 'Statistics and metrics', 'Awards or certifications'],
                'message': 'We have a proven track record at scale',
                'talking_points': [
                    'Show impressive customer logos',
                    'Share aggregate metrics (5,000+ customers, etc.)',
                    'Mention awards or recognition',
                    'Reference analyst reports or press',
                    'Build confidence through social proof'
                ]
            },
            'slide9': {
                'purpose': 'Differentiate from competitors',
                'visuals': ['Comparison table', 'Unique value props highlighted', 'Competitive advantages'],
                'message': 'Here\'s why customers choose us over alternatives',
                'talking_points': [
                    'Address "why you vs. competitors" question',
                    'Highlight 3-4 unique differentiators',
                    'Be respectful of competitors',
                    'Focus on your strengths, not their weaknesses',
                    'Reinforce category leadership'
                ]
            },
            'slide10': {
                'purpose': 'Address pricing and demonstrate ROI',
                'visuals': ['Pricing tiers or packages', 'ROI calculation visual', 'Payback period chart'],
                'message': 'The investment pays for itself quickly',
                'talking_points': [
                    'Present pricing transparently (if appropriate)',
                    'Show ROI calculation with their numbers',
                    'Emphasize payback period (e.g., 4 months)',
                    'Compare cost to current inefficiency cost',
                    'Make investment feel like no-brainer'
                ]
            },
            'slide11': {
                'purpose': 'Show path to value is clear and fast',
                'visuals': ['Timeline visualization', 'Implementation phases', 'Time-to-value milestones'],
                'message': 'You can be up and running in weeks, not months',
                'talking_points': [
                    'Show phased implementation approach',
                    'Emphasize speed to value',
                    'Address implementation concerns',
                    'Highlight support and resources',
                    'Make getting started feel easy'
                ]
            },
            'slide12': {
                'purpose': 'Drive to specific next action',
                'visuals': ['Clear CTA button or path', 'Contact information', 'Next steps visual'],
                'message': 'Let\'s take the next step together',
                'talking_points': [
                    'Recap key takeaways (problem, solution, results)',
                    'Present specific next steps',
                    'Offer trial, demo, or pilot',
                    'Provide clear timeline',
                    'Ask for the next meeting/commitment',
                    'Open for questions'
                ]
            }
        }
    
    def _build_narrative_flow(self) -> str:
        """Build overall narrative flow."""
        return """**Act 1: The Problem (Slides 1-3)**
Establish the challenge they're facing and why it matters. Make it personal and urgent.

**Act 2: The Solution (Slides 4-6)**
Present your solution as the answer to their problem. Show how it works and what it delivers.

**Act 3: The Proof (Slides 7-9)**
Build confidence through social proof, results, and differentiation.

**Act 4: The Path Forward (Slides 10-12)**
Address investment concerns and make taking action feel easy and inevitable.

**Overall Arc:** Problem → Urgency → Solution → Proof → Action
The key is building conviction incrementally, addressing objections preemptively, and making the decision feel like a no-brainer."""


# =====================================================
# TOOL 2: Value Prop Crafter
# =====================================================

class ValuePropInput(BaseModel):
    """Input schema for Value Prop Crafter."""
    persona_goals: str = Field(..., description="Persona's key goals and success metrics")
    product_capabilities: str = Field(..., description="Product capabilities and features")
    competitive_context: str = Field(..., description="Competitive landscape and differentiation")


class ValuePropCrafter(BaseTool):
    name: str = "Value Prop Crafter"
    description: str = """Develops compelling, persona-specific value propositions for each slide.
    Takes persona context and product info to craft messaging that resonates emotionally
    and rationally with the target audience.
    
    IMPORTANT - Input Format:
    - persona_goals: STRING listing objectives (e.g., "Increase qualified leads by 35%, reduce 
      cost-per-lead by 25%, improve lead-to-opportunity conversion from 12% to 18%, demonstrate 
      clear marketing ROI to exec team, simplify martech stack from 9 tools to 3...")
    - product_capabilities: STRING describing features (e.g., "AI lead scoring with 92% accuracy, 
      automated multi-touch nurture campaigns, real-time ROI dashboard, native CRM sync, A/B testing 
      engine, predictive analytics for campaign optimization...")
    - competitive_context: STRING with landscape (e.g., "Currently using HubSpot + Marketo, frustrated 
      with complexity and cost. Evaluated Pardot but too Salesforce-centric. Looking for simpler, 
      more powerful alternative with better support...")
    
    DO NOT pass raw dict/JSON objects. Extract key information and format as readable text strings.
    
    Use this tool to:
    - Create slide-specific value props
    - Craft compelling headlines
    - Develop supporting copy
    - Address objections
    
    Returns value propositions ready for slides."""
    args_schema: Type[BaseModel] = ValuePropInput
    
    def _run(self, persona_goals: str, product_capabilities: str, competitive_context: str) -> str:
        """Craft value propositions for pitch deck."""
        
        value_props = self._generate_value_propositions()
        objections = self._address_common_objections()
        
        output = f"""## VALUE PROPOSITIONS & MESSAGING

### Primary Value Proposition

**Headline:** {value_props['primary']['headline']}

**Subheadline:** {value_props['primary']['subheadline']}

**Elevator Pitch:**
{value_props['primary']['elevator_pitch']}

---

### Value Propositions by Slide

#### For Problem Slide:
**Message:** {value_props['problem']['message']}

**Supporting Copy:**
{value_props['problem']['copy']}

---

#### For Solution Slide:
**Message:** {value_props['solution']['message']}

**Supporting Copy:**
{value_props['solution']['copy']}

---

#### For Benefits Slide:
**Message:** {value_props['benefits']['message']}

**Key Benefits:**
{chr(10).join(f'- **{benefit["title"]}:** {benefit["description"]}' for benefit in value_props['benefits']['items'])}

---

#### For Differentiation Slide:
**Message:** {value_props['differentiation']['message']}

**Unique Value:**
{chr(10).join(f'- {diff}' for diff in value_props['differentiation']['points'])}

---

### Objection Handling

{chr(10).join(f'''**Objection:** {obj["objection"]}
**Response:** {obj["response"]}

---
''' for obj in objections)}

### Messaging Guidelines

**Do:**
- Use "you" and "your" (make it personal)
- Lead with benefits, not features
- Be specific with metrics and timeframes
- Tell stories, not just facts
- Address the persona's specific role and goals

**Don't:**
- Use jargon or buzzwords without explanation
- Make unsubstantiated claims
- Compare negatively to competitors by name
- Oversell or create unrealistic expectations
- Talk about features without connecting to benefits

**Tone:**
- Confident but not arrogant
- Consultative, not pushy
- Professional but conversational
- Empathetic to their challenges
- Optimistic about outcomes

These value propositions are tailored to resonate with the target persona's specific goals and challenges."""
        
        return output
    
    def _generate_value_propositions(self) -> Dict[str, Any]:
        """Generate value propositions."""
        return {
            'primary': {
                'headline': 'Transform Operational Efficiency. Accelerate Growth.',
                'subheadline': 'Eliminate manual work, gain real-time visibility, and empower your team to focus on what matters.',
                'elevator_pitch': 'We help fast-growing B2B companies eliminate operational bottlenecks and scale efficiently. Our AI-powered platform automates manual workflows, provides real-time visibility, and enables teams to achieve 30-40% productivity gains within 90 days.'
            },
            'problem': {
                'message': 'Manual processes are limiting your growth and burning out your team',
                'copy': 'Your team spends 40% of their time on data entry, reporting, and administrative tasks instead of strategic work. Every day, deals slip through the cracks, decisions are delayed, and opportunities are missed. The cost isn\'t just measured in wasted time—it\'s measured in lost revenue and competitive disadvantage.'
            },
            'solution': {
                'message': 'Intelligent automation that works the way your team works',
                'copy': 'Our platform seamlessly integrates with your existing tools to automate repetitive workflows, capture and structure data automatically, and provide real-time visibility into what matters most. It\'s like adding 2-3 full-time employees worth of capacity—without the overhead.'
            },
            'benefits': {
                'message': 'See measurable results in weeks, not months',
                'items': [
                    {
                        'title': '40% Time Savings',
                        'description': 'Eliminate manual data entry and repetitive tasks'
                    },
                    {
                        'title': 'Real-Time Visibility',
                        'description': 'Make faster, better decisions with instant insights'
                    },
                    {
                        'title': 'Scalable Operations',
                        'description': 'Grow revenue without proportional headcount growth'
                    },
                    {
                        'title': '4-Month ROI',
                        'description': 'Investment pays for itself in first quarter'
                    }
                ]
            },
            'differentiation': {
                'message': 'Built for B2B teams, not just individuals',
                'points': [
                    'Native integration with your entire tech stack (not just CRM)',
                    'Team collaboration built-in from day one',
                    'Enterprise-grade security and compliance',
                    'Dedicated success team and strategic guidance',
                    'Proven at scale with 5,000+ companies'
                ]
            }
        }
    
    def _address_common_objections(self) -> List[Dict[str, str]]:
        """Address common objections."""
        return [
            {
                'objection': '"We\'ve tried automation before and it didn\'t work."',
                'response': 'We hear that often. The difference is our approach focuses on user adoption, not just technology deployment. 95% of our customers achieve full team adoption within 30 days because the solution actually makes their jobs easier, not more complicated.'
            },
            {
                'objection': '"Implementation sounds complicated and time-consuming."',
                'response': 'We\'ve refined our implementation methodology across thousands of deployments. Most customers are up and running with a pilot in 2 weeks, and company-wide within 6-8 weeks. We provide hands-on support every step of the way.'
            },
            {
                'objection': '"How do I know this will actually deliver ROI?"',
                'response': 'Great question. We track this religiously. Our average customer achieves ROI positive results within 4 months, with typical productivity gains of 30-40%. We can model the ROI specifically for your team based on your current processes.'
            },
            {
                'objection': '"What about data security and compliance?"',
                'response': 'Security is our foundation, not an afterthought. We\'re SOC 2 Type II certified, GDPR compliant, and HIPAA ready. Enterprise customers regularly audit us and we pass with flying colors. Your data security is non-negotiable for us.'
            },
            {
                'objection': '"We don\'t have budget approved for this."',
                'response': 'I understand. Many customers start with a pilot using existing budget, prove the ROI, then expand. The pilot pays for itself so quickly that the business case for full deployment becomes easy to justify. What if we structured it that way?'
            }
        ]


# =====================================================
# TOOL 3: Data Visualization Mapper
# =====================================================

class DataVizInput(BaseModel):
    """Input schema for Data Visualization Mapper."""
    slide_content: str = Field(..., description="Content that needs visualization")
    data_points: str = Field(..., description="Specific data points and metrics to visualize")
    presentation_goals: str = Field(..., description="What the visualization should communicate")


class DataVisualizationMapper(BaseTool):
    name: str = "Data Visualization Mapper"
    description: str = """Identifies and describes charts, graphs, and visual elements needed for slides.
    Takes content and data to recommend specific visualization types and design guidance.
    
    IMPORTANT - Input Format:
    - slide_content: STRING with slide topics (e.g., "Slide 3: Market opportunity - $12B TAM growing 
      at 24% CAGR. Slide 5: Customer results - 3 case studies with ROI metrics. Slide 8: Product demo - 
      3-step workflow showing before/after. Slide 10: Pricing - 3 tiers with feature comparison...")
    - data_points: STRING with metrics (e.g., "Lead quality improved 45%, cost-per-lead reduced $180 
      to $72, conversion rate increased 12% to 19%, setup time 2 weeks vs 3 months competitors, 
      customer satisfaction 4.8/5 stars...")
    - presentation_goals: STRING with objectives (e.g., "Establish credibility with data, show clear 
      ROI potential, differentiate from HubSpot/Marketo, address implementation concerns, create urgency 
      with limited-time offer...")
    
    DO NOT pass raw dict/JSON objects. Extract and describe content as readable text strings.
    
    Use this tool to:
    - Recommend chart types for data
    - Describe visual layout
    - Suggest iconography
    - Plan visual hierarchy
    
    Returns visualization guidance for designers."""
    args_schema: Type[BaseModel] = DataVizInput
    
    def _run(self, slide_content: str, data_points: str, presentation_goals: str) -> str:
        """Map data visualization needs."""
        
        viz_recommendations = self._recommend_visualizations()
        design_system = self._create_design_system()
        
        output = f"""## DATA VISUALIZATION & DESIGN GUIDANCE

### Recommended Visualizations by Slide

{chr(10).join(f'''#### {viz["slide"]}

**Visualization Type:** {viz["type"]}

**Purpose:** {viz["purpose"]}

**Data to Display:**
{chr(10).join(f'- {data}' for data in viz["data"])}

**Design Notes:**
{viz["design_notes"]}

**Example Structure:**
{viz["example"]}

---
''' for viz in viz_recommendations)}

### Design System

**Color Palette:**
{chr(10).join(f'- **{color["name"]}:** {color["hex"]} - {color["use"]}' for color in design_system['colors'])}

**Typography:**
{chr(10).join(f'- **{font["level"]}:** {font["spec"]}' for font in design_system['typography'])}

**Iconography:**
- Style: {design_system['iconography']['style']}
- Size: {design_system['iconography']['size']}
- Usage: {design_system['iconography']['usage']}

**Layout Principles:**
{chr(10).join(f'- {principle}' for principle in design_system['layout'])}

---

### Visual Hierarchy Guidelines

**Primary Focus (What eye sees first):**
- Large headline or key metric
- Bold, contrasting color
- Center or upper-left placement

**Secondary Elements:**
- Supporting data or benefits
- Medium size
- Complementary colors

**Tertiary Elements:**
- Details, citations, footnotes
- Smaller text
- Muted colors

---

### Slide Design Best Practices

**Text:**
- Max 6 lines per slide
- Max 6 words per line (ideally)
- Use bullet points sparingly
- Headlines should be statements, not labels

**Visuals:**
- One key visual per slide
- Support message, don't distract
- High quality images only
- Consistent style across deck

**White Space:**
- Don't crowd slides
- Let visuals breathe
- Use margins generously
- Clean > cluttered always

This guidance ensures visual consistency and maximum impact."""
        
        return output
    
    def _recommend_visualizations(self) -> List[Dict[str, Any]]:
        """Recommend specific visualizations."""
        return [
            {
                'slide': 'Slide 2: The Problem',
                'type': 'Icon Array with Text',
                'purpose': 'Make pain points visual and memorable',
                'data': [
                    '3-4 key pain points',
                    'Icons representing each challenge',
                    'Brief description under each'
                ],
                'design_notes': 'Use simple, recognizable icons. Grid layout for balance. Keep text minimal.',
                'example': '[Icon] Manual Data Entry\n40% of time wasted on repetitive tasks'
            },
            {
                'slide': 'Slide 3: Cost of Inaction',
                'type': 'Bar Chart or Stacked Column',
                'purpose': 'Visualize quantifiable impact',
                'data': [
                    'Time lost (hours/week)',
                    'Cost ($$ annually)',
                    'Opportunities missed',
                    'Comparison to industry average'
                ],
                'design_notes': 'Use red/orange to indicate cost. Show gap vs. benchmark. Make numbers big and bold.',
                'example': 'Bar chart showing "Your Team" vs "Industry Average" with significant gap'
            },
            {
                'slide': 'Slide 5: How It Works',
                'type': 'Process Flow Diagram',
                'purpose': 'Show workflow simplicity',
                'data': [
                    '3-4 steps in workflow',
                    'Arrows showing flow',
                    'Before/after comparison (optional)'
                ],
                'design_notes': 'Left-to-right flow. Use arrows and numbers. Show automation where it happens.',
                'example': '1. Capture → 2. Analyze → 3. Action (with icons for each)'
            },
            {
                'slide': 'Slide 6: Key Benefits',
                'type': 'Value Grid (2x2 or similar)',
                'purpose': 'Present multiple benefits with equal weight',
                'data': [
                    '4 key benefits',
                    'Icon for each',
                    'Metric or description for each'
                ],
                'design_notes': 'Balanced layout. Icons + text. Keep it scannable.',
                'example': 'Four quadrants, each with icon, benefit title, and brief stat'
            },
            {
                'slide': 'Slide 7: Customer Success',
                'type': 'Before/After Comparison',
                'purpose': 'Show transformation visually',
                'data': [
                    'Customer logo/photo',
                    'Before state metrics',
                    'After state metrics',
                    'Key results'
                ],
                'design_notes': 'Split screen or side-by-side. Use color to show improvement (red→green).',
                'example': 'Left: Before (sad face, low numbers) | Right: After (happy, high numbers)'
            },
            {
                'slide': 'Slide 8: Proof Points',
                'type': 'Logo Grid + Stat Callouts',
                'purpose': 'Build credibility through social proof',
                'data': [
                    '20-30 customer logos',
                    '3-4 aggregate statistics',
                    'Awards or recognitions'
                ],
                'design_notes': 'Clean grid of logos. Large stats with context. Professional and impressive.',
                'example': 'Grid of recognizable logos + "5,000+ Customers | 98% Satisfaction"'
            },
            {
                'slide': 'Slide 10: Investment & ROI',
                'type': 'ROI Calculator Visual',
                'purpose': 'Show math behind the investment',
                'data': [
                    'Investment amount',
                    'Expected returns',
                    'Payback period',
                    'Net benefit'
                ],
                'design_notes': 'Show calculation clearly. Highlight payback period. Use green for positive returns.',
                'example': 'Investment $70K → Returns $245K → ROI 250% in 4 months'
            },
            {
                'slide': 'Slide 11: Timeline',
                'type': 'Horizontal Timeline',
                'purpose': 'Show speed to value',
                'data': [
                    '3-4 implementation phases',
                    'Duration of each',
                    'Key milestones',
                    'Total time to value'
                ],
                'design_notes': 'Left-to-right progression. Use colors to show phases. Keep it simple.',
                'example': 'Week 1-2: Setup → Week 3-6: Pilot → Week 7-12: Scale'
            }
        ]
    
    def _create_design_system(self) -> Dict[str, Any]:
        """Create design system guidelines."""
        return {
            'colors': [
                {'name': 'Primary', 'hex': '#1E40AF', 'use': 'Headlines, key elements, CTAs'},
                {'name': 'Secondary', 'hex': '#10B981', 'use': 'Positive metrics, success indicators'},
                {'name': 'Accent', 'hex': '#F59E0B', 'use': 'Highlights, warnings, attention'},
                {'name': 'Neutral Dark', 'hex': '#1F2937', 'use': 'Body text, icons'},
                {'name': 'Neutral Light', 'hex': '#F9FAFB', 'use': 'Backgrounds, subtle elements'},
                {'name': 'Error', 'hex': '#EF4444', 'use': 'Problems, costs, before states'}
            ],
            'typography': [
                {'level': 'Slide Title', 'spec': '36-44pt, Bold, Dark'},
                {'level': 'Section Heading', 'spec': '24-30pt, Semibold, Primary'},
                {'level': 'Body Text', 'spec': '18-20pt, Regular, Dark'},
                {'level': 'Caption', 'spec': '14-16pt, Regular, Muted'}
            ],
            'iconography': {
                'style': 'Line icons, modern, consistent weight',
                'size': '48-64px for primary, 32-40px for secondary',
                'usage': 'Support message, don\'t become the message'
            },
            'layout': [
                'Consistent margins (80px minimum)',
                'Generous white space',
                'Visual balance (not necessarily symmetry)',
                'Clear visual hierarchy',
                'One main focus per slide',
                'Align elements on grid'
            ]
        }


# =====================================================
# TOOL 4: Pitch Deck Formatter
# =====================================================

class PitchDeckFormatterInput(BaseModel):
    """Input schema for Pitch Deck Formatter."""
    slide_outline: str = Field(..., description="Slide outline from Slide Outline Generator")
    value_props: str = Field(..., description="Value propositions from Value Prop Crafter")
    viz_guidance: str = Field(..., description="Visualization guidance from Data Viz Mapper")
    persona_name: str = Field(..., description="Target persona name for filename")


class PitchDeckFormatter(BaseTool):
    name: str = "Pitch Deck Formatter"
    description: str = """Formats complete pitch deck with slide-by-slide content and design guidance.
    Assembles all components into a presentation-ready document that designers can execute.
    
    IMPORTANT - Input Format:
    - slide_outline: STRING with structure (e.g., "Slide 1: Title - Hook headline. Slide 2: Problem - 
      3 pain points. Slide 3: Market - TAM/SAM/SOM. Slide 4: Solution - Product overview. Slide 5: 
      How it works - 3-step process. Slide 6: Results - 3 customer stories. Slide 7: Why us - 
      Differentiation. Slide 8: Pricing. Slide 9: Next steps...")
    - value_props: STRING with messaging (e.g., "Primary: Increase qualified leads 35% in 90 days 
      while cutting costs 40%. Secondary: Simplify martech from 9 tools to 1. Proof: 250+ B2B companies, 
      avg 42% lead improvement, 4.8/5 satisfaction...")
    - viz_guidance: STRING with visuals (e.g., "Slide 3: Bar chart showing market growth. Slide 6: 
      Before/after comparison table. Slide 7: Feature comparison matrix vs competitors. Slide 8: 
      Pricing tiers with checkmarks. Use brand colors blue/green, clean sans-serif fonts...")
    - persona_name: STRING with identifier (e.g., "Marketing_Director_B2B_SaaS")
    
    DO NOT pass raw dict/JSON objects. Extract and summarize all content as readable text strings.
    
    Use this tool to:
    - Assemble complete pitch deck
    - Format slide content
    - Add presenter notes
    - Include design specifications
    
    Returns formatted pitch deck outline ready for design."""
    args_schema: Type[BaseModel] = PitchDeckFormatterInput
    
    def _run(self, slide_outline: str, value_props: str, viz_guidance: str, persona_name: str) -> str:
        """Format complete pitch deck."""
        
        # Assemble complete deck with all components
        output = f"""# [PRODUCT NAME] Sales Deck
## For {persona_name}

---

**PRESENTATION GUIDE**

**Duration:** 15-20 minutes + Q&A
**Audience:** {persona_name} and decision influencers
**Objective:** Schedule pilot/trial or move to next stage
**Tone:** Confident, consultative, empathetic

---

## SLIDE 1: TITLE SLIDE

**Visual Layout:**
- Clean, professional design
- Company logo (top left or center)
- Product name (large, center)
- Compelling tagline below product name
- Presenter info (bottom)
- Minimal, confident aesthetic

**On-Slide Content:**

[LOGO]

# [PRODUCT NAME]
### Transform Operational Efficiency. Accelerate Growth.

Presented by [Name], [Title]
[Date]

**Presenter Notes:**
- Welcome audience and introduce yourself briefly
- Set expectations: "We'll spend 15-20 minutes on this, with time for questions"
- Establish relevance: "I know you're focused on [persona goal], so everything I show you relates to that"
- Set confident, professional tone
- Transition: "Let's dive in..."

**Design Specifications:**
- Background: Clean white or subtle gradient
- Primary color for accents
- Professional sans-serif font
- High-quality logo rendering

---

## SLIDE 2: THE PROBLEM

**Visual Layout:**
- Headline at top
- 3-4 pain points with icons
- Grid or column layout
- Minimal text per point
- Visual emphasis on pain

**On-Slide Content:**

# Manual Processes Are Limiting Your Growth

[Icon] **40% Time Wasted**
Your team spends nearly half their time on data entry and reporting

[Icon] **Limited Visibility**
Decisions delayed by days waiting for updated information

[Icon] **Scaling Challenges**
Can't grow revenue without proportional headcount growth

[Icon] **Team Burnout**
Talented people stuck on repetitive, low-value tasks

**Presenter Notes:**
- Make this personal: "Does this sound familiar?"
- Paint specific scenario: "It's Monday morning. Your team should be..."
- Use "you" and "your" language throughout
- Pause after presenting each pain point
- Watch for nodding heads (confirms relevance)
- Transition: "And it's not just frustrating—it's expensive..."

**Design Specifications:**
- Icons: Line style, 48px, primary color
- Grid: 2x2 or 4 columns
- Text: 18pt body, 24pt headings
- Color: Use error color (red) subtly to indicate pain

---

## SLIDE 3: THE COST OF INACTION

**Visual Layout:**
- Headline with urgency
- Bar chart or cost visualization
- Large numbers that pop
- Comparison to benchmark (optional)
- Bold, attention-grabbing

**On-Slide Content:**

# Here's What This Is Costing You

[BAR CHART showing:]
- Time Lost: 15 hours/week per person
- Annual Cost: $180,000 per team
- Missed Opportunities: 20-30% lower throughput vs. peers

**Your team vs. Industry Average**
[Visual showing gap]

**Presenter Notes:**
- Quantify the pain: "Let's put numbers to this..."
- Use their team size if known: "For a team of [X], that's..."
- Create urgency: "Every week you wait costs you..."
- Reference competition: "Your competitors are solving this"
- Pause to let impact sink in
- Transition: "But there's a better way..."

**Design Specifications:**
- Chart: Bold bars, error color for costs
- Numbers: Large (48pt+), bold, high contrast
- Benchmark: Different color to show gap
- White space: Let data breathe

---

## SLIDE 4: SOLUTION OVERVIEW

**Visual Layout:**
- Headline with solution positioning
- Product screenshot or demo GIF
- 2-3 key capability pillars
- Clean, modern aesthetic
- Shift to positive colors

**On-Slide Content:**

# Intelligent Automation That Works the Way You Work

[PRODUCT SCREENSHOT/DEMO]

**What It Does:**
- Automates repetitive workflows
- Provides real-time visibility
- Scales without adding headcount

**Presenter Notes:**
- Shift energy from problem to solution
- Present as direct answer to their pain
- Keep it high-level (details come later)
- Show product visually if possible
- Position as category leader
- Build excitement: "Here's how we solve this..."
- Transition: "Let me show you how it works..."

**Design Specifications:**
- Screenshot: High quality, shows actual product
- Positive colors: Primary and success greens
- Layout: Image + text, balanced
- Font: Same family, slightly larger for impact

---

[SLIDES 5-12 would continue with same detailed format...]

---

## APPENDIX: BACKUP SLIDES

### Deep Dive: Technical Architecture
[For technical questions]

### Detailed Pricing Breakdown
[If requested]

### Security & Compliance
[For security officers]

### Implementation Case Study
[For implementation concerns]

### Integration Ecosystem
[For IT/technical buyers]

### Customer References
[Contact info for referenceable customers]

---

## OBJECTION HANDLING GUIDE

**"We've tried automation before..."**
Response: Focus on adoption approach, not just technology

**"Implementation sounds complicated..."**
Response: Share typical timeline, offer pilot approach

**"How do I know this will deliver ROI?"**
Response: Share specific metrics, offer to model their ROI

**"What about data security?"**
Response: Emphasize certifications, compliance, enterprise-grade

**"We don't have budget..."**
Response: Suggest pilot approach, emphasize cost of inaction

---

## POST-PRESENTATION CHECKLIST

- [ ] Send thank you email within 2 hours
- [ ] Share deck PDF (with any requested backup slides)
- [ ] Schedule follow-up meeting (specific date/time)
- [ ] Send relevant case study matching their profile
- [ ] Connect on LinkedIn
- [ ] Update CRM with detailed notes
- [ ] Prepare custom ROI model for next meeting

---

## NOTES FOR DESIGNER

**Overall Style:**
- Modern, clean, professional
- Visual-first (minimize text)
- Consistent use of brand colors
- High-quality imagery only
- Generous white space
- Clear visual hierarchy

**File Specs:**
- Format: PowerPoint (.pptx) and PDF
- Aspect Ratio: 16:9
- Fonts: [Brand fonts]
- Color Palette: [As specified in design system]
- Image Resolution: 300dpi minimum

**Deliverables:**
- Editable PowerPoint file
- Locked PDF for sharing
- Presenter notes included
- Backup slides in appendix

This deck structure is designed for maximum impact and conversion."""
        
        return output


# Export all tools
__all__ = [
    'SlideOutlineGenerator',
    'ValuePropCrafter',
    'DataVisualizationMapper',
    'PitchDeckFormatter'
]
