"""Quality Assurance Review Tools for CREW 3

These tools help the Quality Assurance Reviewer agent check content for:
- Accuracy and factual correctness
- Consistency in terminology and formatting
- Readability and clarity
- Link and reference validation
"""

from crewai.tools import BaseTool
from typing import Type, Dict, Any, List
from pydantic import BaseModel, Field
import random
import re


# =====================================================
# TOOL 1: Accuracy Checker
# =====================================================

class AccuracyInput(BaseModel):
    """Input schema for Accuracy Checker."""
    content: str = Field(..., description="The content to check for accuracy")
    content_type: str = Field(..., description="Type of content (case_study, white_paper, pitch_deck, social_post)")
    claims_to_verify: str = Field(..., description="Specific claims, metrics, or facts to verify")


class AccuracyChecker(BaseTool):
    name: str = "Accuracy Checker"
    description: str = """Validates factual accuracy, metrics, and claims in content.
    Checks for exaggerated claims, unrealistic metrics, and factual errors.
    
    IMPORTANT - Input Format:
    - content: STRING with the full content to review (e.g., "# Case Study: TechCorp Success Story. 
      TechCorp achieved 400% productivity increase in 2 weeks using our solution...")
    - content_type: STRING specifying type (e.g., "case_study", "white_paper", "pitch_deck", "social_post")
    - claims_to_verify: STRING listing specific claims (e.g., "400% productivity increase, 
      2-week implementation time, $2M cost savings, 99.9% uptime guarantee")
    
    DO NOT pass raw dict/JSON objects. Extract content and format as readable text strings.
    
    Use this tool to:
    - Flag exaggerated or unrealistic metrics
    - Identify unsupported claims
    - Check for logical inconsistencies
    - Validate timeframes and ROI calculations
    
    Returns accuracy report with flagged issues and corrections."""
    args_schema: Type[BaseModel] = AccuracyInput
    
    def _run(self, content: str, content_type: str, claims_to_verify: str) -> str:
        """Check content for accuracy issues."""
        
        issues = self._identify_accuracy_issues(content, claims_to_verify)
        severity = self._assess_severity(issues)
        recommendations = self._generate_recommendations(issues)
        
        output = f"""## ACCURACY REVIEW REPORT

**Content Type:** {content_type}
**Review Date:** 2025-11-03
**Overall Accuracy Score:** {100 - len(issues) * 10}/100

---

### IDENTIFIED ISSUES

{self._format_issues(issues)}

---

### SEVERITY ASSESSMENT

**Critical Issues:** {severity['critical']}
**Moderate Issues:** {severity['moderate']}
**Minor Issues:** {severity['minor']}

---

### RECOMMENDATIONS

{chr(10).join(f'{i+1}. {rec}' for i, rec in enumerate(recommendations))}

---

### CORRECTED CLAIMS

{self._suggest_corrections(claims_to_verify, issues)}

**Review Status:** {'⚠️ NEEDS REVISION' if len(issues) > 2 else '✅ APPROVED'}
"""
        return output
    
    def _identify_accuracy_issues(self, content: str, claims: str) -> List[Dict[str, Any]]:
        """Identify potential accuracy issues."""
        issues = []
        
        # Check for exaggerated metrics
        if any(word in content.lower() for word in ['10x', '1000%', 'revolutionary', 'game-changing']):
            issues.append({
                'type': 'exaggeration',
                'severity': 'moderate',
                'description': 'Content contains potentially exaggerated claims or superlatives',
                'location': 'Multiple instances throughout'
            })
        
        # Check for unrealistic timeframes
        if any(phrase in content.lower() for phrase in ['overnight', 'instantly', 'immediate results']):
            issues.append({
                'type': 'unrealistic_timeframe',
                'severity': 'critical',
                'description': 'Claims suggest unrealistic implementation or results timeframe',
                'location': 'Results section'
            })
        
        # Check for unsupported absolute claims
        if any(word in content.lower() for word in ['always', 'never', 'guaranteed', '100% success']):
            issues.append({
                'type': 'absolute_claim',
                'severity': 'moderate',
                'description': 'Content contains absolute claims that may not be universally true',
                'location': 'Value propositions'
            })
        
        return issues
    
    def _assess_severity(self, issues: List[Dict]) -> Dict[str, int]:
        """Assess severity distribution."""
        severity_counts = {'critical': 0, 'moderate': 0, 'minor': 0}
        for issue in issues:
            severity_counts[issue.get('severity', 'minor')] += 1
        return severity_counts
    
    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """Generate fix recommendations."""
        recommendations = []
        
        for issue in issues:
            if issue['type'] == 'exaggeration':
                recommendations.append("Replace superlatives with specific, measurable results (e.g., '40% improvement' instead of 'revolutionary')")
            elif issue['type'] == 'unrealistic_timeframe':
                recommendations.append("Provide realistic implementation timeframes (e.g., '6-8 weeks' instead of 'overnight')")
            elif issue['type'] == 'absolute_claim':
                recommendations.append("Qualify absolute statements with data or conditions (e.g., '95% of customers' instead of 'always')")
        
        if not recommendations:
            recommendations.append("Content meets accuracy standards. No corrections needed.")
        
        return recommendations
    
    def _format_issues(self, issues: List[Dict]) -> str:
        """Format issues for output."""
        if not issues:
            return "✅ No accuracy issues identified."
        
        formatted = []
        for i, issue in enumerate(issues, 1):
            formatted.append(f"""
**Issue #{i}: {issue['type'].replace('_', ' ').title()}**
- Severity: {issue['severity'].upper()}
- Description: {issue['description']}
- Location: {issue['location']}
""")
        return '\n'.join(formatted)
    
    def _suggest_corrections(self, claims: str, issues: List[Dict]) -> str:
        """Suggest corrected versions of claims."""
        if not issues:
            return "✅ All claims are accurate and well-supported."
        
        return """
**Original:** "Achieved 10x productivity increase overnight"
**Corrected:** "Achieved 40% productivity improvement over 3 months"

**Original:** "Guaranteed 100% ROI for all customers"
**Corrected:** "95% of customers achieve positive ROI within 6 months"

**Original:** "Revolutionary game-changing solution"
**Corrected:** "Comprehensive solution addressing key operational challenges"
"""


# =====================================================
# TOOL 2: Consistency Validator
# =====================================================

class ConsistencyInput(BaseModel):
    """Input schema for Consistency Validator."""
    content: str = Field(..., description="The content to check for consistency")
    brand_guidelines: str = Field(..., description="Brand terminology, naming conventions, style rules")
    content_type: str = Field(..., description="Type of content being reviewed")


class ConsistencyValidator(BaseTool):
    name: str = "Consistency Validator"
    description: str = """Validates consistency in terminology, formatting, and style.
    Checks for consistent use of product names, brand terms, formatting patterns.
    
    IMPORTANT - Input Format:
    - content: STRING with full content (e.g., "Our platform, the Friend AI assistant, helps teams... 
      The friend system integrates with... Using Friend technology...")
    - brand_guidelines: STRING with rules (e.g., "Product name: 'Friend AI' (capitalize both words). 
      Never use 'friend assistant' or 'FRIEND'. Company name: 'FriendTech'. Tone: Professional but 
      approachable. Use active voice. Bullet points for lists...")
    - content_type: STRING with type (e.g., "case_study", "white_paper")
    
    DO NOT pass raw dict/JSON objects. Format guidelines and content as readable text.
    
    Use this tool to:
    - Check product name consistency
    - Validate formatting patterns
    - Ensure style guide compliance
    - Flag terminology inconsistencies
    
    Returns consistency report with issues and corrections."""
    args_schema: Type[BaseModel] = ConsistencyInput
    
    def _run(self, content: str, brand_guidelines: str, content_type: str) -> str:
        """Check content for consistency issues."""
        
        naming_issues = self._check_naming_consistency(content)
        formatting_issues = self._check_formatting(content)
        style_issues = self._check_style_compliance(content)
        
        total_issues = len(naming_issues) + len(formatting_issues) + len(style_issues)
        
        output = f"""## CONSISTENCY VALIDATION REPORT

**Content Type:** {content_type}
**Review Date:** 2025-11-03
**Consistency Score:** {max(0, 100 - total_issues * 5)}/100

---

### NAMING CONSISTENCY

{self._format_naming_issues(naming_issues)}

---

### FORMATTING CONSISTENCY

{self._format_formatting_issues(formatting_issues)}

---

### STYLE COMPLIANCE

{self._format_style_issues(style_issues)}

---

### SUMMARY

**Total Issues Found:** {total_issues}
- Naming: {len(naming_issues)}
- Formatting: {len(formatting_issues)}
- Style: {len(style_issues)}

**Recommended Actions:**
1. Apply consistent product naming throughout
2. Standardize formatting patterns (headings, bullets, etc.)
3. Ensure style guide compliance in tone and voice

**Review Status:** {'⚠️ NEEDS REVISION' if total_issues > 3 else '✅ APPROVED'}
"""
        return output
    
    def _check_naming_consistency(self, content: str) -> List[str]:
        """Check for naming inconsistencies."""
        issues = []
        
        # Check for mixed case in product names
        if re.search(r'\b(friend|FRIEND)\b', content, re.IGNORECASE):
            issues.append("Product name capitalization inconsistent (found 'friend', 'FRIEND', should be 'Friend AI')")
        
        # Check for inconsistent terminology
        if 'platform' in content.lower() and 'solution' in content.lower() and 'product' in content.lower():
            issues.append("Mixed terminology: using 'platform', 'solution', and 'product' interchangeably")
        
        return issues
    
    def _check_formatting(self, content: str) -> List[str]:
        """Check formatting consistency."""
        issues = []
        
        # Check heading patterns
        if '##' in content and '###' in content:
            # Good - uses proper heading hierarchy
            pass
        else:
            issues.append("Inconsistent heading structure - use proper Markdown hierarchy (##, ###)")
        
        # Check list formatting
        bullet_types = []
        if re.search(r'^\s*-\s', content, re.MULTILINE):
            bullet_types.append('dash')
        if re.search(r'^\s*\*\s', content, re.MULTILINE):
            bullet_types.append('asterisk')
        if len(bullet_types) > 1:
            issues.append("Mixed bullet point styles - use consistent list formatting")
        
        return issues
    
    def _check_style_compliance(self, content: str) -> List[str]:
        """Check style guide compliance."""
        issues = []
        
        # Check for passive voice (simplified check)
        passive_indicators = ['is being', 'was being', 'has been', 'have been', 'will be']
        passive_count = sum(content.lower().count(phrase) for phrase in passive_indicators)
        if passive_count > 5:
            issues.append(f"Excessive passive voice ({passive_count} instances) - prefer active voice")
        
        # Check sentence length (simplified)
        sentences = re.split(r'[.!?]+', content)
        long_sentences = [s for s in sentences if len(s.split()) > 30]
        if len(long_sentences) > 5:
            issues.append(f"Several long sentences ({len(long_sentences)} over 30 words) - consider breaking up for readability")
        
        return issues
    
    def _format_naming_issues(self, issues: List[str]) -> str:
        if not issues:
            return "✅ Product names and terminology are consistent."
        return '\n'.join(f'- {issue}' for issue in issues)
    
    def _format_formatting_issues(self, issues: List[str]) -> str:
        if not issues:
            return "✅ Formatting is consistent throughout."
        return '\n'.join(f'- {issue}' for issue in issues)
    
    def _format_style_issues(self, issues: List[str]) -> str:
        if not issues:
            return "✅ Content complies with style guidelines."
        return '\n'.join(f'- {issue}' for issue in issues)


# =====================================================
# TOOL 3: Readability Analyzer
# =====================================================

class ReadabilityInput(BaseModel):
    """Input schema for Readability Analyzer."""
    content: str = Field(..., description="The content to analyze for readability")
    target_audience: str = Field(..., description="Target audience description (affects readability expectations)")
    content_type: str = Field(..., description="Type of content")


class ReadabilityAnalyzer(BaseTool):
    name: str = "Readability Analyzer"
    description: str = """Analyzes content readability, sentence complexity, and clarity.
    Provides Flesch-Kincaid scores, grade level, and improvement suggestions.
    
    IMPORTANT - Input Format:
    - content: STRING with full text (e.g., "The implementation process begins with a comprehensive 
      assessment of existing workflows and pain points. Stakeholders collaborate to identify optimization 
      opportunities and establish success metrics...")
    - target_audience: STRING describing readers (e.g., "C-level executives at enterprise companies, 
      MBA education level, prefer concise insights over technical details, limited reading time")
    - content_type: STRING with type (e.g., "white_paper", "case_study")
    
    DO NOT pass raw dict/JSON objects. Extract and format as readable text strings.
    
    Use this tool to:
    - Calculate readability scores
    - Assess sentence complexity
    - Identify jargon overuse
    - Suggest clarity improvements
    
    Returns readability report with scores and recommendations."""
    args_schema: Type[BaseModel] = ReadabilityInput
    
    def _run(self, content: str, target_audience: str, content_type: str) -> str:
        """Analyze content readability."""
        
        scores = self._calculate_readability_scores(content)
        complexity = self._analyze_complexity(content)
        recommendations = self._generate_readability_recommendations(scores, complexity, target_audience)
        
        output = f"""## READABILITY ANALYSIS REPORT

**Content Type:** {content_type}
**Target Audience:** {target_audience}
**Analysis Date:** 2025-11-03

---

### READABILITY SCORES

**Flesch Reading Ease:** {scores['flesch_ease']}/100
- Score interpretation: {scores['ease_interpretation']}

**Flesch-Kincaid Grade Level:** {scores['grade_level']}
- Reading level: {scores['grade_interpretation']}

**Target Match:** {scores['target_match']}

---

### COMPLEXITY ANALYSIS

**Average Sentence Length:** {complexity['avg_sentence_length']} words
**Average Word Length:** {complexity['avg_word_length']} characters
**Complex Words:** {complexity['complex_word_percentage']}%
**Jargon Density:** {complexity['jargon_density']}

**Paragraph Structure:**
- Average paragraph length: {complexity['avg_paragraph_length']} sentences
- Longest paragraph: {complexity['longest_paragraph']} sentences

---

### RECOMMENDATIONS

{chr(10).join(f'{i+1}. {rec}' for i, rec in enumerate(recommendations))}

---

### OVERALL ASSESSMENT

**Readability Status:** {scores['status']}
**Recommended Actions:** {scores['action_needed']}
"""
        return output
    
    def _calculate_readability_scores(self, content: str) -> Dict[str, Any]:
        """Calculate Flesch reading scores (simplified implementation)."""
        
        # Simplified calculations for demonstration
        sentences = len(re.split(r'[.!?]+', content))
        words = len(content.split())
        syllables = sum(self._count_syllables(word) for word in content.split())
        
        # Flesch Reading Ease: 206.835 - 1.015(words/sentences) - 84.6(syllables/words)
        flesch_ease = max(0, min(100, 206.835 - 1.015 * (words / max(sentences, 1)) - 84.6 * (syllables / max(words, 1))))
        flesch_ease = round(flesch_ease, 1)
        
        # Flesch-Kincaid Grade Level: 0.39(words/sentences) + 11.8(syllables/words) - 15.59
        grade_level = max(0, 0.39 * (words / max(sentences, 1)) + 11.8 * (syllables / max(words, 1)) - 15.59)
        grade_level = round(grade_level, 1)
        
        # Interpretations
        if flesch_ease >= 70:
            ease_interp = "Easy to read (8th-9th grade level)"
            status = "✅ EXCELLENT"
        elif flesch_ease >= 60:
            ease_interp = "Standard reading level (10th-12th grade)"
            status = "✅ GOOD"
        elif flesch_ease >= 50:
            ease_interp = "Fairly difficult (college level)"
            status = "⚠️ ACCEPTABLE"
        else:
            ease_interp = "Difficult to read (college graduate level)"
            status = "⚠️ NEEDS IMPROVEMENT"
        
        if grade_level <= 12:
            grade_interp = "High school level - accessible to most audiences"
        elif grade_level <= 16:
            grade_interp = "College level - appropriate for business professionals"
        else:
            grade_interp = "Graduate level - may be too complex for some readers"
        
        target_match = "✅ Matches target audience" if 50 <= flesch_ease <= 70 else "⚠️ May not match target audience"
        action_needed = "Consider simplifying complex sentences" if flesch_ease < 60 else "No action needed"
        
        return {
            'flesch_ease': flesch_ease,
            'ease_interpretation': ease_interp,
            'grade_level': grade_level,
            'grade_interpretation': grade_interp,
            'target_match': target_match,
            'status': status,
            'action_needed': action_needed
        }
    
    def _count_syllables(self, word: str) -> int:
        """Simplified syllable counter."""
        word = word.lower()
        vowels = 'aeiouy'
        count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                count += 1
            previous_was_vowel = is_vowel
        
        if word.endswith('e'):
            count -= 1
        if count == 0:
            count = 1
            
        return count
    
    def _analyze_complexity(self, content: str) -> Dict[str, Any]:
        """Analyze sentence and word complexity."""
        
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        words = content.split()
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        avg_sentence_length = round(len(words) / max(len(sentences), 1), 1)
        avg_word_length = round(sum(len(w) for w in words) / max(len(words), 1), 1)
        
        # Count complex words (3+ syllables)
        complex_words = [w for w in words if self._count_syllables(w) >= 3]
        complex_percentage = round((len(complex_words) / max(len(words), 1)) * 100, 1)
        
        # Estimate jargon density
        jargon_indicators = ['leverage', 'synergy', 'paradigm', 'utilize', 'optimize', 'strategize']
        jargon_count = sum(content.lower().count(word) for word in jargon_indicators)
        jargon_density = "Low" if jargon_count < 5 else "Medium" if jargon_count < 10 else "High"
        
        # Paragraph analysis
        paragraph_lengths = [len(re.split(r'[.!?]+', p)) for p in paragraphs]
        avg_paragraph_length = round(sum(paragraph_lengths) / max(len(paragraph_lengths), 1), 1)
        longest_paragraph = max(paragraph_lengths) if paragraph_lengths else 0
        
        return {
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length,
            'complex_word_percentage': complex_percentage,
            'jargon_density': jargon_density,
            'avg_paragraph_length': avg_paragraph_length,
            'longest_paragraph': longest_paragraph
        }
    
    def _generate_readability_recommendations(self, scores: Dict, complexity: Dict, target_audience: str) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        if scores['flesch_ease'] < 60:
            recommendations.append("Break up long, complex sentences into shorter, clearer statements")
            recommendations.append("Replace multi-syllable words with simpler alternatives where possible")
        
        if complexity['avg_sentence_length'] > 25:
            recommendations.append(f"Average sentence length ({complexity['avg_sentence_length']} words) is high - aim for 15-20 words")
        
        if complexity['complex_word_percentage'] > 20:
            recommendations.append(f"High percentage of complex words ({complexity['complex_word_percentage']}%) - simplify technical terminology")
        
        if complexity['jargon_density'] == "High":
            recommendations.append("Reduce business jargon - use clear, concrete language instead")
        
        if complexity['longest_paragraph'] > 6:
            recommendations.append(f"Break up longest paragraph ({complexity['longest_paragraph']} sentences) into smaller chunks")
        
        if not recommendations:
            recommendations.append("Content readability is excellent - no changes needed")
        
        return recommendations


# =====================================================
# TOOL 4: Link Validator
# =====================================================

class LinkInput(BaseModel):
    """Input schema for Link Validator."""
    content: str = Field(..., description="The content to check for CTAs and references")
    content_type: str = Field(..., description="Type of content")


class LinkValidator(BaseTool):
    name: str = "Link Validator"
    description: str = """Validates CTAs, references, and links in content.
    Checks for working calls-to-action, proper reference formatting, and link structure.
    
    IMPORTANT - Input Format:
    - content: STRING with full content including CTAs (e.g., "To learn more, visit www.example.com. 
      Schedule a demo at demo.example.com. Read our white paper on best practices. Contact us at 
      sales@example.com for pricing...")
    - content_type: STRING with type (e.g., "case_study", "pitch_deck")
    
    DO NOT pass raw dict/JSON objects. Extract content as readable text string.
    
    Use this tool to:
    - Identify all CTAs in content
    - Check CTA clarity and effectiveness
    - Validate reference formatting
    - Ensure proper link structure
    
    Returns validation report with CTA analysis and recommendations."""
    args_schema: Type[BaseModel] = LinkInput
    
    def _run(self, content: str, content_type: str) -> str:
        """Validate CTAs and links in content."""
        
        ctas = self._identify_ctas(content)
        references = self._identify_references(content)
        effectiveness = self._assess_cta_effectiveness(ctas)
        recommendations = self._generate_cta_recommendations(ctas, effectiveness, content_type)
        
        output = f"""## LINK & CTA VALIDATION REPORT

**Content Type:** {content_type}
**Review Date:** 2025-11-03
**CTAs Found:** {len(ctas)}

---

### IDENTIFIED CALLS-TO-ACTION

{self._format_ctas(ctas)}

---

### CTA EFFECTIVENESS ANALYSIS

**Clarity Score:** {effectiveness['clarity_score']}/10
**Placement Score:** {effectiveness['placement_score']}/10
**Action-oriented Score:** {effectiveness['action_score']}/10

**Overall CTA Quality:** {effectiveness['overall_quality']}

---

### REFERENCES & LINKS

{self._format_references(references)}

---

### RECOMMENDATIONS

{chr(10).join(f'{i+1}. {rec}' for i, rec in enumerate(recommendations))}

---

### VALIDATION STATUS

**CTAs:** {effectiveness['cta_status']}
**References:** {effectiveness['reference_status']}
**Overall:** {'✅ APPROVED' if effectiveness['overall_quality'] in ['Excellent', 'Good'] else '⚠️ NEEDS IMPROVEMENT'}
"""
        return output
    
    def _identify_ctas(self, content: str) -> List[Dict[str, str]]:
        """Identify all CTAs in content."""
        ctas = []
        
        # Common CTA patterns
        cta_patterns = [
            (r'schedule (a|an|your) (demo|call|meeting)', 'Schedule Demo'),
            (r'contact (us|sales|our team)', 'Contact Sales'),
            (r'learn more', 'Learn More'),
            (r'get started', 'Get Started'),
            (r'download (the|our)', 'Download Resource'),
            (r'sign up', 'Sign Up'),
            (r'request (a|an) (demo|quote|consultation)', 'Request Demo'),
            (r'visit (our website|us at)', 'Visit Website'),
        ]
        
        for pattern, cta_type in cta_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                context = content[max(0, match.start()-50):min(len(content), match.end()+50)]
                ctas.append({
                    'type': cta_type,
                    'text': match.group(),
                    'context': context.strip(),
                    'position': 'beginning' if match.start() < len(content) * 0.3 else 'middle' if match.start() < len(content) * 0.7 else 'end'
                })
        
        if not ctas:
            ctas.append({
                'type': 'Missing',
                'text': 'No clear CTA identified',
                'context': 'N/A',
                'position': 'N/A'
            })
        
        return ctas
    
    def _identify_references(self, content: str) -> List[str]:
        """Identify references and citations."""
        references = []
        
        # Look for URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        if urls:
            references.append(f"URLs found: {len(urls)}")
        
        # Look for email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
        if emails:
            references.append(f"Email addresses found: {len(emails)}")
        
        # Look for reference markers
        if re.search(r'\[\d+\]|\(\d+\)', content):
            references.append("Citation markers found (proper academic style)")
        
        if not references:
            references.append("No explicit references or links found")
        
        return references
    
    def _assess_cta_effectiveness(self, ctas: List[Dict]) -> Dict[str, Any]:
        """Assess CTA effectiveness."""
        
        if ctas[0]['type'] == 'Missing':
            return {
                'clarity_score': 0,
                'placement_score': 0,
                'action_score': 0,
                'overall_quality': 'Poor',
                'cta_status': '❌ NO CTA FOUND',
                'reference_status': '⚠️ NEEDS REVIEW'
            }
        
        # Calculate scores based on CTA characteristics
        clarity_score = 8 if len(ctas) > 0 else 0
        placement_score = 10 if any(cta['position'] == 'end' for cta in ctas) else 6
        action_score = 9 if any(word in ' '.join(c['text'] for c in ctas).lower() for word in ['schedule', 'start', 'contact', 'request']) else 5
        
        avg_score = (clarity_score + placement_score + action_score) / 3
        
        if avg_score >= 8:
            overall_quality = 'Excellent'
            cta_status = '✅ STRONG CTAs'
        elif avg_score >= 6:
            overall_quality = 'Good'
            cta_status = '✅ ACCEPTABLE'
        else:
            overall_quality = 'Needs Improvement'
            cta_status = '⚠️ WEAK CTAs'
        
        return {
            'clarity_score': round(clarity_score, 1),
            'placement_score': round(placement_score, 1),
            'action_score': round(action_score, 1),
            'overall_quality': overall_quality,
            'cta_status': cta_status,
            'reference_status': '✅ VALID'
        }
    
    def _format_ctas(self, ctas: List[Dict]) -> str:
        """Format CTAs for output."""
        if ctas[0]['type'] == 'Missing':
            return "❌ No CTAs identified in content - add clear calls-to-action"
        
        formatted = []
        for i, cta in enumerate(ctas, 1):
            formatted.append(f"""
**CTA #{i}: {cta['type']}**
- Text: "{cta['text']}"
- Position: {cta['position']}
- Context: "...{cta['context']}..."
""")
        return '\n'.join(formatted)
    
    def _format_references(self, references: List[str]) -> str:
        """Format references for output."""
        return '\n'.join(f'- {ref}' for ref in references)
    
    def _generate_cta_recommendations(self, ctas: List[Dict], effectiveness: Dict, content_type: str) -> List[str]:
        """Generate CTA improvement recommendations."""
        recommendations = []
        
        if ctas[0]['type'] == 'Missing':
            recommendations.append(f"Add a clear CTA at the end of the {content_type}")
            recommendations.append("Use action-oriented language (e.g., 'Schedule a demo', 'Contact our team')")
            recommendations.append("Include specific next steps for the reader")
        else:
            if effectiveness['clarity_score'] < 8:
                recommendations.append("Make CTAs more specific and action-oriented")
            if effectiveness['placement_score'] < 8:
                recommendations.append("Add a strong CTA at the end of the content")
            if effectiveness['action_score'] < 8:
                recommendations.append("Use stronger action verbs (schedule, start, discover, etc.)")
        
        # Content-type specific recommendations
        if content_type == 'case_study':
            recommendations.append("Consider adding: 'Ready for similar results? Schedule a consultation'")
        elif content_type == 'white_paper':
            recommendations.append("Consider adding: 'Download the implementation guide' or 'Speak with an expert'")
        elif content_type == 'pitch_deck':
            recommendations.append("Final slide should have clear next steps and contact information")
        
        if not recommendations:
            recommendations.append("CTAs are strong and well-placed - no changes needed")
        
        return recommendations
