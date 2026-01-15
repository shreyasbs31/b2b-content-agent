"""Brand Voice & Messaging Tools for CREW 3

These tools help the Brand Voice Guardian agent ensure:
- Consistent tone and brand voice
- Messaging alignment with strategy
- Persona-specific relevance
- Compliance with guidelines
"""

from crewai.tools import BaseTool
from typing import Type, Dict, Any, List
from pydantic import BaseModel, Field
import random


# =====================================================
# TOOL 1: Tone Analyzer
# =====================================================

class ToneInput(BaseModel):
    """Input schema for Tone Analyzer."""
    content: str = Field(..., description="The content to analyze for tone")
    target_tone: str = Field(..., description="Expected tone (professional, casual, authoritative, etc.)")
    content_type: str = Field(..., description="Type of content")


class ToneAnalyzer(BaseTool):
    name: str = "Tone Analyzer"
    description: str = """Analyzes tone and voice consistency in content.
    Ensures content matches target tone and maintains consistent voice.
    
    IMPORTANT - Input Format:
    - content: STRING with full text (e.g., "Hey there! We're super excited to share this amazing 
      case study about how TechCorp crushed their goals. It's totally game-changing and you'll love it!")
    - target_tone: STRING describing desired tone (e.g., "Professional but approachable, confident 
      without being salesy, consultative voice, avoid casual slang or overly enthusiastic language")
    - content_type: STRING with type (e.g., "case_study", "white_paper")
    
    DO NOT pass raw dict/JSON objects. Format as readable text strings.
    
    Use this tool to:
    - Detect tone inconsistencies
    - Flag inappropriate language
    - Assess formality level
    - Check emotional balance
    
    Returns tone analysis report with recommendations."""
    args_schema: Type[BaseModel] = ToneInput
    
    def _run(self, content: str, target_tone: str, content_type: str) -> str:
        """Analyze tone and voice in content."""
        
        detected_tone = self._detect_tone(content)
        tone_match = self._compare_to_target(detected_tone, target_tone)
        issues = self._identify_tone_issues(content, target_tone)
        recommendations = self._generate_tone_recommendations(issues, detected_tone, target_tone)
        
        output = f"""## TONE & VOICE ANALYSIS REPORT

**Content Type:** {content_type}
**Target Tone:** {target_tone}
**Review Date:** 2025-11-03

---

### DETECTED TONE CHARACTERISTICS

**Primary Tone:** {detected_tone['primary']}
**Formality Level:** {detected_tone['formality']}
**Emotional Intensity:** {detected_tone['emotion']}
**Confidence Level:** {detected_tone['confidence']}

---

### TONE ALIGNMENT

**Match with Target:** {tone_match['score']}/100
**Assessment:** {tone_match['assessment']}

**Strengths:**
{chr(10).join(f'- {s}' for s in tone_match['strengths'])}

**Areas for Improvement:**
{chr(10).join(f'- {a}' for a in tone_match['areas_to_improve'])}

---

### IDENTIFIED ISSUES

{self._format_tone_issues(issues)}

---

### RECOMMENDATIONS

{chr(10).join(f'{i+1}. {rec}' for i, rec in enumerate(recommendations))}

---

### TONE EXAMPLES

**Current style example:**
"{self._extract_example(content, 'current')}"

**Recommended style:**
"{self._extract_example(content, 'recommended')}"

**Review Status:** {tone_match['status']}
"""
        return output
    
    def _detect_tone(self, content: str) -> Dict[str, str]:
        """Detect tone characteristics in content."""
        
        content_lower = content.lower()
        
        # Detect formality
        casual_indicators = ['hey', 'super', 'awesome', 'totally', 'crush', 'nail', 'gonna']
        formal_indicators = ['furthermore', 'consequently', 'nevertheless', 'therefore', 'accordingly']
        
        casual_count = sum(content_lower.count(word) for word in casual_indicators)
        formal_count = sum(content_lower.count(word) for word in formal_indicators)
        
        if casual_count > formal_count:
            formality = "Casual"
        elif formal_count > casual_count:
            formality = "Formal"
        else:
            formality = "Professional"
        
        # Detect emotional intensity
        intense_words = ['amazing', 'incredible', 'revolutionary', 'game-changing', 'awesome']
        intense_count = sum(content_lower.count(word) for word in intense_words)
        
        if intense_count > 5:
            emotion = "High (overly enthusiastic)"
        elif intense_count > 2:
            emotion = "Medium (balanced)"
        else:
            emotion = "Low (understated)"
        
        # Detect confidence
        confident_words = ['proven', 'guaranteed', 'ensures', 'delivers', 'achieves']
        hesitant_words = ['might', 'maybe', 'perhaps', 'possibly', 'could potentially']
        
        confident_count = sum(content_lower.count(word) for word in confident_words)
        hesitant_count = sum(content_lower.count(word) for word in hesitant_words)
        
        if confident_count > hesitant_count * 2:
            confidence = "High (assertive)"
        elif hesitant_count > confident_count:
            confidence = "Low (hesitant)"
        else:
            confidence = "Balanced (consultative)"
        
        # Determine primary tone
        if formality == "Casual" and emotion == "High (overly enthusiastic)":
            primary = "Overly casual and enthusiastic"
        elif formality == "Formal" and confidence == "High (assertive)":
            primary = "Authoritative and professional"
        elif formality == "Professional" and confidence == "Balanced (consultative)":
            primary = "Professional and consultative"
        else:
            primary = "Mixed (inconsistent)"
        
        return {
            'primary': primary,
            'formality': formality,
            'emotion': emotion,
            'confidence': confidence
        }
    
    def _compare_to_target(self, detected: Dict, target: str) -> Dict[str, Any]:
        """Compare detected tone to target."""
        
        strengths = []
        areas_to_improve = []
        
        # Check if detected tone matches target expectations
        if 'professional' in target.lower():
            if detected['formality'] == 'Professional':
                strengths.append("Maintains professional tone throughout")
                score = 85
            elif detected['formality'] == 'Casual':
                areas_to_improve.append("Too casual for professional content")
                score = 60
            else:
                strengths.append("Appropriately formal")
                score = 75
        else:
            score = 70
        
        if 'approachable' in target.lower() or 'friendly' in target.lower():
            if detected['formality'] != 'Formal':
                strengths.append("Achieves approachable tone")
            else:
                areas_to_improve.append("May be too formal - add warmth")
        
        if 'confident' in target.lower():
            if 'High' in detected['confidence'] or 'Balanced' in detected['confidence']:
                strengths.append("Projects appropriate confidence")
            else:
                areas_to_improve.append("Lacks confidence - strengthen assertions")
        
        if 'avoid' in target.lower() and 'enthusiastic' in target.lower():
            if 'High' in detected['emotion']:
                areas_to_improve.append("Too enthusiastic - tone down superlatives")
                score -= 15
            else:
                strengths.append("Maintains appropriate emotional balance")
        
        if score >= 80:
            assessment = "Excellent match with target tone"
            status = "✅ APPROVED"
        elif score >= 70:
            assessment = "Good match with minor adjustments needed"
            status = "✅ APPROVED WITH NOTES"
        else:
            assessment = "Significant tone mismatch - revision recommended"
            status = "⚠️ NEEDS REVISION"
        
        if not strengths:
            strengths = ["Some positive tone elements present"]
        if not areas_to_improve:
            areas_to_improve = ["No significant issues identified"]
        
        return {
            'score': score,
            'assessment': assessment,
            'strengths': strengths,
            'areas_to_improve': areas_to_improve,
            'status': status
        }
    
    def _identify_tone_issues(self, content: str, target_tone: str) -> List[Dict[str, str]]:
        """Identify specific tone issues."""
        issues = []
        
        content_lower = content.lower()
        
        # Check for overly casual language
        casual_phrases = ['hey there', 'super excited', 'totally', 'awesome', 'crush it']
        found_casual = [p for p in casual_phrases if p in content_lower]
        if found_casual and 'professional' in target_tone.lower():
            issues.append({
                'type': 'Overly casual language',
                'severity': 'Moderate',
                'examples': ', '.join(found_casual[:3]),
                'recommendation': 'Replace casual phrases with professional alternatives'
            })
        
        # Check for excessive enthusiasm
        enthusiasm_markers = ['!', '!!', '!!!']
        exclamation_count = sum(content.count(marker) for marker in enthusiasm_markers)
        if exclamation_count > 5:
            issues.append({
                'type': 'Excessive enthusiasm',
                'severity': 'Moderate',
                'examples': f'{exclamation_count} exclamation marks found',
                'recommendation': 'Reduce exclamation marks to 2-3 maximum for emphasis only'
            })
        
        # Check for weak/hedging language
        hedging_words = ['might', 'maybe', 'perhaps', 'possibly', 'could potentially', 'somewhat']
        found_hedging = [w for w in hedging_words if w in content_lower]
        if len(found_hedging) > 5:
            issues.append({
                'type': 'Excessive hedging',
                'severity': 'Minor',
                'examples': ', '.join(found_hedging[:3]),
                'recommendation': 'Strengthen language with confident assertions'
            })
        
        return issues
    
    def _format_tone_issues(self, issues: List[Dict]) -> str:
        """Format tone issues for output."""
        if not issues:
            return "✅ No tone issues identified - voice is consistent and appropriate."
        
        formatted = []
        for i, issue in enumerate(issues, 1):
            formatted.append(f"""
**Issue #{i}: {issue['type']}**
- Severity: {issue['severity']}
- Examples: {issue['examples']}
- Recommendation: {issue['recommendation']}
""")
        return '\n'.join(formatted)
    
    def _generate_tone_recommendations(self, issues: List[Dict], detected: Dict, target: str) -> List[str]:
        """Generate tone improvement recommendations."""
        recommendations = []
        
        for issue in issues:
            recommendations.append(issue['recommendation'])
        
        # Add general recommendations based on detected vs target
        if detected['formality'] == 'Casual' and 'professional' in target.lower():
            recommendations.append("Replace casual phrases with professional equivalents (e.g., 'Hello' instead of 'Hey')")
        
        if 'High' in detected['emotion']:
            recommendations.append("Reduce superlatives and enthusiastic language - use specific metrics instead")
        
        if 'Low' in detected['confidence']:
            recommendations.append("Use stronger, more confident language (e.g., 'enables' instead of 'might help')")
        
        if not recommendations:
            recommendations.append("Tone is well-aligned with target - no significant changes needed")
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _extract_example(self, content: str, example_type: str) -> str:
        """Extract example sentences."""
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        
        if example_type == 'current' and sentences:
            return sentences[0] + '.'
        elif example_type == 'recommended':
            # Provide improved version
            return "TechCorp achieved a 40% improvement in operational efficiency within three months of implementation."
        
        return "No example available"


# =====================================================
# TOOL 2: Messaging Aligner
# =====================================================

class MessagingInput(BaseModel):
    """Input schema for Messaging Aligner."""
    content: str = Field(..., description="Content to check for messaging alignment")
    content_strategy: str = Field(..., description="Key messages and value propositions from strategy")
    persona_profile: str = Field(..., description="Target persona details")


class MessagingAligner(BaseTool):
    name: str = "Messaging Aligner"
    description: str = """Validates messaging alignment with content strategy and value propositions.
    Ensures content reflects key messages and resonates with target persona.
    
    IMPORTANT - Input Format:
    - content: STRING with full content to review
    - content_strategy: STRING with key messages (e.g., "Primary message: Increase productivity 
      40% in 90 days. Secondary messages: Reduce manual work, improve forecast accuracy, seamless 
      CRM integration. Value props: Time savings, data quality, ease of use")
    - persona_profile: STRING with persona details (e.g., "VP of Sales at mid-market B2B companies, 
      primary concerns: team productivity, forecast accuracy, CRM adoption. Pain points: manual data 
      entry, lost context, reporting burden")
    
    DO NOT pass raw dict/JSON objects. Extract and format as readable text strings.
    
    Use this tool to:
    - Check message presence and emphasis
    - Validate value prop coverage
    - Assess persona relevance
    - Identify messaging gaps
    
    Returns messaging alignment report with recommendations."""
    args_schema: Type[BaseModel] = MessagingInput
    
    def _run(self, content: str, content_strategy: str, persona_profile: str) -> str:
        """Check messaging alignment."""
        
        key_messages = self._extract_key_messages(content_strategy)
        message_coverage = self._check_message_coverage(content, key_messages)
        persona_alignment = self._assess_persona_alignment(content, persona_profile)
        gaps = self._identify_messaging_gaps(message_coverage, persona_alignment)
        
        output = f"""## MESSAGING ALIGNMENT REPORT

**Review Date:** 2025-11-03
**Target Persona:** {persona_profile[:100]}...
**Alignment Score:** {message_coverage['overall_score']}/100

---

### KEY MESSAGE COVERAGE

{self._format_message_coverage(message_coverage)}

---

### PERSONA ALIGNMENT

**Relevance Score:** {persona_alignment['relevance_score']}/10
**Pain Point Addressed:** {persona_alignment['pain_points_covered']}/{persona_alignment['total_pain_points']}

{self._format_persona_alignment(persona_alignment)}

---

### IDENTIFIED GAPS

{self._format_gaps(gaps)}

---

### RECOMMENDATIONS

{chr(10).join(f'{i+1}. {rec}' for i, rec in enumerate(self._generate_messaging_recommendations(gaps, message_coverage)))}

---

**Review Status:** {message_coverage['status']}
"""
        return output
    
    def _extract_key_messages(self, strategy: str) -> List[str]:
        """Extract key messages from strategy."""
        # Simple extraction - in production would use more sophisticated parsing
        messages = []
        
        if 'productivity' in strategy.lower():
            messages.append('productivity improvement')
        if 'time' in strategy.lower() or 'save' in strategy.lower():
            messages.append('time savings')
        if 'accuracy' in strategy.lower() or 'quality' in strategy.lower():
            messages.append('data accuracy')
        if 'integration' in strategy.lower():
            messages.append('integration capabilities')
        if 'easy' in strategy.lower() or 'simple' in strategy.lower():
            messages.append('ease of use')
        
        return messages if messages else ['value delivery', 'problem solving']
    
    def _check_message_coverage(self, content: str, messages: List[str]) -> Dict[str, Any]:
        """Check how well key messages are covered."""
        
        content_lower = content.lower()
        covered_messages = []
        missing_messages = []
        
        for message in messages:
            if message in content_lower or any(word in content_lower for word in message.split()):
                covered_messages.append(message)
            else:
                missing_messages.append(message)
        
        coverage_percentage = (len(covered_messages) / max(len(messages), 1)) * 100
        
        if coverage_percentage >= 80:
            status = "✅ EXCELLENT"
            overall_score = 90
        elif coverage_percentage >= 60:
            status = "✅ GOOD"
            overall_score = 75
        else:
            status = "⚠️ NEEDS IMPROVEMENT"
            overall_score = 60
        
        return {
            'covered': covered_messages,
            'missing': missing_messages,
            'coverage_percentage': round(coverage_percentage, 1),
            'status': status,
            'overall_score': overall_score
        }
    
    def _assess_persona_alignment(self, content: str, persona: str) -> Dict[str, Any]:
        """Assess alignment with persona needs."""
        
        content_lower = content.lower()
        persona_lower = persona.lower()
        
        # Extract pain points from persona
        pain_point_indicators = ['concern', 'pain point', 'challenge', 'problem', 'struggle']
        total_pain_points = sum(persona_lower.count(indicator) for indicator in pain_point_indicators)
        
        # Check if content addresses these
        addressed_indicators = ['address', 'solve', 'eliminate', 'reduce', 'improve']
        addressed_count = sum(content_lower.count(word) for word in addressed_indicators)
        
        pain_points_covered = min(addressed_count, total_pain_points)
        
        relevance_score = min(10, (pain_points_covered / max(total_pain_points, 1)) * 10)
        
        persona_keywords = []
        if 'vp' in persona_lower or 'director' in persona_lower:
            persona_keywords.append('executive')
        if 'sales' in persona_lower:
            persona_keywords.append('sales-focused')
        if 'team' in persona_lower:
            persona_keywords.append('team management')
        
        return {
            'relevance_score': round(relevance_score, 1),
            'pain_points_covered': pain_points_covered,
            'total_pain_points': max(total_pain_points, 1),
            'persona_keywords': persona_keywords,
            'addresses_pain_points': pain_points_covered > 0
        }
    
    def _identify_messaging_gaps(self, message_coverage: Dict, persona_alignment: Dict) -> List[Dict[str, str]]:
        """Identify messaging gaps."""
        gaps = []
        
        if message_coverage['missing']:
            gaps.append({
                'type': 'Missing Key Messages',
                'severity': 'High',
                'details': f"Key messages not covered: {', '.join(message_coverage['missing'])}",
                'impact': 'Content may not convey full value proposition'
            })
        
        if persona_alignment['relevance_score'] < 6:
            gaps.append({
                'type': 'Weak Persona Alignment',
                'severity': 'High',
                'details': 'Content does not adequately address persona pain points',
                'impact': 'May not resonate with target audience'
            })
        
        if not persona_alignment['addresses_pain_points']:
            gaps.append({
                'type': 'Pain Points Not Addressed',
                'severity': 'Critical',
                'details': 'Content fails to explicitly address persona challenges',
                'impact': 'Audience may not see relevance or value'
            })
        
        return gaps
    
    def _format_message_coverage(self, coverage: Dict) -> str:
        """Format message coverage results."""
        output = f"**Coverage:** {coverage['coverage_percentage']}%\n\n"
        
        if coverage['covered']:
            output += "**Messages Present:**\n"
            output += '\n'.join(f"✅ {msg.title()}" for msg in coverage['covered'])
            output += "\n\n"
        
        if coverage['missing']:
            output += "**Messages Missing:**\n"
            output += '\n'.join(f"❌ {msg.title()}" for msg in coverage['missing'])
        
        return output
    
    def _format_persona_alignment(self, alignment: Dict) -> str:
        """Format persona alignment results."""
        output = f"**Pain Points Addressed:** {alignment['addresses_pain_points']}\n"
        output += f"**Persona Context:** {', '.join(alignment['persona_keywords'])}\n"
        
        if alignment['relevance_score'] >= 7:
            output += "\n✅ Content is highly relevant to target persona"
        elif alignment['relevance_score'] >= 5:
            output += "\n⚠️ Content has moderate relevance - strengthen persona-specific examples"
        else:
            output += "\n❌ Content lacks strong persona alignment - add persona-specific pain points and outcomes"
        
        return output
    
    def _format_gaps(self, gaps: List[Dict]) -> str:
        """Format messaging gaps."""
        if not gaps:
            return "✅ No significant messaging gaps identified."
        
        formatted = []
        for i, gap in enumerate(gaps, 1):
            formatted.append(f"""
**Gap #{i}: {gap['type']}**
- Severity: {gap['severity']}
- Details: {gap['details']}
- Impact: {gap['impact']}
""")
        return '\n'.join(formatted)
    
    def _generate_messaging_recommendations(self, gaps: List[Dict], coverage: Dict) -> List[str]:
        """Generate messaging recommendations."""
        recommendations = []
        
        for gap in gaps:
            if gap['type'] == 'Missing Key Messages':
                recommendations.append(f"Add content highlighting: {', '.join(coverage['missing'])}")
            elif gap['type'] == 'Weak Persona Alignment':
                recommendations.append("Include 2-3 specific examples that directly address persona pain points")
            elif gap['type'] == 'Pain Points Not Addressed':
                recommendations.append("Lead with the persona's primary challenge before introducing solution")
        
        if coverage['missing']:
            for message in coverage['missing'][:2]:  # Top 2 missing messages
                recommendations.append(f"Incorporate '{message}' messaging in the results or value proposition section")
        
        if not recommendations:
            recommendations.append("Messaging is well-aligned - maintain current approach")
        
        return recommendations[:5]


# =====================================================
# TOOL 3: Persona Validator
# =====================================================

class PersonaValidationInput(BaseModel):
    """Input schema for Persona Validator."""
    content: str = Field(..., description="Content to validate against persona")
    persona_profile: str = Field(..., description="Full persona profile with demographics, goals, pain points")
    content_brief: str = Field(..., description="Original content brief with persona requirements")


class PersonaValidator(BaseTool):
    name: str = "Persona Validator"
    description: str = """Validates content specificity and relevance to target persona.
    Ensures content speaks directly to persona needs, goals, and context.
    
    IMPORTANT - Input Format:
    - content: STRING with full content to validate
    - persona_profile: STRING with complete profile (e.g., "Sarah Jenkins, VP of Sales at $50M B2B 
      SaaS company. Manages 25-person sales team. Goals: improve forecast accuracy from 65% to 85%, 
      reduce admin burden on reps, increase team quota attainment. Pain points: manual CRM data entry, 
      inconsistent pipeline visibility, high rep turnover due to admin work...")
    - content_brief: STRING with requirements (e.g., "Target: VP of Sales personas. Must address 
      forecast accuracy concerns, showcase team productivity gains, include specific ROI metrics. 
      Tone: executive-level, focus on business impact not features...")
    
    DO NOT pass raw dict/JSON objects. Extract and format as readable text strings.
    
    Use this tool to:
    - Check persona-specific language
    - Validate goals alignment
    - Assess pain point coverage
    - Verify contextual relevance
    
    Returns persona validation report with specificity score."""
    args_schema: Type[BaseModel] = PersonaValidationInput
    
    def _run(self, content: str, persona_profile: str, content_brief: str) -> str:
        """Validate content against persona requirements."""
        
        specificity_score = self._assess_specificity(content, persona_profile)
        goal_alignment = self._check_goal_alignment(content, persona_profile)
        pain_point_coverage = self._check_pain_point_coverage(content, persona_profile)
        brief_compliance = self._check_brief_compliance(content, content_brief)
        
        overall_score = (specificity_score + goal_alignment['score'] + pain_point_coverage['score'] + brief_compliance['score']) / 4
        
        output = f"""## PERSONA VALIDATION REPORT

**Persona:** {persona_profile[:80]}...
**Review Date:** 2025-11-03
**Overall Persona Fit:** {round(overall_score, 1)}/100

---

### SPECIFICITY ASSESSMENT

**Specificity Score:** {specificity_score}/100
**Assessment:** {self._get_specificity_assessment(specificity_score)}

---

### GOAL ALIGNMENT

**Alignment Score:** {goal_alignment['score']}/100
{self._format_goal_alignment(goal_alignment)}

---

### PAIN POINT COVERAGE

**Coverage Score:** {pain_point_coverage['score']}/100
{self._format_pain_point_coverage(pain_point_coverage)}

---

### BRIEF COMPLIANCE

**Compliance Score:** {brief_compliance['score']}/100
{self._format_brief_compliance(brief_compliance)}

---

### RECOMMENDATIONS

{chr(10).join(f'{i+1}. {rec}' for i, rec in enumerate(self._generate_persona_recommendations(specificity_score, goal_alignment, pain_point_coverage)))}

---

**Validation Status:** {'✅ APPROVED' if overall_score >= 75 else '⚠️ NEEDS REVISION'}
"""
        return output
    
    def _assess_specificity(self, content: str, persona: str) -> float:
        """Assess how specific content is to the persona."""
        
        content_lower = content.lower()
        
        score = 60  # Base score
        
        # Check for role-specific language
        if any(role in persona.lower() for role in ['vp', 'director', 'manager', 'executive']):
            role_words = ['team', 'leadership', 'management', 'strategic', 'organizational']
            if any(word in content_lower for word in role_words):
                score += 10
        
        # Check for industry-specific details
        if any(industry in persona.lower() for industry in ['saas', 'software', 'technology', 'healthcare', 'finance']):
            if any(term in content_lower for term in ['industry', 'sector', 'market', 'competitive']):
                score += 10
        
        # Check for company size context
        if any(size in persona.lower() for size in ['enterprise', 'mid-market', 'smb']):
            if any(context in content_lower for context in ['scale', 'size', 'team size', 'organization']):
                score += 10
        
        # Check for specific metrics mentioned
        if any(char.isdigit() for char in content):
            score += 10
        
        return min(100, score)
    
    def _check_goal_alignment(self, content: str, persona: str) -> Dict[str, Any]:
        """Check alignment with persona goals."""
        
        content_lower = content.lower()
        persona_lower = persona.lower()
        
        # Extract goals from persona
        goal_keywords = ['goal', 'objective', 'target', 'aim']
        has_goals = any(keyword in persona_lower for keyword in goal_keywords)
        
        # Check if content addresses achieving goals
        achievement_words = ['achieve', 'reach', 'attain', 'accomplish', 'deliver', 'enable']
        achievement_count = sum(content_lower.count(word) for word in achievement_words)
        
        score = min(100, achievement_count * 15)
        
        return {
            'score': score,
            'has_goal_language': achievement_count > 0,
            'addresses_outcomes': score >= 60
        }
    
    def _check_pain_point_coverage(self, content: str, persona: str) -> Dict[str, Any]:
        """Check coverage of persona pain points."""
        
        content_lower = content.lower()
        persona_lower = persona.lower()
        
        # Pain point indicators
        pain_keywords = ['challenge', 'problem', 'pain', 'struggle', 'difficulty', 'burden']
        persona_pain_count = sum(persona_lower.count(word) for word in pain_keywords)
        
        # Solution indicators in content
        solution_keywords = ['solve', 'address', 'eliminate', 'reduce', 'overcome', 'resolve']
        solution_count = sum(content_lower.count(word) for word in solution_keywords)
        
        coverage_ratio = solution_count / max(persona_pain_count, 1)
        score = min(100, coverage_ratio * 50)
        
        return {
            'score': score,
            'pain_points_identified': persona_pain_count,
            'solutions_presented': solution_count,
            'adequate_coverage': score >= 60
        }
    
    def _check_brief_compliance(self, content: str, brief: str) -> Dict[str, Any]:
        """Check compliance with content brief requirements."""
        
        # Extract requirements from brief
        requirements = []
        if 'must' in brief.lower():
            requirements.append('mandatory requirements present')
        if 'roi' in brief.lower() or 'metric' in brief.lower():
            requirements.append('quantitative metrics')
        if 'tone' in brief.lower():
            requirements.append('tone requirements')
        
        # Simple compliance check - in production would be more sophisticated
        score = 75  # Base compliance score
        
        if 'roi' in brief.lower() and any(char.isdigit() for char in content):
            score += 10
        
        if 'executive' in brief.lower() and len(content.split()) > 800:
            score += 10
        
        return {
            'score': min(100, score),
            'requirements_count': len(requirements),
            'compliant': score >= 70
        }
    
    def _get_specificity_assessment(self, score: float) -> str:
        """Get specificity assessment text."""
        if score >= 85:
            return "Highly specific - content directly addresses persona context"
        elif score >= 70:
            return "Good specificity - persona relevance is clear"
        else:
            return "Generic - content lacks persona-specific details"
    
    def _format_goal_alignment(self, alignment: Dict) -> str:
        """Format goal alignment results."""
        if alignment['addresses_outcomes']:
            return "✅ Content clearly connects to persona goals and desired outcomes"
        else:
            return "⚠️ Content should more explicitly tie to persona's specific goals"
    
    def _format_pain_point_coverage(self, coverage: Dict) -> str:
        """Format pain point coverage results."""
        output = f"**Pain Points in Persona:** {coverage['pain_points_identified']}\n"
        output += f"**Solutions Presented:** {coverage['solutions_presented']}\n\n"
        
        if coverage['adequate_coverage']:
            output += "✅ Content adequately addresses persona pain points"
        else:
            output += "⚠️ Strengthen pain point coverage - add 2-3 specific examples"
        
        return output
    
    def _format_brief_compliance(self, compliance: Dict) -> str:
        """Format brief compliance results."""
        if compliance['compliant']:
            return "✅ Content meets brief requirements"
        else:
            return "⚠️ Review brief requirements - some may not be fully addressed"
    
    def _generate_persona_recommendations(self, specificity: float, goals: Dict, pain_points: Dict) -> List[str]:
        """Generate persona-specific recommendations."""
        recommendations = []
        
        if specificity < 75:
            recommendations.append("Add persona-specific details (role, company size, industry context)")
            recommendations.append("Include examples that match the persona's exact situation")
        
        if not goals['addresses_outcomes']:
            recommendations.append("Explicitly connect outcomes to persona's stated goals")
        
        if not pain_points['adequate_coverage']:
            recommendations.append("Address at least 2-3 specific pain points mentioned in persona profile")
        
        if not recommendations:
            recommendations.append("Persona alignment is strong - content is well-tailored")
        
        return recommendations[:5]


# =====================================================
# TOOL 4: Compliance Checker
# =====================================================

class ComplianceInput(BaseModel):
    """Input schema for Compliance Checker."""
    content: str = Field(..., description="Content to check for compliance issues")
    industry: str = Field(..., description="Industry context for compliance rules")
    content_type: str = Field(..., description="Type of content")


class ComplianceChecker(BaseTool):
    name: str = "Compliance Checker"
    description: str = """Flags potential legal, regulatory, or compliance concerns in content.
    Identifies claims that need disclaimers, regulated terminology, or risk areas.
    
    IMPORTANT - Input Format:
    - content: STRING with full text (e.g., "Our solution guarantees 100% HIPAA compliance and 
      ensures you'll never face a security breach. FDA-approved technology eliminates all risk...")
    - industry: STRING with context (e.g., "Healthcare (HIPAA regulations), handles PHI/PII data, 
      medical device regulations apply, FDA oversight for clinical claims")
    - content_type: STRING with type (e.g., "case_study", "white_paper")
    
    DO NOT pass raw dict/JSON objects. Format as readable text strings.
    
    Use this tool to:
    - Flag absolute guarantees
    - Identify regulated terminology
    - Check for required disclaimers
    - Highlight risk areas
    
    Returns compliance report with flagged issues and recommendations."""
    args_schema: Type[BaseModel] = ComplianceInput
    
    def _run(self, content: str, industry: str, content_type: str) -> str:
        """Check content for compliance issues."""
        
        issues = self._identify_compliance_issues(content, industry)
        risk_level = self._assess_risk_level(issues)
        disclaimers_needed = self._identify_needed_disclaimers(content, industry)
        
        output = f"""## COMPLIANCE REVIEW REPORT

**Industry:** {industry}
**Content Type:** {content_type}
**Review Date:** 2025-11-03
**Risk Level:** {risk_level}

---

### COMPLIANCE ISSUES IDENTIFIED

{self._format_compliance_issues(issues)}

---

### REQUIRED DISCLAIMERS

{self._format_disclaimers(disclaimers_needed)}

---

### RECOMMENDATIONS

{chr(10).join(f'{i+1}. {rec}' for i, rec in enumerate(self._generate_compliance_recommendations(issues, disclaimers_needed)))}

---

**Compliance Status:** {'⚠️ REQUIRES LEGAL REVIEW' if risk_level in ['High', 'Critical'] else '✅ LOW RISK'}
"""
        return output
    
    def _identify_compliance_issues(self, content: str, industry: str) -> List[Dict[str, str]]:
        """Identify potential compliance issues."""
        issues = []
        
        content_lower = content.lower()
        
        # Check for absolute guarantees
        guarantee_words = ['guarantee', 'guaranteed', '100%', 'ensures', 'never fail', 'always']
        if any(word in content_lower for word in guarantee_words):
            issues.append({
                'type': 'Absolute Guarantee',
                'severity': 'High',
                'description': 'Content contains absolute guarantees that may not be legally defensible',
                'location': 'Value propositions and results claims'
            })
        
        # Healthcare-specific
        if 'health' in industry.lower() or 'hipaa' in industry.lower():
            if 'hipaa' in content_lower:
                issues.append({
                    'type': 'HIPAA Claims',
                    'severity': 'Critical',
                    'description': 'HIPAA compliance claims require legal verification and proper disclaimers',
                    'location': 'Compliance and security sections'
                })
        
        # Financial services
        if 'financ' in industry.lower() or 'sec' in industry.lower():
            regulated_terms = ['approved', 'certified', 'guaranteed returns']
            if any(term in content_lower for term in regulated_terms):
                issues.append({
                    'type': 'Regulated Financial Claims',
                    'severity': 'Critical',
                    'description': 'Financial services claims may violate SEC or FINRA regulations',
                    'location': 'Performance and results sections'
                })
        
        # FDA-related
        if 'fda' in content_lower:
            issues.append({
                'type': 'FDA Claims',
                'severity': 'Critical',
                'description': 'FDA approval/certification claims must be verified and properly documented',
                'location': 'Product description'
            })
        
        return issues
    
    def _assess_risk_level(self, issues: List[Dict]) -> str:
        """Assess overall compliance risk level."""
        if not issues:
            return "Low"
        
        severity_levels = [issue['severity'] for issue in issues]
        
        if 'Critical' in severity_levels:
            return "Critical"
        elif 'High' in severity_levels:
            return "High"
        else:
            return "Medium"
    
    def _identify_needed_disclaimers(self, content: str, industry: str) -> List[str]:
        """Identify needed disclaimers."""
        disclaimers = []
        
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['result', 'outcome', 'roi', 'saving']):
            disclaimers.append("Results may vary. Outcomes are based on specific customer implementations.")
        
        if 'health' in industry.lower() or 'medical' in industry.lower():
            disclaimers.append("This information is not medical advice. Consult appropriate professionals.")
        
        if 'financ' in industry.lower():
            disclaimers.append("Past performance does not guarantee future results.")
        
        if not disclaimers:
            disclaimers.append("No specific disclaimers required")
        
        return disclaimers
    
    def _format_compliance_issues(self, issues: List[Dict]) -> str:
        """Format compliance issues."""
        if not issues:
            return "✅ No compliance issues identified."
        
        formatted = []
        for i, issue in enumerate(issues, 1):
            formatted.append(f"""
**Issue #{i}: {issue['type']}**
- Severity: {issue['severity']}
- Description: {issue['description']}
- Location: {issue['location']}
""")
        return '\n'.join(formatted)
    
    def _format_disclaimers(self, disclaimers: List[str]) -> str:
        """Format required disclaimers."""
        if disclaimers[0] == "No specific disclaimers required":
            return "✅ No specific disclaimers required for this content."
        
        return '\n'.join(f'- {disclaimer}' for disclaimer in disclaimers)
    
    def _generate_compliance_recommendations(self, issues: List[Dict], disclaimers: List[str]) -> List[str]:
        """Generate compliance recommendations."""
        recommendations = []
        
        for issue in issues:
            if issue['severity'] == 'Critical':
                recommendations.append(f"URGENT: Obtain legal review for {issue['type']} before publishing")
            elif issue['severity'] == 'High':
                recommendations.append(f"Remove or qualify {issue['type']} claims to reduce legal risk")
        
        if disclaimers and disclaimers[0] != "No specific disclaimers required":
            recommendations.append("Add required disclaimers in footer or prominent location")
        
        if any('guarantee' in issue['type'].lower() for issue in issues):
            recommendations.append("Replace absolute guarantees with conditional statements (e.g., 'typically achieves' instead of 'guarantees')")
        
        if not recommendations:
            recommendations.append("Content appears compliant - no immediate legal concerns identified")
        
        return recommendations
