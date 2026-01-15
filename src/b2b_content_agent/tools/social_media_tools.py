"""Social Media Content Generation Tools for CREW 2

This module provides 4 specialized tools for the Social Media Specialist agent:
1. HookGenerator - Creates attention-grabbing opening hooks
2. StoryAngleIdentifier - Finds compelling story angles for posts
3. HashtagResearcher - Generates relevant B2B hashtag strategies
4. SocialPostFormatter - Formats complete social media posts
"""

from crewai.tools import BaseTool
from typing import Type, Dict, Any, List
from pydantic import BaseModel, Field
import random


# =====================================================
# TOOL 1: Hook Generator
# =====================================================

class HookInput(BaseModel):
    """Input schema for Hook Generator."""
    persona_profile: str = Field(..., description="Target persona with pain points and role")
    content_theme: str = Field(..., description="Theme or topic for the post")
    platform: str = Field(..., description="Social platform (LinkedIn, Twitter, etc.)")


class HookGenerator(BaseTool):
    name: str = "Hook Generator"
    description: str = """Creates attention-grabbing opening hooks for B2B social media posts.
    Takes persona context and content theme to craft hooks that stop scrolling and
    drive engagement.
    
    IMPORTANT - Input Format:
    - persona_profile: STRING describing audience (e.g., "VP of Sales at mid-market companies, 
      time-starved and skeptical of marketing hype, values data and peer recommendations, 
      active on LinkedIn during morning commute 7-9am...")
    - content_theme: STRING with topic (e.g., "Overcoming sales team resistance to new CRM 
      adoption - addressing change management, showing quick wins, building champions internally...")
    - platform: STRING specifying channel (e.g., "LinkedIn", "Twitter", "Facebook")
    
    DO NOT pass raw dict/JSON objects. Extract key context and format as readable text strings.
    
    Use this tool to:
    - Generate platform-specific hooks
    - Create pattern interrupts
    - Test multiple hook styles
    - Optimize for engagement
    
    Returns 10+ hook variations to choose from."""
    args_schema: Type[BaseModel] = HookInput
    
    def _run(self, persona_profile: str, content_theme: str, platform: str) -> str:
        """Generate attention-grabbing hooks."""
        
        hooks = self._generate_hook_variations()
        platform_tips = self._get_platform_guidance(platform)
        
        output = f"""## SOCIAL MEDIA HOOKS

**Platform:** {platform}
**Theme:** {content_theme}
**Target:** {persona_profile}

---

### Hook Style Guide

{platform_tips}

---

### Hook Variations

{chr(10).join(f'''#### Style {i+1}: {hook["style"]}

**Hook:**
{hook["text"]}

**Why It Works:**
{hook["why"]}

**Best Used For:**
{hook["use_case"]}

---
''' for i, hook in enumerate(hooks))}

### Testing Recommendations

**A/B Test These Combinations:**
1. Question hook vs. Bold statement
2. Data-driven vs. Story-driven
3. Problem-focused vs. Solution-focused
4. Personal vs. Industry perspective

**Track These Metrics:**
- Impressions (reach)
- Engagement rate (likes, comments, shares)
- Click-through rate (if applicable)
- Time to first engagement

**Iterate Based On:**
- Which styles get most saves/shares
- Which generate quality comments (not just likes)
- Which drive profile visits or website clicks
- Which resonate with target persona specifically

Use these hooks as starting points and adapt based on your brand voice and what resonates with your specific audience."""
        
        return output
    
    def _generate_hook_variations(self) -> List[Dict[str, Any]]:
        """Generate different hook styles."""
        return [
            {
                'style': 'Provocative Question',
                'text': 'What if I told you that 40% of your team\'s time is completely wasted?\n\nAnd not on things that matter.',
                'why': 'Questions create curiosity gap, forces reader to think',
                'use_case': 'Problem awareness posts, thought leadership'
            },
            {
                'style': 'Bold Contrarian Statement',
                'text': 'Most "productivity tools" actually make teams less productive.\n\nHere\'s why:',
                'why': 'Challenges conventional wisdom, creates controversy',
                'use_case': 'Thought leadership, differentiation, hot takes'
            },
            {
                'style': 'Specific Data Point',
                'text': '87% of sales teams say manual data entry is their #1 time drain.\n\nYet only 12% have automated it.',
                'why': 'Numbers add credibility, creates "aha" moment',
                'use_case': 'Industry insights, problem validation, research shares'
            },
            {
                'style': 'Personal Story Opening',
                'text': 'I spent 3 hours yesterday on a task that should have taken 10 minutes.\n\nSound familiar?',
                'why': 'Relatability, authenticity, draws reader into narrative',
                'use_case': 'Building connection, humanizing brand, case studies'
            },
            {
                'style': 'Pattern Interrupt',
                'text': 'Stop buying "productivity" software.\n\nStart eliminating work that shouldn\'t exist.',
                'why': 'Unexpected advice, breaks scrolling pattern',
                'use_case': 'Thought leadership, provocative takes, differentiation'
            },
            {
                'style': 'Pain Agitation',
                'text': 'Your team is drowning in manual work.\n\nYour competitors automated it 6 months ago.',
                'why': 'Creates urgency through competitive pressure',
                'use_case': 'Competitive positioning, urgency building'
            },
            {
                'style': 'Surprising Insight',
                'text': 'The fastest growing B2B companies don\'t work harder.\n\nThey eliminate more work.',
                'why': 'Reframes common assumption, creates curiosity',
                'use_case': 'Thought leadership, industry insights, case studies'
            },
            {
                'style': 'List Promise',
                'text': '5 signs your operations can\'t scale:\n\n(#3 is the silent killer)',
                'why': 'Lists are scannable, number creates expectation',
                'use_case': 'Educational content, how-to posts, tips/tricks'
            },
            {
                'style': 'Outcome First',
                'text': 'We helped a SaaS company save 200 hours per month.\n\nWithout hiring anyone.',
                'why': 'Leads with value, creates desire for outcome',
                'use_case': 'Case studies, testimonials, results-focused content'
            },
            {
                'style': 'Empathy Hook',
                'text': 'Being a sales leader shouldn\'t mean being a data entry manager.\n\nBut for most, it does.',
                'why': 'Shows understanding of frustration, builds trust',
                'use_case': 'Building rapport, persona-specific content'
            },
            {
                'style': 'Myth Busting',
                'text': 'Myth: Automation replaces people.\n\nReality: It frees them to do what they do best.',
                'why': 'Addresses objections, educates, reframes',
                'use_case': 'Overcoming objections, educational content'
            },
            {
                'style': 'Future Pacing',
                'text': 'Imagine your team spending zero time on data entry.\n\nThat\'s not a dream. It\'s already happening.',
                'why': 'Creates vision of better future, inspires action',
                'use_case': 'Vision selling, aspiration content, inspiration'
            }
        ]
    
    def _get_platform_guidance(self, platform: str) -> str:
        """Get platform-specific guidance."""
        guidance = {
            'LinkedIn': """**LinkedIn Best Practices:**
- First 2-3 lines are critical (visible before "see more")
- Professional but conversational tone
- Longer form content performs well (1,200-2,000 characters)
- Questions and insights > self-promotion
- Engage with comments within first hour for algorithm boost
- Post 2-4x per week for consistency
- Best times: Tue-Thu, 8-10am or 12-2pm""",
            
            'Twitter': """**Twitter Best Practices:**
- Hook must work in first tweet of thread
- Shorter, punchier than LinkedIn
- Threads perform well for complex topics
- Use line breaks for readability
- Tag relevant accounts (not too many)
- Post 1-3x per day for reach
- Best times: Mon-Fri, 8-10am or 5-6pm""",
            
            'Facebook': """**Facebook Best Practices:**
- More casual, community-oriented tone
- Visual content crucial (image/video)
- Ask questions to drive comments
- Shorter than LinkedIn (500-800 characters)
- Engage with group discussions
- Post 1-2x per day maximum
- Best times: Wed-Fri, 1-3pm"""
        }
        
        return guidance.get(platform, guidance['LinkedIn'])


# =====================================================
# TOOL 2: Story Angle Identifier
# =====================================================

class StoryAngleInput(BaseModel):
    """Input schema for Story Angle Identifier."""
    product_features: str = Field(..., description="Product features and capabilities")
    customer_outcomes: str = Field(..., description="Customer results and testimonials")
    persona_interests: str = Field(..., description="What the persona cares about")


class StoryAngleIdentifier(BaseTool):
    name: str = "Story Angle Identifier"
    description: str = """Identifies compelling story angles for social media content.
    Takes product context and customer outcomes to find angles that resonate
    emotionally and professionally with B2B audiences.
    
    IMPORTANT - Input Format:
    - product_features: STRING listing capabilities (e.g., "Automated data capture from emails/calls, 
      AI-powered deal forecasting, real-time pipeline visibility dashboard, mobile app for field reps, 
      Salesforce/HubSpot integration, custom reporting builder...")
    - customer_outcomes: STRING with results (e.g., "Sales teams spending 60% more time selling vs admin, 
      forecast accuracy improved from 65% to 89%, deal cycle shortened by 23 days, rep satisfaction up 
      4.2 to 4.7/5, $450K additional revenue per rep annually...")
    - persona_interests: STRING with topics (e.g., "Sales productivity, team management, quota attainment, 
      forecast accuracy, work-life balance, career advancement, peer recognition, executive visibility...")
    
    DO NOT pass raw dict/JSON objects. Extract and describe key information as readable text strings.
    
    Use this tool to:
    - Find multiple story angles
    - Match angles to personas
    - Identify emotional triggers
    - Plan content series
    
    Returns 8-10 story angles with execution guidance."""
    args_schema: Type[BaseModel] = StoryAngleInput
    
    def _run(self, product_features: str, customer_outcomes: str, persona_interests: str) -> str:
        """Identify compelling story angles."""
        
        angles = self._generate_story_angles()
        content_calendar = self._create_content_calendar()
        
        output = f"""## STORY ANGLES & CONTENT IDEAS

### Story Angle Library

{chr(10).join(f'''#### Angle {i+1}: {angle["title"]}

**Core Message:**
{angle["message"]}

**Emotional Trigger:**
{angle["emotion"]}

**Best Format:**
{angle["format"]}

**Content Ideas:**
{chr(10).join(f'- {idea}' for idea in angle["ideas"])}

**Call to Action:**
{angle["cta"]}

**Success Metrics:**
{angle["metrics"]}

---
''' for i, angle in enumerate(angles))}

### Content Calendar Framework

{content_calendar}

---

### Angle Selection Guide

**Choose Transformation Stories When:**
- You have strong before/after data
- Customer willing to be featured
- Visual transformation possible
- ROI is impressive

**Choose Thought Leadership When:**
- No specific customer story available
- Industry trends are hot topic
- Establishing expertise is priority
- Controversial take to share

**Choose Behind-the-Scenes When:**
- Building brand authenticity
- Recruiting is secondary goal
- Product development milestone
- Team culture is differentiator

**Choose Problem-Solution When:**
- Awareness building is goal
- Educational content performs well
- Pain point is universal
- Solution is differentiated

**Vary Angles for:**
- Audience fatigue prevention
- Algorithm optimization
- Testing what resonates
- Comprehensive storytelling

Use mix of angles across content calendar to maintain engagement and reach different audience segments."""
        
        return output
    
    def _generate_story_angles(self) -> List[Dict[str, Any]]:
        """Generate story angle options."""
        return [
            {
                'title': 'Customer Transformation',
                'message': 'Real company, real results, real impact',
                'emotion': 'Aspiration, proof, FOMO',
                'format': 'Case study post, customer quote, before/after metrics',
                'ideas': [
                    'How [Company] saved 200 hours/month using [Product]',
                    '"We went from 40 hours to 4 hours per week" - Customer story',
                    'Before and after: A sales team\'s transformation',
                    'Day in the life: Using [Product] at [Customer Company]'
                ],
                'cta': 'See how [Company] achieved similar results',
                'metrics': 'Engagement rate, click-through to case study, demo requests'
            },
            {
                'title': 'Founder/Team Story',
                'message': 'Why we built this, who we are, what drives us',
                'emotion': 'Connection, authenticity, trust',
                'format': 'Personal narrative, team photos, origin story',
                'ideas': [
                    'The problem that obsessed me for 3 years',
                    'Why I left [BigCorp] to build this',
                    'Meet the team building the future of [category]',
                    'The "aha" moment that started it all'
                ],
                'cta': 'Join us on this journey / We\'re hiring',
                'metrics': 'Profile visits, follower growth, application clicks'
            },
            {
                'title': 'Industry Insights',
                'message': 'We understand your world, here\'s what\'s happening',
                'emotion': 'Curiosity, validation, expertise',
                'format': 'Data visualization, trend analysis, hot take',
                'ideas': [
                    '87% of B2B teams are struggling with [problem]',
                    'The future of [category] in 2025: 5 predictions',
                    'Why [common practice] is broken (and what to do instead)',
                    'What the best B2B teams are doing differently'
                ],
                'cta': 'Download full report / Learn more',
                'metrics': 'Shares, comments, engagement rate, downloads'
            },
            {
                'title': 'Problem Awareness',
                'message': 'This is costing you more than you think',
                'emotion': 'Recognition, urgency, frustration',
                'format': 'Pain agitation, cost calculation, competitive comparison',
                'ideas': [
                    'The hidden cost of manual [process]',
                    '5 signs your [system] is holding you back',
                    'Your competitors automated this. Here\'s why it matters.',
                    'How much time does your team waste on [task]?'
                ],
                'cta': 'Calculate your cost / Free assessment',
                'metrics': 'Engagement rate, calculator uses, consultation bookings'
            },
            {
                'title': 'How-To / Educational',
                'message': 'We\'re here to help, no strings attached',
                'emotion': 'Gratitude, trust, reciprocity',
                'format': 'Step-by-step guide, tips thread, video tutorial',
                'ideas': [
                    'How to [solve problem] in 30 minutes',
                    '10 tips for [better outcome] (from 500+ implementations)',
                    'The complete guide to [process improvement]',
                    'Common mistakes when [doing task] and how to avoid them'
                ],
                'cta': 'Save this for later / Share with your team',
                'metrics': 'Saves, shares, comment quality, traffic to blog'
            },
            {
                'title': 'Behind the Product',
                'message': 'See how we\'re innovating for you',
                'emotion': 'Excitement, inclusion, anticipation',
                'format': 'Product demo, feature spotlight, roadmap preview',
                'ideas': [
                    'New feature: What it does and why we built it',
                    'Product demo: Automating [workflow] in 3 clicks',
                    'Coming soon: A sneak peek at what we\'re building',
                    'How we designed [feature] based on customer feedback'
                ],
                'cta': 'Try it now / Join beta / Request demo',
                'metrics': 'Video views, trial signups, feature adoption'
            },
            {
                'title': 'Contrarian Take',
                'message': 'Everyone\'s doing it wrong. Here\'s why.',
                'emotion': 'Intrigue, controversy, superiority',
                'format': 'Opinion piece, myth busting, rant',
                'ideas': [
                    'Unpopular opinion: [Common belief] is backwards',
                    'Why I stopped [common practice] and never looked back',
                    'The [tool/method] everyone uses is actually harmful',
                    'Hot take: [Industry standard] needs to die'
                ],
                'cta': 'Agree or disagree? Let me know.',
                'metrics': 'Comments (especially debates), shares, engagement rate'
            },
            {
                'title': 'Milestone Celebration',
                'message': 'We\'re growing because we\'re solving real problems',
                'emotion': 'Pride, celebration, social proof',
                'format': 'Announcement, thank you post, infographic',
                'ideas': [
                    'We just hit 5,000 customers. Here\'s what we learned.',
                    'Thanks to our community for helping us reach [milestone]',
                    '[Big number] teams automated [process] this year',
                    'From 0 to [milestone] in [timeframe]: Lessons learned'
                ],
                'cta': 'Thank you / Join us / Become customer 5,001',
                'metrics': 'Engagement rate, sentiment, new customer inquiries'
            },
            {
                'title': 'Day in the Life',
                'message': 'See what\'s possible with the right tools',
                'emotion': 'Aspiration, curiosity, relatability',
                'format': 'Narrative post, video, image carousel',
                'ideas': [
                    'A day in the life of a sales manager using [Product]',
                    'Morning routine: From chaos to control',
                    'What it\'s like to never do data entry again',
                    'How [User] spends their time now vs. before'
                ],
                'cta': 'Imagine your day like this / See how',
                'metrics': 'Time on content, engagement rate, demo requests'
            },
            {
                'title': 'Community Content',
                'message': 'You\'re not alone, we\'re in this together',
                'emotion': 'Belonging, validation, community',
                'format': 'Question post, poll, user-generated content',
                'ideas': [
                    'What\'s the most frustrating part of [role]?',
                    'Poll: How many hours do you spend on [task]?',
                    'Share your [tip/hack] in the comments',
                    'Who else feels this way about [situation]?'
                ],
                'cta': 'Comment below / Join the conversation',
                'metrics': 'Comments, engagement rate, community growth'
            }
        ]
    
    def _create_content_calendar(self) -> str:
        """Create content calendar framework."""
        return """**Weekly Content Mix (4 posts/week):**

**Monday:** Industry Insight or Thought Leadership
- Starts week with value
- Drives authority and expertise
- Often most shared content

**Wednesday:** Customer Story or Product Feature
- Mid-week social proof
- Drives consideration and demos
- More sales-oriented

**Thursday:** Educational or How-To
- High-value, shareable
- Builds goodwill
- SEO benefit from links

**Friday:** Community or Behind-the-Scenes
- Casual, human, relatable
- Builds connection
- Weekend engagement

**Monthly Themes:**

**Week 1:** Problem Awareness
Focus on pain points and industry challenges

**Week 2:** Solution Education
How-to content, tips, best practices

**Week 3:** Social Proof
Customer stories, case studies, testimonials

**Week 4:** Product/Company
Features, milestones, behind-the-scenes

**Quarterly Campaigns:**

Q1: New Year optimization ("Make 2025 your most efficient year")
Q2: Mid-year reset ("Mid-year check-in: Are you on track?")
Q3: Fall preparation ("Gear up for Q4 success")
Q4: Year-end reflection ("2025 wins and 2026 goals")

Balance promotional vs. value content: 80% value, 20% promotional"""


# =====================================================
# TOOL 3: Hashtag Researcher
# =====================================================

class HashtagInput(BaseModel):
    """Input schema for Hashtag Researcher."""
    content_topic: str = Field(..., description="Topic or theme of the post")
    target_audience: str = Field(..., description="Target audience characteristics")
    platform: str = Field(..., description="Social platform for hashtag optimization")


class HashtagResearcher(BaseTool):
    name: str = "Hashtag Researcher"
    description: str = """Generates relevant B2B hashtag strategies for social media posts.
    Takes content topic and platform to recommend optimal hashtag combinations
    for reach and engagement.
    
    IMPORTANT - Input Format:
    - content_topic: STRING with subject (e.g., "Sales productivity and CRM adoption best practices - 
      change management, team buy-in, quick wins, measuring success...")
    - target_audience: STRING describing audience (e.g., "VPs and Directors of Sales at B2B companies 
      50-500 employees, managing 10-50 reps, challenged by forecast accuracy and team efficiency...")
    - platform: STRING specifying channel (e.g., "LinkedIn", "Twitter", "Instagram")
    
    DO NOT pass raw dict/JSON objects. Extract and format key information as readable text strings.
    
    Use this tool to:
    - Generate relevant hashtags
    - Mix high/medium/low competition tags
    - Optimize for discoverability
    - Build branded hashtag strategy
    
    Returns hashtag sets ready to use."""
    args_schema: Type[BaseModel] = HashtagInput
    
    def _run(self, content_topic: str, target_audience: str, platform: str) -> str:
        """Research and recommend hashtags."""
        
        hashtag_sets = self._generate_hashtag_sets()
        strategy = self._create_hashtag_strategy(platform)
        
        output = f"""## HASHTAG STRATEGY

**Platform:** {platform}
**Topic:** {content_topic}
**Audience:** {target_audience}

---

### Recommended Hashtag Sets

{chr(10).join(f'''#### Set {i+1}: {hs["name"]}

**Hashtags:**
{hs["tags"]}

**Mix:**
{hs["mix"]}

**Expected Reach:**
{hs["reach"]}

**Best For:**
{hs["use_case"]}

---
''' for i, hs in enumerate(hashtag_sets))}

### Platform-Specific Strategy

{strategy}

---

### Hashtag Best Practices

**Research:**
- Check hashtag before using (avoid irrelevant or controversial)
- Monitor competitor hashtag usage
- Track which hashtags drive best engagement
- Update strategy quarterly based on trends

**Usage:**
- Don't use same hashtags on every post
- Vary between broad and niche tags
- Include 1-2 branded hashtags consistently
- Place hashtags at end of post (cleaner)

**Testing:**
- A/B test different hashtag combinations
- Track reach and engagement by hashtag set
- Identify which tags attract quality followers
- Retire underperforming hashtags

**Monitoring:**
- Search your hashtags to see other content
- Engage with others using same hashtags
- Join hashtag conversations authentically
- Build relationships through hashtag discovery

These hashtag recommendations are optimized for B2B reach and engagement on {platform}."""
        
        return output
    
    def _generate_hashtag_sets(self) -> List[Dict[str, Any]]:
        """Generate hashtag set recommendations."""
        return [
            {
                'name': 'High Reach Mix',
                'tags': '#B2B #SaaS #Productivity #BusinessGrowth #SalesOps #TechStartup',
                'mix': '3 high-volume (500K+ posts), 2 medium (50K-500K), 1 niche (<50K)',
                'reach': 'High - More impressions, lower engagement rate',
                'use_case': 'Brand awareness posts, announcements, general content'
            },
            {
                'name': 'Targeted Engagement Mix',
                'tags': '#SalesAutomation #RevenueOperations #B2BSales #GTMStrategy #SalesLeaders',
                'mix': '1 high-volume, 3 medium, 2 niche',
                'reach': 'Medium - Better engagement rate, qualified audience',
                'use_case': 'Thought leadership, persona-specific content, educational posts'
            },
            {
                'name': 'Niche Authority Mix',
                'tags': '#SalesOperations #RevOps #QuoteToCash #DealDesk #SalesEfficiency',
                'mix': '1 medium, 5 niche',
                'reach': 'Lower - Highest engagement rate, very targeted',
                'use_case': 'Deep dives, technical content, expert insights'
            },
            {
                'name': 'Industry Events Mix',
                'tags': '#SaaStr #SalesEnablement #B2BMarketing #GrowthHacking #ScaleUp',
                'mix': '2 high-volume, 3 medium, 1 event-specific',
                'reach': 'High during event season, otherwise medium',
                'use_case': 'Conference season, industry events, thought leadership'
            },
            {
                'name': 'Problem-Solution Mix',
                'tags': '#ManualProcesses #DataEntry #Automation #DigitalTransformation #Efficiency',
                'mix': '3 problem hashtags, 3 solution hashtags',
                'reach': 'Medium - Attracts problem-aware audience',
                'use_case': 'Problem-solution posts, educational content, case studies'
            },
            {
                'name': 'Branded + Category Mix',
                'tags': '#YourBrand #YourBrandTips #SalesOps #RevOps #B2BSaaS #Productivity',
                'mix': '2 branded, 4 category/industry',
                'reach': 'Medium - Builds brand while reaching new audience',
                'use_case': 'All posts, consistent branding strategy'
            }
        ]
    
    def _create_hashtag_strategy(self, platform: str) -> str:
        """Create platform-specific hashtag strategy."""
        strategies = {
            'LinkedIn': """**LinkedIn Hashtag Strategy:**

**Optimal Count:** 3-5 hashtags
- More than 5 looks spammy
- Less than 3 limits discoverability
- Quality over quantity always

**Placement:** End of post or first comment
- First comment keeps main post cleaner
- End of post is easier, more common
- Test both to see what works

**Mix Formula:**
- 1 broad category hashtag (e.g., #B2B)
- 2 specific industry hashtags (e.g., #SalesOps, #RevOps)
- 1-2 niche/branded hashtags (e.g., #YourBrand)

**LinkedIn-Specific Tips:**
- Follow hashtags your audience uses
- Engage with content under those hashtags
- Use hashtags in articles too, not just posts
- Create brand hashtag and use consistently""",
            
            'Twitter': """**Twitter Hashtag Strategy:**

**Optimal Count:** 1-3 hashtags
- 1-2 is often ideal for Twitter
- More than 3 decreases engagement
- Use sparingly, strategically

**Placement:** Within the tweet naturally
- Integrate into sentence when possible
- Don't stack at end unless thread
- Make readable, not hashtag-heavy

**Mix Formula:**
- 1 trending/popular hashtag if relevant
- 1-2 specific topic hashtags
- Minimal branded hashtags

**Twitter-Specific Tips:**
- Check trending hashtags daily
- Join relevant trending conversations
- Use hashtags in threads sparingly
- Monitor hashtag to engage with users""",
            
            'Facebook': """**Facebook Hashtag Strategy:**

**Optimal Count:** 1-2 hashtags (minimal)
- Facebook hashtags less important
- Don't overuse or look spammy
- Focus on content quality instead

**Placement:** End of post
- Keep out of main narrative
- Less emphasis than other platforms
- Test with/without to see difference

**Mix Formula:**
- 1 broad category hashtag
- 1 specific topic if relevant
- Branded hashtag optional

**Facebook-Specific Tips:**
- Hashtags less effective than LinkedIn/Twitter
- Focus on engaging copy and visuals
- Use for consistency across platforms
- Groups > hashtags for reach on Facebook"""
        }
        
        return strategies.get(platform, strategies['LinkedIn'])


# =====================================================
# TOOL 4: Social Post Formatter
# =====================================================

class SocialPostFormatterInput(BaseModel):
    """Input schema for Social Post Formatter."""
    hook: str = Field(..., description="Opening hook from Hook Generator")
    story_angle: str = Field(..., description="Story angle from Story Angle Identifier")
    hashtags: str = Field(..., description="Hashtags from Hashtag Researcher")
    platform: str = Field(..., description="Target social platform")
    persona_name: str = Field(..., description="Target persona name")


class SocialPostFormatter(BaseTool):
    name: str = "Social Post Formatter"
    description: str = """Formats complete social media posts optimized for each platform.
    Assembles all components into ready-to-publish posts with proper formatting,
    length, and platform-specific optimizations.
    
    IMPORTANT - Input Format:
    - hook: STRING with opening line (e.g., "Your sales team hates your CRM. Here's why (and what 
      to do about it)...")
    - story_angle: STRING with narrative (e.g., "The 'reluctant champion' story - How one skeptical 
      sales manager became the biggest advocate after seeing 3-hour weekly time savings in first month. 
      Focus on transformation journey, initial resistance, aha moment, team impact...")
    - hashtags: STRING with tags (e.g., "#SalesProductivity #CRMAdoption #B2BSales #SalesLeadership 
      #RevenueOps #SalesEnablement")
    - platform: STRING specifying channel (e.g., "LinkedIn", "Twitter", "Facebook")
    - persona_name: STRING with identifier (e.g., "VP_Sales_Midmarket")
    
    DO NOT pass raw dict/JSON objects. Extract and format all content as readable text strings.
    
    Use this tool to:
    - Format complete posts
    - Optimize for platform
    - Add CTAs and links
    - Create post variations
    
    Returns 5-10 ready-to-publish social posts."""
    args_schema: Type[BaseModel] = SocialPostFormatterInput
    
    def _run(self, hook: str, story_angle: str, hashtags: str, platform: str, persona_name: str) -> str:
        """Format complete social media posts."""
        
        posts = self._generate_post_variations(platform)
        posting_guide = self._create_posting_guide(platform)
        
        output = f"""# SOCIAL MEDIA POSTS
## For {persona_name} on {platform}

---

## Ready-to-Publish Posts

{chr(10).join(f'''### Post {i+1}: {post["type"]}

**Optimal Post Time:** {post["timing"]}
**Expected Engagement:** {post["engagement"]}

**POST CONTENT:**

{post["content"]}

---

**VISUAL GUIDANCE:**
{post["visual"]}

**ENGAGEMENT PLAN:**
{post["engagement_plan"]}

**METRICS TO TRACK:**
{chr(10).join(f'- {metric}' for metric in post["metrics"])}

---
''' for i, post in enumerate(posts))}

## Platform-Specific Posting Guide

{posting_guide}

---

## Post Performance Optimization

**Before Posting:**
- [ ] Proofread for typos and clarity
- [ ] Verify all links work
- [ ] Check visual quality and size
- [ ] Schedule for optimal time
- [ ] Prepare first comment if needed

**After Posting (First Hour):**
- [ ] Respond to all comments quickly
- [ ] Like every comment
- [ ] Ask follow-up questions
- [ ] Share to relevant groups (if appropriate)
- [ ] Tag team members to boost engagement

**After Posting (First 24 Hours):**
- [ ] Continue engaging with comments
- [ ] Track metrics in spreadsheet
- [ ] Identify top performers
- [ ] Respond to DMs from post
- [ ] Document what worked/didn't work

**Continuous Optimization:**
- [ ] A/B test post times
- [ ] Try different hook styles
- [ ] Experiment with formats (text, carousel, video)
- [ ] Analyze which topics perform best
- [ ] Double down on what works

These posts are optimized for {platform} and ready to publish. Adapt based on your specific brand voice and what resonates with your audience."""
        
        return output
    
    def _generate_post_variations(self, platform: str) -> List[Dict[str, Any]]:
        """Generate ready-to-publish post variations."""
        
        # Platform-specific character limits and formats
        if platform == 'LinkedIn':
            return self._linkedin_posts()
        elif platform == 'Twitter':
            return self._twitter_posts()
        else:
            return self._linkedin_posts()  # Default to LinkedIn
    
    def _linkedin_posts(self) -> List[Dict[str, Any]]:
        """Generate LinkedIn-optimized posts."""
        return [
            {
                'type': 'Customer Success Story',
                'timing': 'Tuesday or Thursday, 8-10am',
                'engagement': 'High - Social proof performs well',
                'content': '''What if I told you that 40% of your team's time is completely wasted?

Not on things that matter. Just... wasted.

That was reality for TechCorp's sales team last year.

Sarah, their VP of Sales, told me:

"My team spent 15 hours per week on data entry. That's nearly half their time NOT selling."

The cost? $180,000 annually in wasted salary. Plus countless missed opportunities.

So we helped them automate it.

Here's what changed:

→ 15 hours/week saved per rep
→ 40% productivity increase
→ $245K in additional revenue (first quarter)
→ 4-month ROI

But the best part?

Sarah said: "My team actually enjoys their work now. They're selling, not entering data."

That's what happens when you eliminate work that shouldn't exist.

If your team is drowning in manual processes, let's talk.

---

💡 Want to see how we did it? Download the full case study: [LINK]

#SalesOps #B2BSales #Productivity #SalesLeaders #RevOps''',
                'visual': 'Professional image of happy sales team OR before/after metrics graphic',
                'engagement_plan': 'Ask in comments: "What manual process is eating your team\'s time?" Respond to every comment with genuine interest and follow-up questions.',
                'metrics': [
                    'Engagement rate (target: 3-5%)',
                    'Comments (target: 10-20)',
                    'Case study downloads',
                    'Demo requests from post'
                ]
            },
            {
                'type': 'Thought Leadership / Hot Take',
                'timing': 'Monday, 8-9am',
                'engagement': 'Very High - Controversy drives engagement',
                'content': '''Most "productivity tools" actually make teams less productive.

Here's why:

They add more steps, not fewer.
They require constant input, not automation.
They create visibility without action.

I've seen sales teams with 8+ tools that collectively:
→ Require 20+ hours/week to maintain
→ Create data silos
→ Still miss critical insights

The average B2B team uses 10+ SaaS tools.
But productivity has decreased 23% in the last 5 years.

Something's broken.

The solution isn't MORE tools.
It's eliminating work that shouldn't exist.

Ask yourself:

"Is this tool reducing work, or just reorganizing it?"

If your team is busier than ever but less productive, you're not alone.

And you don't need another tool.

You need to delete half of them.

---

What's your take? Too many tools or not enough?

#Productivity #B2B #SaaS #SalesOps #TechStack''',
                'visual': 'Graphic showing tool overload OR simple text-based image with key quote',
                'engagement_plan': 'This will generate debates. Engage with ALL comments, especially disagreements. Be respectful but hold your position. Ask counter-questions.',
                'metrics': [
                    'Comments (target: 30+)',
                    'Shares (target: 10+)',
                    'Engagement rate (target: 5-8%)',
                    'Debate quality (positive)'
                ]
            },
            {
                'type': 'Educational How-To',
                'timing': 'Thursday, 12-1pm',
                'engagement': 'High - Useful content gets saved',
                'content': '''How to eliminate 10 hours of manual work per week (in 30 minutes):

I've helped 500+ teams do this. Here's the framework:

Step 1: Track One Week
→ What tasks do you repeat daily/weekly?
→ Which ones frustrate you most?
→ List everything (even 5-min tasks add up)

Step 2: Calculate the Cost
→ Hours per week × hourly cost
→ Most teams waste $50K-$200K/year on manual work
→ This creates urgency for change

Step 3: Prioritize by Impact
→ High frequency + High frustration = Start here
→ Look for patterns (data entry, reporting, etc.)
→ Pick ONE to automate first

Step 4: Find the Right Solution
→ Don't buy more tools blindly
→ Look for automation-first solutions
→ Test with a pilot before full rollout

Step 5: Measure Everything
→ Time saved per person
→ Quality improvement
→ Team satisfaction
→ ROI

The average team eliminates 40% of manual work following this.

That's 15+ hours per person. Per week.

What could your team do with that time?

---

💾 Save this for your next planning meeting.

#Productivity #ProcessImprovement #SalesOps #B2BOperations #Efficiency''',
                'visual': '5-step infographic or carousel post walking through framework',
                'engagement_plan': 'Encourage saves and shares. Ask: "What manual process is your team most frustrated by?" Engage with every response.',
                'metrics': [
                    'Saves (target: 20+)',
                    'Shares (target: 15+)',
                    'Comments with specific pain points',
                    'Link clicks to guide/tool'
                ]
            },
            {
                'type': 'Behind the Scenes / Company',
                'timing': 'Friday, 2-3pm',
                'engagement': 'Medium - Builds connection',
                'content': '''Why we built this.

Three years ago, I was a sales ops manager at a fast-growing SaaS company.

My team was scaling fast. But I was drowning.

40 hours a week on:
→ Building reports no one read
→ Cleaning data that got dirty immediately
→ Answering "what's our pipeline?" 20x per day

I kept thinking: "There has to be a better way."

So I started building internal tools to automate my job.

My team went from 60-hour weeks to 40-hour weeks.
Our accuracy improved.
Our insights got faster.

Leadership noticed.

"Can you do this for other teams?"

That's when I realized:

Every sales ops person is building the same duct-tape solutions.

We're all solving the same problems independently.

That shouldn't be necessary.

So I left to build [Product].

Three years later:

→ 5,000+ companies using it
→ 200,000+ hours saved monthly
→ Thousands of ops people NOT drowning anymore

If you're in sales ops and feel like you're constantly underwater:

You're not alone.
It's not your fault.
And there's a better way.

That's why we built this.

---

P.S. If you're in sales ops, what's the most frustrating part of your role?

#SalesOps #Startup #FounderStory #B2BSaaS #ProductDevelopment''',
                'visual': 'Photo of founder or team, or journey timeline graphic',
                'engagement_plan': 'Very personal tone. Share in founder groups. Respond to every comment with empathy. This builds authentic connection.',
                'metrics': [
                    'Engagement rate (target: 4-6%)',
                    'Positive sentiment in comments',
                    'Profile visits',
                    'Follower growth'
                ]
            },
            {
                'type': 'Quick Tip / Snackable',
                'timing': 'Wednesday, 9-10am',
                'engagement': 'Medium-High - Quick value',
                'content': '''Your sales forecast is probably wrong.

Here's why:

You're using last month's data to predict next month.

But you're missing:
→ Deal velocity changes
→ Win rate trends
→ Pipeline quality shifts

Better approach:

Track these 3 metrics weekly:
1. Average deal age (is it increasing?)
2. Win rate by stage (where are deals dying?)
3. Pipeline coverage (3x minimum)

This takes 5 minutes.
But it makes your forecast 10x more accurate.

Your CFO will thank you.

---

What metrics do you track for forecasting?

#SalesOps #RevOps #SalesForecasting #B2BSales #DataDriven''',
                'visual': 'Simple graphic with 3 metrics OR text-only post works',
                'engagement_plan': 'Quick, actionable tip. Encourage responses with specific question. Engage with everyone who shares their approach.',
                'metrics': [
                    'Engagement rate (target: 3-5%)',
                    'Comments sharing methods',
                    'Saves',
                    'Shares to colleagues'
                ]
            }
        ]
    
    def _twitter_posts(self) -> List[Dict[str, Any]]:
        """Generate Twitter-optimized posts."""
        # Twitter has different constraints and formats
        return [
            {
                'type': 'Thread - Customer Story',
                'timing': 'Tuesday or Wednesday, 9-11am',
                'engagement': 'High - Threads perform well',
                'content': '''1/ What if I told you that 40% of your team's time is completely wasted?

Not on important work. Just wasted.

Here's how TechCorp's sales team fixed it 🧵

2/ Sarah, their VP of Sales, had a problem:

Her team spent 15 hrs/week on data entry
That's $180K/year in wasted salary
Plus countless missed deals

Something had to change.

3/ So we helped them automate it.

Results after 90 days:
→ 15 hrs/week saved per rep
→ 40% productivity increase
→ $245K additional revenue
→ 4-month ROI

4/ But the best part?

Sarah told me: "My team actually enjoys their work now."

That's what happens when you eliminate work that shouldn't exist.

5/ If your team is drowning in manual work, there's a better way.

Full case study: [LINK]

#SalesOps #B2BSales''',
                'visual': 'Thread with supporting images for key tweets (2, 3, 4)',
                'engagement_plan': 'Post thread, then engage with responses. Quote tweet your own thread with additional insights.',
                'metrics': [
                    'Thread engagement rate',
                    'Retweets (target: 10+)',
                    'Replies',
                    'Link clicks'
                ]
            },
            {
                'type': 'Hot Take - Single Tweet',
                'timing': 'Monday, 8-9am',
                'engagement': 'Very High - Controversial',
                'content': '''Most "productivity tools" make teams LESS productive.

They add steps instead of removing work.

The average B2B team uses 10+ tools.

Productivity has dropped 23% in 5 years.

You don't need another tool.

You need to delete half of them.

#Productivity #B2B''',
                'visual': 'Text-only works, or simple graphic with key stat',
                'engagement_plan': 'This will get responses/debates. Engage with everyone. Be prepared to back up claims with data.',
                'metrics': [
                    'Engagement rate (target: 5-8%)',
                    'Replies (quality over quantity)',
                    'Quote tweets',
                    'Profile visits'
                ]
            }
        ]
    
    def _create_posting_guide(self, platform: str) -> str:
        """Create platform-specific posting guide."""
        guides = {
            'LinkedIn': """**LinkedIn Posting Guide:**

**Optimal Post Times:**
- Tuesday-Thursday: 8-10am, 12-1pm (lunch), 5-6pm
- Monday: 8-9am (week kickoff)
- Friday: 2-4pm (casual, community content)
- Weekends: Test sparingly

**Post Length:**
- Sweet spot: 1,200-2,000 characters
- First 2-3 lines crucial (visible before "see more")
- Use line breaks generously for readability
- Longer = better for algorithm (if engaging)

**Engagement Strategy:**
- First hour is critical for algorithm
- Respond to every comment in first hour
- Like every comment
- Ask follow-up questions
- Tag colleagues to boost engagement
- Share to relevant groups (don't spam)

**Content Mix:**
- 40% Educational/how-to
- 30% Thought leadership/insights
- 20% Company/product (soft sell)
- 10% Personal/team stories

**Algorithm Tips:**
- Native content > external links (in post)
- Put links in first comment instead
- Videos perform better than images
- Carousels get high engagement
- Consistent posting > sporadic great posts""",
            
            'Twitter': """**Twitter Posting Guide:**

**Optimal Post Times:**
- Weekdays: 8-10am, 12-1pm, 5-6pm
- Wednesday and Friday peak days
- Weekends: Lower engagement but less competition

**Tweet Length:**
- Short and punchy (100-150 characters) OR
- Threads for complex topics (2,280 char limit)
- Use line breaks
- Don't use all 280 chars just because

**Engagement Strategy:**
- Respond to replies within minutes
- Quote tweet yourself with additions
- Use polls for engagement
- Join trending conversations (when relevant)
- Thread your best content for more reach

**Content Mix:**
- 50% Value/insights
- 30% Engagement/questions
- 15% Promotional (soft)
- 5% Personal

**Algorithm Tips:**
- Engagement within first 15 min crucial
- Threads perform well
- Video tweets get 10x more engagement
- Retweets with comments > straight RTs
- Consistency matters (daily posting)"""
        }
        
        return guides.get(platform, guides['LinkedIn'])


# Export all tools
__all__ = [
    'HookGenerator',
    'StoryAngleIdentifier',
    'HashtagResearcher',
    'SocialPostFormatter'
]
