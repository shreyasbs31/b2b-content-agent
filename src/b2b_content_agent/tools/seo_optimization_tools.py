"""SEO Optimization Tools for CREW 3

These tools help the SEO Optimizer agent improve content discoverability:
- Keyword optimization
- Metadata generation  
- CTA enhancement
- Format optimization
"""

from crewai.tools import BaseTool
from typing import Type, Dict, Any, List
from pydantic import BaseModel, Field
import random


# =====================================================
# TOOL 1: Keyword Optimizer
# =====================================================

class KeywordInput(BaseModel):
    """Input schema for Keyword Optimizer."""
    content: str = Field(..., description="Content to optimize for keywords")
    target_keywords: str = Field(..., description="Primary and secondary keywords to target")
    content_type: str = Field(..., description="Type of content")


class KeywordOptimizer(BaseTool):
    name: str = "Keyword Optimizer"
    description: str = """Analyzes keyword usage and suggests optimization improvements.
    Ensures natural keyword integration without stuffing.
    
    IMPORTANT - Input Format:
    - content: STRING with full text to analyze
    - target_keywords: STRING with keywords (e.g., "Primary: sales productivity software, CRM 
      automation. Secondary: sales team efficiency, automated data entry, pipeline management, 
      forecast accuracy tools, sales enablement platform")
    - content_type: STRING with type (e.g., "case_study", "white_paper")
    
    DO NOT pass raw dict/JSON objects. Format as comma-separated or descriptive text strings.
    
    Use this tool to:
    - Check keyword density
    - Identify keyword placement
    - Suggest natural variations
    - Flag keyword stuffing
    
    Returns keyword optimization report with recommendations."""
    args_schema: Type[BaseModel] = KeywordInput
    
    def _run(self, content: str, target_keywords: str, content_type: str) -> str:
        """Analyze and optimize keyword usage."""
        
        keywords = self._extract_keywords(target_keywords)
        keyword_analysis = self._analyze_keyword_usage(content, keywords)
        placement_analysis = self._analyze_keyword_placement(content, keywords)
        density_check = self._check_keyword_density(content, keywords)
        
        output = f"""## KEYWORD OPTIMIZATION REPORT

**Content Type:** {content_type}
**Target Keywords:** {len(keywords['primary'])} primary, {len(keywords['secondary'])} secondary
**Review Date:** 2025-11-03

---

### KEYWORD USAGE ANALYSIS

{self._format_keyword_usage(keyword_analysis)}

---

### PLACEMENT ANALYSIS

{self._format_placement_analysis(placement_analysis)}

---

### DENSITY CHECK

{self._format_density_check(density_check)}

---

### KEYWORD VARIATIONS SUGGESTED

{self._format_keyword_variations(keywords)}

---

### RECOMMENDATIONS

{chr(10).join(f'{i+1}. {rec}' for i, rec in enumerate(self._generate_keyword_recommendations(keyword_analysis, placement_analysis, density_check)))}

---

**Optimization Score:** {keyword_analysis['overall_score']}/100
**Status:** {keyword_analysis['status']}
"""
        return output
    
    def _extract_keywords(self, target_keywords: str) -> Dict[str, List[str]]:
        """Extract primary and secondary keywords."""
        
        primary = []
        secondary = []
        
        # Split by common separators
        parts = target_keywords.replace(',', '.').replace(';', '.').split('.')
        
        is_primary_section = False
        is_secondary_section = False
        
        for part in parts:
            part = part.strip().lower()
            
            if 'primary' in part:
                is_primary_section = True
                is_secondary_section = False
                # Extract keyword from same line
                keyword = part.split('primary')[-1].strip().strip(':').strip()
                if keyword and len(keyword) > 3:
                    primary.append(keyword)
            elif 'secondary' in part:
                is_secondary_section = True
                is_primary_section = False
                # Extract keyword from same line
                keyword = part.split('secondary')[-1].strip().strip(':').strip()
                if keyword and len(keyword) > 3:
                    secondary.append(keyword)
            elif is_primary_section and part and len(part) > 3:
                primary.append(part.strip())
            elif is_secondary_section and part and len(part) > 3:
                secondary.append(part.strip())
            elif not is_primary_section and not is_secondary_section and part and len(part) > 5:
                # Default to primary if no section specified
                primary.append(part.strip())
        
        # Ensure we have at least one primary keyword
        if not primary:
            primary = ['productivity', 'efficiency']
        
        return {
            'primary': primary[:3],  # Max 3 primary
            'secondary': secondary[:5]  # Max 5 secondary
        }
    
    def _analyze_keyword_usage(self, content: str, keywords: Dict[str, List[str]]) -> Dict[str, Any]:
        """Analyze how keywords are used in content."""
        
        content_lower = content.lower()
        
        primary_usage = {}
        for keyword in keywords['primary']:
            count = content_lower.count(keyword)
            primary_usage[keyword] = count
        
        secondary_usage = {}
        for keyword in keywords['secondary']:
            count = content_lower.count(keyword)
            secondary_usage[keyword] = count
        
        # Calculate overall score
        primary_score = sum(1 for count in primary_usage.values() if count >= 2) / max(len(keywords['primary']), 1) * 100
        secondary_score = sum(1 for count in secondary_usage.values() if count >= 1) / max(len(keywords['secondary']), 1) * 100
        
        overall_score = (primary_score * 0.7 + secondary_score * 0.3)
        
        if overall_score >= 75:
            status = "✅ WELL OPTIMIZED"
        elif overall_score >= 60:
            status = "✅ GOOD - MINOR IMPROVEMENTS"
        else:
            status = "⚠️ NEEDS OPTIMIZATION"
        
        return {
            'primary_usage': primary_usage,
            'secondary_usage': secondary_usage,
            'overall_score': round(overall_score, 1),
            'status': status
        }
    
    def _analyze_keyword_placement(self, content: str, keywords: Dict[str, List[str]]) -> Dict[str, Any]:
        """Analyze keyword placement in key positions."""
        
        content_lower = content.lower()
        
        # Check first 200 characters (intro)
        intro = content_lower[:200]
        intro_keywords = sum(1 for kw in keywords['primary'] if kw in intro)
        
        # Check headings (lines starting with # or all caps)
        lines = content.split('\n')
        heading_keywords = 0
        for line in lines:
            if line.strip().startswith('#') or (line.isupper() and len(line) > 5):
                heading_keywords += sum(1 for kw in keywords['primary'] if kw.lower() in line.lower())
        
        # Check conclusion (last 200 characters)
        conclusion = content_lower[-200:]
        conclusion_keywords = sum(1 for kw in keywords['primary'] if kw in conclusion)
        
        return {
            'in_intro': intro_keywords > 0,
            'in_headings': heading_keywords > 0,
            'in_conclusion': conclusion_keywords > 0,
            'intro_count': intro_keywords,
            'heading_count': heading_keywords,
            'conclusion_count': conclusion_keywords
        }
    
    def _check_keyword_density(self, content: str, keywords: Dict[str, List[str]]) -> Dict[str, Any]:
        """Check if keyword density is appropriate."""
        
        word_count = len(content.split())
        content_lower = content.lower()
        
        densities = {}
        issues = []
        
        for keyword in keywords['primary']:
            count = content_lower.count(keyword)
            density = (count / max(word_count, 1)) * 100
            densities[keyword] = {
                'count': count,
                'density': round(density, 2)
            }
            
            if density > 3:
                issues.append(f"'{keyword}' appears too frequently ({density:.1f}%) - may be keyword stuffing")
            elif density < 0.5 and count < 2:
                issues.append(f"'{keyword}' appears too rarely ({count} times) - increase usage")
        
        overall_health = "Good" if not issues else "Needs adjustment"
        
        return {
            'word_count': word_count,
            'densities': densities,
            'issues': issues,
            'health': overall_health
        }
    
    def _format_keyword_usage(self, analysis: Dict) -> str:
        """Format keyword usage results."""
        output = "**Primary Keywords:**\n"
        for keyword, count in analysis['primary_usage'].items():
            status = "✅" if count >= 2 else "⚠️"
            output += f"{status} '{keyword}': {count} occurrences\n"
        
        output += "\n**Secondary Keywords:**\n"
        for keyword, count in analysis['secondary_usage'].items():
            status = "✅" if count >= 1 else "⚠️"
            output += f"{status} '{keyword}': {count} occurrences\n"
        
        return output
    
    def _format_placement_analysis(self, placement: Dict) -> str:
        """Format placement analysis results."""
        output = "**Key Position Coverage:**\n"
        output += f"{'✅' if placement['in_intro'] else '❌'} Introduction: {placement['intro_count']} keywords\n"
        output += f"{'✅' if placement['in_headings'] else '❌'} Headings: {placement['heading_count']} keywords\n"
        output += f"{'✅' if placement['in_conclusion'] else '❌'} Conclusion: {placement['conclusion_count']} keywords\n"
        
        if placement['in_intro'] and placement['in_headings'] and placement['in_conclusion']:
            output += "\n✅ Excellent keyword distribution across all key positions"
        else:
            output += "\n⚠️ Improve keyword placement in missing key positions"
        
        return output
    
    def _format_density_check(self, density: Dict) -> str:
        """Format density check results."""
        output = f"**Total Word Count:** {density['word_count']} words\n\n"
        output += "**Keyword Density:**\n"
        
        for keyword, data in density['densities'].items():
            output += f"- '{keyword}': {data['count']} times ({data['density']}%)\n"
        
        if density['issues']:
            output += "\n**Issues:**\n"
            output += '\n'.join(f"⚠️ {issue}" for issue in density['issues'])
        else:
            output += "\n✅ Keyword density is within optimal range (0.5-3%)"
        
        return output
    
    def _format_keyword_variations(self, keywords: Dict) -> str:
        """Suggest keyword variations."""
        
        variations = []
        
        for keyword in keywords['primary'][:2]:  # First 2 primary keywords
            words = keyword.split()
            if len(words) >= 2:
                # Suggest word order variations
                variations.append(f"- Instead of '{keyword}': try '{words[-1]} {' '.join(words[:-1])}'")
                # Suggest synonym variations
                if 'software' in words:
                    variations.append(f"- Instead of '{keyword}': try '{keyword.replace('software', 'platform')}'")
                if 'productivity' in words:
                    variations.append(f"- Instead of '{keyword}': try '{keyword.replace('productivity', 'efficiency')}'")
        
        if not variations:
            variations = ["- Use natural language variations of primary keywords", "- Include related terms and synonyms"]
        
        return '\n'.join(variations[:4])
    
    def _generate_keyword_recommendations(self, usage: Dict, placement: Dict, density: Dict) -> List[str]:
        """Generate keyword optimization recommendations."""
        recommendations = []
        
        # Check primary keyword usage
        underused_primary = [kw for kw, count in usage['primary_usage'].items() if count < 2]
        if underused_primary:
            recommendations.append(f"Increase usage of primary keywords: {', '.join(underused_primary[:2])}")
        
        # Check placement
        if not placement['in_intro']:
            recommendations.append("Add primary keyword to the first paragraph for better SEO impact")
        if not placement['in_headings']:
            recommendations.append("Incorporate primary keywords into at least 2 section headings")
        if not placement['in_conclusion']:
            recommendations.append("Include primary keyword in the conclusion or final CTA")
        
        # Check density issues
        if density['issues']:
            recommendations.extend(density['issues'][:2])
        
        # General recommendations
        if not recommendations:
            recommendations.append("Keyword optimization is strong - maintain current usage patterns")
        
        return recommendations[:5]


# =====================================================
# TOOL 2: Metadata Generator
# =====================================================

class MetadataInput(BaseModel):
    """Input schema for Metadata Generator."""
    content: str = Field(..., description="Content to generate metadata for")
    target_keywords: str = Field(..., description="Keywords to incorporate in metadata")
    content_type: str = Field(..., description="Type of content")


class MetadataGenerator(BaseTool):
    name: str = "Metadata Generator"
    description: str = """Generates SEO-optimized metadata including titles, descriptions, and tags.
    Creates compelling meta content that improves click-through rates.
    
    IMPORTANT - Input Format:
    - content: STRING with full text or summary
    - target_keywords: STRING with keywords (e.g., "sales automation, CRM productivity, forecast 
      accuracy, pipeline management, sales enablement")
    - content_type: STRING with type (e.g., "case_study", "white_paper", "pitch_deck")
    
    DO NOT pass raw dict/JSON objects. Format as readable text strings.
    
    Use this tool to:
    - Generate meta titles (50-60 chars)
    - Create meta descriptions (150-160 chars)
    - Suggest relevant tags
    - Optimize for CTR
    
    Returns complete metadata package ready for publication."""
    args_schema: Type[BaseModel] = MetadataInput
    
    def _run(self, content: str, target_keywords: str, content_type: str) -> str:
        """Generate SEO metadata."""
        
        # Extract key information
        title_base = self._extract_title_base(content, content_type)
        primary_keyword = self._extract_primary_keyword(target_keywords)
        
        # Generate metadata
        meta_titles = self._generate_meta_titles(title_base, primary_keyword, content_type)
        meta_descriptions = self._generate_meta_descriptions(content, primary_keyword, content_type)
        tags = self._generate_tags(target_keywords, content_type)
        og_metadata = self._generate_og_metadata(meta_titles[0], meta_descriptions[0])
        
        output = f"""## SEO METADATA PACKAGE

**Content Type:** {content_type}
**Primary Keyword:** {primary_keyword}
**Generated:** 2025-11-03

---

### META TITLE OPTIONS

{chr(10).join(f'{i+1}. {title} ({len(title)} chars)' for i, title in enumerate(meta_titles))}

**Recommendation:** Option 1 - best balance of keyword placement and CTR appeal

---

### META DESCRIPTION OPTIONS

{chr(10).join(f'{i+1}. {desc} ({len(desc)} chars)' for i, desc in enumerate(meta_descriptions))}

**Recommendation:** Option 1 - includes primary keyword and compelling value prop

---

### RECOMMENDED TAGS

**Primary Tags:**
{chr(10).join(f'- {tag}' for tag in tags['primary'])}

**Secondary Tags:**
{chr(10).join(f'- {tag}' for tag in tags['secondary'])}

---

### OPEN GRAPH METADATA

```
og:title: {og_metadata['title']}
og:description: {og_metadata['description']}
og:type: article
og:image: [Add relevant case study/report image URL]
```

---

### TWITTER CARD METADATA

```
twitter:card: summary_large_image
twitter:title: {og_metadata['title']}
twitter:description: {og_metadata['description'][:200]}
twitter:image: [Add relevant image URL]
```

---

### RECOMMENDATIONS

1. Use Meta Title Option 1 for best SEO performance
2. Test Meta Description Option 2 if CTR is below 3%
3. Update tags quarterly based on search trends
4. Add schema markup for {content_type.replace('_', ' ')}
5. Monitor rankings for primary keyword: "{primary_keyword}"
"""
        return output
    
    def _extract_title_base(self, content: str, content_type: str) -> str:
        """Extract base for title from content."""
        
        # Try to find first heading
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('#'):
                title = line.strip().lstrip('#').strip()
                if len(title) > 10:
                    return title[:60]
        
        # Fallback to first sentence
        sentences = content.split('.')
        if sentences:
            return sentences[0][:60].strip()
        
        return f"B2B {content_type.replace('_', ' ').title()}"
    
    def _extract_primary_keyword(self, keywords: str) -> str:
        """Extract primary keyword."""
        
        # Look for "Primary:" designation
        if 'primary' in keywords.lower():
            parts = keywords.lower().split('primary')
            if len(parts) > 1:
                keyword_part = parts[1].split('.')[0].split(',')[0].strip().strip(':').strip()
                if keyword_part and len(keyword_part) > 3:
                    return keyword_part
        
        # Fallback to first keyword
        first_keyword = keywords.split('.')[0].split(',')[0].strip()
        return first_keyword if first_keyword else "productivity solution"
    
    def _generate_meta_titles(self, title_base: str, primary_keyword: str, content_type: str) -> List[str]:
        """Generate meta title options."""
        
        titles = []
        
        # Title 1: Keyword-first approach
        if content_type == 'case_study':
            titles.append(f"{primary_keyword.title()}: Customer Success Story")
        elif content_type == 'white_paper':
            titles.append(f"{primary_keyword.title()}: Complete Guide 2025")
        elif content_type == 'pitch_deck':
            titles.append(f"{primary_keyword.title()}: Product Overview")
        else:
            titles.append(f"{primary_keyword.title()}: {content_type.replace('_', ' ').title()}")
        
        # Title 2: Value-first approach  
        if content_type == 'case_study':
            titles.append(f"How TechCorp Achieved 40% Growth with {primary_keyword.title()}")
        elif content_type == 'white_paper':
            titles.append(f"The Ultimate {primary_keyword.title()} Strategy Guide")
        else:
            titles.append(f"Proven {primary_keyword.title()} Best Practices")
        
        # Title 3: Question approach
        titles.append(f"Need Better {primary_keyword.title()}? See How")
        
        # Ensure all titles are within 50-60 character range
        return [title[:60] for title in titles]
    
    def _generate_meta_descriptions(self, content: str, primary_keyword: str, content_type: str) -> List[str]:
        """Generate meta description options."""
        
        descriptions = []
        
        # Description 1: Results-focused
        if content_type == 'case_study':
            descriptions.append(
                f"Discover how leading companies use {primary_keyword} to drive measurable results. "
                f"Real metrics, proven strategies, and actionable insights. Download now."
            )
        elif content_type == 'white_paper':
            descriptions.append(
                f"Complete guide to {primary_keyword} for B2B teams. Best practices, frameworks, "
                f"and implementation strategies. Free download available."
            )
        else:
            descriptions.append(
                f"Learn how {primary_keyword} helps B2B teams improve efficiency and drive growth. "
                f"Practical insights and proven strategies included."
            )
        
        # Description 2: Problem-solution approach
        descriptions.append(
            f"Struggling with {primary_keyword}? This {content_type.replace('_', ' ')} shows "
            f"how top performers solve common challenges and achieve 40%+ improvements."
        )
        
        # Description 3: Benefit-focused
        descriptions.append(
            f"Unlock the full potential of {primary_keyword}. Expert insights, real examples, "
            f"and practical frameworks to accelerate your success."
        )
        
        # Ensure descriptions are 150-160 characters
        return [desc[:160] for desc in descriptions]
    
    def _generate_tags(self, keywords: str, content_type: str) -> Dict[str, List[str]]:
        """Generate relevant tags."""
        
        # Extract keywords into tags
        keyword_list = keywords.replace('.', ',').split(',')
        keyword_list = [k.strip().lower() for k in keyword_list if k.strip() and len(k.strip()) > 3]
        
        # Remove "primary:" and "secondary:" labels
        keyword_list = [k.replace('primary:', '').replace('secondary:', '').strip() for k in keyword_list]
        keyword_list = [k for k in keyword_list if k and len(k) > 3]
        
        primary_tags = keyword_list[:5]
        
        # Add content type tags
        secondary_tags = [
            content_type.replace('_', ' '),
            'b2b',
            'enterprise',
            'productivity'
        ]
        
        return {
            'primary': primary_tags if primary_tags else ['productivity', 'efficiency', 'b2b'],
            'secondary': secondary_tags
        }
    
    def _generate_og_metadata(self, title: str, description: str) -> Dict[str, str]:
        """Generate Open Graph metadata."""
        return {
            'title': title[:60],
            'description': description[:160]
        }


# =====================================================
# TOOL 3: CTA Enhancer
# =====================================================

class CTAEnhancementInput(BaseModel):
    """Input schema for CTA Enhancer."""
    content: str = Field(..., description="Content with existing CTAs")
    content_type: str = Field(..., description="Type of content")
    target_action: str = Field(..., description="Desired user action")


class CTAEnhancer(BaseTool):
    name: str = "CTA Enhancer"
    description: str = """Enhances calls-to-action for better conversion rates.
    Improves CTA placement, wording, and effectiveness.
    
    IMPORTANT - Input Format:
    - content: STRING with full text including current CTAs
    - content_type: STRING with type (e.g., "case_study", "white_paper")
    - target_action: STRING describing goal (e.g., "Schedule a demo with sales team, secondary: 
      download related white paper, tertiary: subscribe to newsletter for industry insights")
    
    DO NOT pass raw dict/JSON objects. Format as readable text strings.
    
    Use this tool to:
    - Analyze existing CTAs
    - Suggest improved wording
    - Optimize placement
    - Increase conversion potential
    
    Returns CTA enhancement report with specific recommendations."""
    args_schema: Type[BaseModel] = CTAEnhancementInput
    
    def _run(self, content: str, content_type: str, target_action: str) -> str:
        """Enhance CTAs for better conversion."""
        
        existing_ctas = self._identify_existing_ctas(content)
        cta_analysis = self._analyze_cta_effectiveness(existing_ctas, target_action)
        enhanced_ctas = self._generate_enhanced_ctas(target_action, content_type)
        placement_recommendations = self._recommend_cta_placement(content, content_type)
        
        output = f"""## CTA ENHANCEMENT REPORT

**Content Type:** {content_type}
**Target Action:** {target_action}
**Review Date:** 2025-11-03

---

### EXISTING CTA ANALYSIS

**CTAs Found:** {len(existing_ctas)}

{self._format_existing_ctas(existing_ctas, cta_analysis)}

---

### ENHANCED CTA OPTIONS

{self._format_enhanced_ctas(enhanced_ctas)}

---

### PLACEMENT RECOMMENDATIONS

{self._format_placement_recommendations(placement_recommendations)}

---

### OPTIMIZATION RECOMMENDATIONS

{chr(10).join(f'{i+1}. {rec}' for i, rec in enumerate(self._generate_cta_recommendations(cta_analysis, existing_ctas, content_type)))}

---

**Effectiveness Score:** {cta_analysis['overall_score']}/10
**Status:** {'✅ STRONG CTAs' if cta_analysis['overall_score'] >= 7 else '⚠️ NEEDS IMPROVEMENT'}
"""
        return output
    
    def _identify_existing_ctas(self, content: str) -> List[Dict[str, str]]:
        """Identify existing CTAs in content."""
        
        ctas = []
        
        # Common CTA patterns
        cta_verbs = ['schedule', 'contact', 'download', 'learn more', 'get started', 'request', 'book', 'try', 'see']
        
        sentences = content.split('.')
        for i, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()
            if any(verb in sentence_lower for verb in cta_verbs):
                ctas.append({
                    'text': sentence.strip(),
                    'position': 'early' if i < len(sentences) // 3 else 'middle' if i < 2 * len(sentences) // 3 else 'end',
                    'type': next((verb for verb in cta_verbs if verb in sentence_lower), 'other')
                })
        
        return ctas[:5]  # Max 5 CTAs
    
    def _analyze_cta_effectiveness(self, ctas: List[Dict], target_action: str) -> Dict[str, Any]:
        """Analyze effectiveness of existing CTAs."""
        
        if not ctas:
            return {
                'overall_score': 3,
                'has_primary_cta': False,
                'action_clarity': 'Weak',
                'alignment_with_goal': 'Poor'
            }
        
        # Check if primary action is present
        target_keywords = target_action.lower().split()
        has_primary = any(any(keyword in cta['text'].lower() for keyword in target_keywords[:3]) for cta in ctas)
        
        # Check action clarity
        action_verbs = sum(1 for cta in ctas if any(verb in cta['text'].lower() for verb in ['schedule', 'download', 'contact', 'request']))
        action_clarity = 'Strong' if action_verbs >= len(ctas) * 0.7 else 'Moderate' if action_verbs > 0 else 'Weak'
        
        # Calculate overall score
        score = 5  # Base score
        if has_primary:
            score += 2
        if action_clarity == 'Strong':
            score += 2
        elif action_clarity == 'Moderate':
            score += 1
        if len(ctas) >= 2:
            score += 1
        
        return {
            'overall_score': min(10, score),
            'has_primary_cta': has_primary,
            'action_clarity': action_clarity,
            'alignment_with_goal': 'Good' if has_primary else 'Needs improvement'
        }
    
    def _generate_enhanced_ctas(self, target_action: str, content_type: str) -> List[Dict[str, str]]:
        """Generate enhanced CTA options."""
        
        ctas = []
        
        # Primary CTA
        if 'demo' in target_action.lower():
            ctas.append({
                'priority': 'Primary',
                'text': "Schedule Your Personalized Demo",
                'supporting_text': "See how we can help your team achieve similar results in just 30 minutes.",
                'type': 'Button'
            })
            ctas.append({
                'priority': 'Primary Alternative',
                'text': "Book a Demo Today",
                'supporting_text': "Join 500+ companies already using our solution.",
                'type': 'Button'
            })
        elif 'download' in target_action.lower():
            ctas.append({
                'priority': 'Primary',
                'text': "Download the Complete Guide",
                'supporting_text': "Get instant access to all strategies and frameworks.",
                'type': 'Button'
            })
        else:
            ctas.append({
                'priority': 'Primary',
                'text': "Get Started Today",
                'supporting_text': "Experience the difference for yourself.",
                'type': 'Button'
            })
        
        # Secondary CTA
        if content_type == 'case_study':
            ctas.append({
                'priority': 'Secondary',
                'text': "Read More Success Stories",
                'supporting_text': "Discover how other companies are achieving results.",
                'type': 'Text Link'
            })
        else:
            ctas.append({
                'priority': 'Secondary',
                'text': "Subscribe for More Insights",
                'supporting_text': "Get monthly tips and best practices delivered to your inbox.",
                'type': 'Text Link'
            })
        
        return ctas
    
    def _recommend_cta_placement(self, content: str, content_type: str) -> List[Dict[str, str]]:
        """Recommend CTA placement."""
        
        recommendations = []
        
        if content_type == 'case_study':
            recommendations.append({
                'location': 'After Results Section',
                'rationale': 'Reader has just seen proof of value - high conversion intent',
                'cta_type': 'Primary action (Schedule Demo)'
            })
            recommendations.append({
                'location': 'End of Document',
                'rationale': 'Final opportunity for engaged readers',
                'cta_type': 'Primary action repeated'
            })
        elif content_type == 'white_paper':
            recommendations.append({
                'location': 'After Executive Summary',
                'rationale': 'Early CTA for time-constrained executives',
                'cta_type': 'Secondary action (Download full PDF)'
            })
            recommendations.append({
                'location': 'After Key Framework Section',
                'rationale': 'Reader sees value, wants to implement',
                'cta_type': 'Primary action (Schedule consultation)'
            })
            recommendations.append({
                'location': 'Conclusion',
                'rationale': 'Final conversion opportunity',
                'cta_type': 'Primary action'
            })
        else:
            recommendations.append({
                'location': 'Introduction',
                'rationale': 'Early engagement opportunity',
                'cta_type': 'Soft CTA (Learn more)'
            })
            recommendations.append({
                'location': 'Conclusion',
                'rationale': 'Final conversion point',
                'cta_type': 'Primary action'
            })
        
        return recommendations
    
    def _format_existing_ctas(self, ctas: List[Dict], analysis: Dict) -> str:
        """Format existing CTA analysis."""
        
        if not ctas:
            return "❌ No clear CTAs found in content\n\n**Impact:** Missing conversion opportunities"
        
        output = ""
        for i, cta in enumerate(ctas, 1):
            output += f"\n**CTA #{i}:**\n"
            output += f"- Text: \"{cta['text']}\"\n"
            output += f"- Position: {cta['position'].title()}\n"
            output += f"- Type: {cta['type'].title()}\n"
        
        output += f"\n**Analysis:**\n"
        output += f"- Primary Action Present: {'✅ Yes' if analysis['has_primary_cta'] else '❌ No'}\n"
        output += f"- Action Clarity: {analysis['action_clarity']}\n"
        output += f"- Goal Alignment: {analysis['alignment_with_goal']}\n"
        
        return output
    
    def _format_enhanced_ctas(self, ctas: List[Dict]) -> str:
        """Format enhanced CTA options."""
        
        output = ""
        for cta in ctas:
            output += f"\n**{cta['priority']} CTA:**\n"
            output += f"```\n{cta['text']}\n```\n"
            output += f"*{cta['supporting_text']}*\n"
            output += f"**Format:** {cta['type']}\n"
        
        return output
    
    def _format_placement_recommendations(self, recommendations: List[Dict]) -> str:
        """Format placement recommendations."""
        
        output = ""
        for i, rec in enumerate(recommendations, 1):
            output += f"\n**Position #{i}: {rec['location']}**\n"
            output += f"- Rationale: {rec['rationale']}\n"
            output += f"- Recommended CTA: {rec['cta_type']}\n"
        
        return output
    
    def _generate_cta_recommendations(self, analysis: Dict, existing_ctas: List[Dict], content_type: str) -> List[str]:
        """Generate CTA improvement recommendations."""
        
        recommendations = []
        
        if not existing_ctas:
            recommendations.append("Add at least 2 CTAs - one after key results, one at conclusion")
            recommendations.append("Use action-oriented button text (e.g., 'Schedule Demo' not 'Click Here')")
        
        if not analysis['has_primary_cta']:
            recommendations.append("Include clear CTA for primary conversion goal in prominent position")
        
        if analysis['action_clarity'] != 'Strong':
            recommendations.append("Replace vague CTAs ('Learn More') with specific actions ('Schedule Your Demo')")
        
        if len(existing_ctas) < 2:
            recommendations.append("Add secondary CTA for lower-intent visitors (e.g., 'Download Guide')")
        
        # Content type specific
        if content_type == 'case_study':
            recommendations.append("Place primary CTA immediately after results/metrics section")
        elif content_type == 'white_paper':
            recommendations.append("Add early CTA after executive summary for time-constrained readers")
        
        if not recommendations:
            recommendations.append("CTAs are well-optimized - test A/B variations to improve conversion")
        
        return recommendations[:5]


# =====================================================
# TOOL 4: Format Optimizer
# =====================================================

class FormatInput(BaseModel):
    """Input schema for Format Optimizer."""
    content: str = Field(..., description="Content to optimize formatting")
    content_type: str = Field(..., description="Type of content")


class FormatOptimizer(BaseTool):
    name: str = "Format Optimizer"
    description: str = """Optimizes content structure and formatting for readability and engagement.
    Suggests visual improvements, heading structure, and content flow.
    
    IMPORTANT - Input Format:
    - content: STRING with full text to analyze
    - content_type: STRING with type (e.g., "case_study", "white_paper", "social_post")
    
    DO NOT pass raw dict/JSON objects. Format as readable text strings.
    
    Use this tool to:
    - Analyze heading structure
    - Check paragraph length
    - Suggest visual elements
    - Improve scanability
    
    Returns format optimization report with specific suggestions."""
    args_schema: Type[BaseModel] = FormatInput
    
    def _run(self, content: str, content_type: str) -> str:
        """Optimize content formatting."""
        
        structure_analysis = self._analyze_structure(content)
        readability_analysis = self._analyze_readability(content)
        visual_suggestions = self._suggest_visual_elements(content, content_type)
        
        output = f"""## FORMAT OPTIMIZATION REPORT

**Content Type:** {content_type}
**Review Date:** 2025-11-03
**Format Score:** {structure_analysis['score']}/100

---

### STRUCTURE ANALYSIS

{self._format_structure_analysis(structure_analysis)}

---

### READABILITY ANALYSIS

{self._format_readability_analysis(readability_analysis)}

---

### VISUAL ELEMENT SUGGESTIONS

{self._format_visual_suggestions(visual_suggestions)}

---

### OPTIMIZATION RECOMMENDATIONS

{chr(10).join(f'{i+1}. {rec}' for i, rec in enumerate(self._generate_format_recommendations(structure_analysis, readability_analysis, content_type)))}

---

**Optimization Status:** {'✅ WELL FORMATTED' if structure_analysis['score'] >= 75 else '⚠️ NEEDS IMPROVEMENT'}
"""
        return output
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure."""
        
        lines = content.split('\n')
        
        # Count headings
        h1_count = sum(1 for line in lines if line.strip().startswith('# ') and not line.startswith('##'))
        h2_count = sum(1 for line in lines if line.strip().startswith('## '))
        h3_count = sum(1 for line in lines if line.strip().startswith('### '))
        
        total_headings = h1_count + h2_count + h3_count
        
        # Check heading hierarchy
        proper_hierarchy = h1_count <= 1 and h2_count >= 2
        
        # Count sections (content between headings)
        section_count = h2_count + h3_count
        
        # Score
        score = 50  # Base
        if proper_hierarchy:
            score += 20
        if total_headings >= 4:
            score += 15
        if section_count >= 3:
            score += 15
        
        return {
            'h1_count': h1_count,
            'h2_count': h2_count,
            'h3_count': h3_count,
            'total_headings': total_headings,
            'proper_hierarchy': proper_hierarchy,
            'section_count': section_count,
            'score': min(100, score)
        }
    
    def _analyze_readability(self, content: str) -> Dict[str, Any]:
        """Analyze readability factors."""
        
        # Remove headings for paragraph analysis
        content_no_headings = '\n'.join(line for line in content.split('\n') if not line.strip().startswith('#'))
        
        paragraphs = [p.strip() for p in content_no_headings.split('\n\n') if p.strip()]
        
        # Analyze paragraph length
        paragraph_lengths = [len(p.split()) for p in paragraphs]
        avg_paragraph_length = sum(paragraph_lengths) / max(len(paragraphs), 1)
        
        long_paragraphs = sum(1 for length in paragraph_lengths if length > 100)
        
        # Check for bullet points
        has_bullets = '-' in content or '*' in content or any(line.strip().startswith(('- ', '* ', '1.', '2.')) for line in content.split('\n'))
        
        # Check for white space
        blank_lines = content.count('\n\n')
        adequate_whitespace = blank_lines >= len(paragraphs) * 0.5
        
        return {
            'paragraph_count': len(paragraphs),
            'avg_paragraph_length': round(avg_paragraph_length, 1),
            'long_paragraphs': long_paragraphs,
            'has_bullets': has_bullets,
            'adequate_whitespace': adequate_whitespace
        }
    
    def _suggest_visual_elements(self, content: str, content_type: str) -> List[Dict[str, str]]:
        """Suggest visual elements to add."""
        
        suggestions = []
        
        # Check if numbers/metrics are present - suggest data visualization
        if any(char.isdigit() for char in content) and '%' in content:
            suggestions.append({
                'type': 'Data Visualization',
                'element': 'Chart or infographic',
                'placement': 'After metrics section',
                'rationale': 'Quantitative results are more impactful when visualized'
            })
        
        # Suggest hero image
        if content_type in ['case_study', 'white_paper']:
            suggestions.append({
                'type': 'Hero Image',
                'element': 'Branded header image',
                'placement': 'Top of document',
                'rationale': 'Creates professional first impression and brand recognition'
            })
        
        # Suggest call-out boxes
        if 'key' in content.lower() or 'important' in content.lower():
            suggestions.append({
                'type': 'Call-out Box',
                'element': 'Highlighted key takeaway',
                'placement': 'After main findings section',
                'rationale': 'Emphasizes critical points for scanners'
            })
        
        # Suggest screenshot/diagram
        if content_type == 'case_study':
            suggestions.append({
                'type': 'Product Screenshot',
                'element': 'Interface or dashboard view',
                'placement': 'Solution description section',
                'rationale': 'Helps readers visualize the solution'
            })
        
        return suggestions[:4]
    
    def _format_structure_analysis(self, analysis: Dict) -> str:
        """Format structure analysis results."""
        
        output = "**Heading Structure:**\n"
        output += f"- H1 headings: {analysis['h1_count']}\n"
        output += f"- H2 headings: {analysis['h2_count']}\n"
        output += f"- H3 headings: {analysis['h3_count']}\n"
        output += f"- Total headings: {analysis['total_headings']}\n\n"
        
        if analysis['proper_hierarchy']:
            output += "✅ Proper heading hierarchy maintained\n"
        else:
            output += "⚠️ Heading hierarchy needs improvement\n"
        
        output += f"\n**Sections:** {analysis['section_count']} content sections identified\n"
        
        return output
    
    def _format_readability_analysis(self, analysis: Dict) -> str:
        """Format readability analysis results."""
        
        output = f"**Paragraph Statistics:**\n"
        output += f"- Total paragraphs: {analysis['paragraph_count']}\n"
        output += f"- Average length: {analysis['avg_paragraph_length']} words\n"
        output += f"- Long paragraphs (>100 words): {analysis['long_paragraphs']}\n\n"
        
        if analysis['avg_paragraph_length'] > 75:
            output += "⚠️ Paragraphs are too long - break into shorter chunks\n"
        else:
            output += "✅ Paragraph length is good for readability\n"
        
        output += f"\n{'✅' if analysis['has_bullets'] else '❌'} Bullet points: {'Present' if analysis['has_bullets'] else 'Missing'}\n"
        output += f"{'✅' if analysis['adequate_whitespace'] else '⚠️'} White space: {'Adequate' if analysis['adequate_whitespace'] else 'Needs more'}\n"
        
        return output
    
    def _format_visual_suggestions(self, suggestions: List[Dict]) -> str:
        """Format visual element suggestions."""
        
        if not suggestions:
            return "No specific visual elements needed - content is primarily text-based"
        
        output = ""
        for i, suggestion in enumerate(suggestions, 1):
            output += f"\n**Suggestion #{i}: {suggestion['type']}**\n"
            output += f"- Element: {suggestion['element']}\n"
            output += f"- Placement: {suggestion['placement']}\n"
            output += f"- Rationale: {suggestion['rationale']}\n"
        
        return output
    
    def _generate_format_recommendations(self, structure: Dict, readability: Dict, content_type: str) -> List[str]:
        """Generate format optimization recommendations."""
        
        recommendations = []
        
        # Structure recommendations
        if structure['h2_count'] < 3:
            recommendations.append("Add more H2 section headings (target: 4-6) to improve scanability")
        
        if not structure['proper_hierarchy']:
            recommendations.append("Maintain proper heading hierarchy: one H1, multiple H2s, H3s under H2s")
        
        # Readability recommendations
        if readability['long_paragraphs'] > 2:
            recommendations.append(f"Break down {readability['long_paragraphs']} long paragraphs into shorter 3-4 sentence chunks")
        
        if not readability['has_bullets']:
            recommendations.append("Add bullet points to list out key features, benefits, or steps")
        
        if not readability['adequate_whitespace']:
            recommendations.append("Add more white space between sections for better visual separation")
        
        # Content-type specific
        if content_type == 'case_study':
            recommendations.append("Add pull quote or customer testimonial in highlighted box")
        elif content_type == 'white_paper':
            recommendations.append("Include table of contents for documents over 2000 words")
        
        if not recommendations:
            recommendations.append("Format is well-optimized - focus on content quality")
        
        return recommendations[:5]
