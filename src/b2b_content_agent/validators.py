"""Validation utilities for CREW 1 inputs and outputs.

This module provides validation functions to ensure:
1. Input files/URLs are valid before processing
2. Agent outputs meet quality standards
3. Data flows correctly between agents
"""

import logging
from pathlib import Path
from typing import Optional, Tuple
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# =====================================================
# INPUT VALIDATION
# =====================================================

class InputValidationError(Exception):
    """Raised when input validation fails."""
    pass


def validate_input_file(file_path: Path) -> Tuple[bool, Optional[str]]:
    """Validate an input file before processing.
    
    Args:
        file_path: Path to the input file
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Checks:
        - File exists and is readable
        - File size is reasonable (< 50MB)
        - File format is supported
        - File is not empty
    """
    # Check if file exists
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    # Check if file is readable
    if not file_path.is_file():
        return False, f"Not a file: {file_path}"
    
    try:
        # Check file size (max 50MB)
        file_size = file_path.stat().st_size
        if file_size == 0:
            return False, f"File is empty: {file_path}"
        
        if file_size > 50 * 1024 * 1024:  # 50MB
            return False, f"File too large ({file_size / 1024 / 1024:.1f}MB). Maximum size is 50MB."
        
        # Check file format
        supported_extensions = ['.pdf', '.docx', '.txt', '.md', '.doc']
        if file_path.suffix.lower() not in supported_extensions:
            return False, f"Unsupported file format: {file_path.suffix}. Supported formats: {', '.join(supported_extensions)}"
        
        # Try to read a few bytes to ensure file is readable
        with open(file_path, 'rb') as f:
            f.read(100)
        
        return True, None
        
    except PermissionError:
        return False, f"Permission denied: Cannot read {file_path}"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """Validate a URL before scraping.
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Checks:
        - Valid URL format
        - Has http/https scheme
        - Not obviously malicious
    """
    if not url or not isinstance(url, str):
        return False, "URL is empty or invalid type"
    
    # Check URL format
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            return False, "URL missing scheme (http/https)"
        if parsed.scheme not in ['http', 'https']:
            return False, f"Invalid URL scheme: {parsed.scheme}. Must be http or https"
        if not parsed.netloc:
            return False, "URL missing domain"
        
        # Basic blacklist check
        blacklisted_domains = ['localhost', '127.0.0.1', '0.0.0.0']
        if any(domain in parsed.netloc.lower() for domain in blacklisted_domains):
            return False, f"Localhost URLs are not allowed: {parsed.netloc}"
        
        return True, None
        
    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"


def validate_inputs(input_file: Optional[Path] = None, url: Optional[str] = None) -> None:
    """Validate all inputs before starting CREW 1.
    
    Args:
        input_file: Optional path to input file
        url: Optional URL to scrape
        
    Raises:
        InputValidationError: If validation fails
    """
    errors = []
    
    if input_file:
        is_valid, error = validate_input_file(input_file)
        if not is_valid:
            errors.append(f"File validation failed: {error}")
    
    if url:
        is_valid, error = validate_url(url)
        if not is_valid:
            errors.append(f"URL validation failed: {error}")
    
    if not input_file and not url:
        errors.append("No input provided. Please provide either a file or URL.")
    
    if errors:
        raise InputValidationError("\n".join(errors))


# =====================================================
# OUTPUT VALIDATION
# =====================================================

class OutputValidationError(Exception):
    """Raised when output validation fails."""
    pass


def validate_product_analysis(file_path: Path) -> Tuple[bool, list]:
    """Validate product analysis output file.
    
    Args:
        file_path: Path to 01_product_analysis.md
        
    Returns:
        Tuple of (is_valid, list_of_errors)
        
    Checks:
        - File exists and has content
        - Word count > 100
        - Contains required sections
        - Has minimum data quality
    """
    errors = []
    
    # Check file exists
    if not file_path.exists():
        errors.append("Product analysis file not generated")
        return False, errors
    
    try:
        content = file_path.read_text()
        
        # Check minimum length
        word_count = len(content.split())
        if word_count < 100:
            errors.append(f"Product analysis too short: {word_count} words (minimum: 100)")
        
        # Check for required sections
        required_sections = [
            "PRODUCT OVERVIEW",
            "FEATURES",
            "BENEFITS",
            "USE CASES",
            "TARGET MARKET"
        ]
        
        for section in required_sections:
            if section.lower() not in content.lower():
                errors.append(f"Missing required section: {section}")
        
        # Check for some actual content (not just headers)
        # Count lines that are not headers (not starting with #)
        content_lines = [line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        if len(content_lines) < 20:
            errors.append(f"Insufficient content: only {len(content_lines)} content lines")
        
        return len(errors) == 0, errors
        
    except Exception as e:
        errors.append(f"Error reading product analysis: {str(e)}")
        return False, errors


def validate_persona_library(file_path: Path, min_personas: int = 10) -> Tuple[bool, list]:
    """Validate persona library output file.
    
    Args:
        file_path: Path to 02_persona_library.md
        min_personas: Minimum number of personas required
        
    Returns:
        Tuple of (is_valid, list_of_errors)
        
    Checks:
        - File exists and has content
        - Minimum number of personas (default: 10)
        - Each persona has required fields
        - Diversity check (different industries/roles)
    """
    errors = []
    
    # Check file exists
    if not file_path.exists():
        errors.append("Persona library file not generated")
        return False, errors
    
    try:
        content = file_path.read_text()
        
        # Count personas (look for "### Persona #" pattern)
        persona_pattern = r'###\s+Persona\s+#\d+'
        persona_matches = re.findall(persona_pattern, content)
        persona_count = len(persona_matches)
        
        if persona_count < min_personas:
            errors.append(f"Insufficient personas: {persona_count} found (minimum: {min_personas})")
        
        # Check for required persona fields (should appear multiple times)
        required_fields = [
            "Profile Overview",
            "Context:",
            "Challenges & Pain Points",
            "Goals & Success Metrics",
            "Product Fit",
            "Buying Behavior"
        ]
        
        for field in required_fields:
            if content.count(field) < min_personas * 0.8:  # At least 80% of personas should have this
                errors.append(f"Many personas missing required field: {field}")
        
        # Check for diversity (should have different industries mentioned)
        if content.lower().count("industry") < 3:
            errors.append("Insufficient industry diversity in personas")
        
        # Check minimum length
        word_count = len(content.split())
        if word_count < 500:
            errors.append(f"Persona library too short: {word_count} words (minimum: 500)")
        
        return len(errors) == 0, errors
        
    except Exception as e:
        errors.append(f"Error reading persona library: {str(e)}")
        return False, errors


def validate_content_strategy(file_path: Path, expected_briefs: Optional[int] = None) -> Tuple[bool, list]:
    """Validate content strategy output file.
    
    Args:
        file_path: Path to 03_content_strategy.md
        expected_briefs: Optional expected number of content briefs
        
    Returns:
        Tuple of (is_valid, list_of_errors)
        
    Checks:
        - File exists and has content
        - Has content assignment matrix
        - Number of briefs matches personas
        - Briefs have required sections
    """
    errors = []
    
    # Check file exists
    if not file_path.exists():
        errors.append("Content strategy file not generated")
        return False, errors
    
    try:
        content = file_path.read_text()
        
        # Check for main sections
        if "CONTENT ASSIGNMENT MATRIX" not in content:
            errors.append("Missing content assignment matrix")
        
        if "CONTENT BRIEF" not in content.upper():
            errors.append("No content briefs found")
        
        # Count content briefs
        brief_pattern = r'###\s+Content\s+Brief\s+#\d+'
        brief_matches = re.findall(brief_pattern, content)
        brief_count = len(brief_matches)
        
        if brief_count == 0:
            errors.append("No content briefs generated")
        elif expected_briefs and brief_count < expected_briefs:
            errors.append(f"Insufficient content briefs: {brief_count} found (expected: {expected_briefs})")
        
        # Check for required brief sections (should appear in most briefs)
        required_brief_sections = [
            "Target Persona",
            "Strategic Context",
            "Key Messages",
            "Pain Points",
            "Value Propositions"
        ]
        
        for section in required_brief_sections:
            if content.count(section) < brief_count * 0.8:
                errors.append(f"Many briefs missing required section: {section}")
        
        # Check minimum length
        word_count = len(content.split())
        if word_count < 500:
            errors.append(f"Content strategy too short: {word_count} words (minimum: 500)")
        
        return len(errors) == 0, errors
        
    except Exception as e:
        errors.append(f"Error reading content strategy: {str(e)}")
        return False, errors


def validate_crew1_outputs(output_dir: Path) -> None:
    """Validate all CREW 1 outputs.
    
    Args:
        output_dir: Directory containing output files
        
    Raises:
        OutputValidationError: If validation fails
    """
    all_errors = []
    
    logger.info("Validating CREW 1 outputs...")
    
    # Validate product analysis
    product_file = output_dir / "01_product_analysis.md"
    is_valid, errors = validate_product_analysis(product_file)
    if not is_valid:
        all_errors.append("Product Analysis validation failed:")
        all_errors.extend([f"  - {e}" for e in errors])
    else:
        logger.info("✓ Product analysis validation passed")
    
    # Validate persona library
    persona_file = output_dir / "02_persona_library.md"
    is_valid, errors = validate_persona_library(persona_file, min_personas=10)
    if not is_valid:
        all_errors.append("Persona Library validation failed:")
        all_errors.extend([f"  - {e}" for e in errors])
    else:
        logger.info("✓ Persona library validation passed")
        
        # Extract persona count for next validation
        content = persona_file.read_text()
        persona_count = len(re.findall(r'###\s+Persona\s+#\d+', content))
    
    # Validate content strategy
    strategy_file = output_dir / "03_content_strategy.md"
    expected_briefs = persona_count if 'persona_count' in locals() else None
    is_valid, errors = validate_content_strategy(strategy_file, expected_briefs)
    if not is_valid:
        all_errors.append("Content Strategy validation failed:")
        all_errors.extend([f"  - {e}" for e in errors])
    else:
        logger.info("✓ Content strategy validation passed")
    
    # Raise error if any validation failed
    if all_errors:
        error_message = "\n".join(all_errors)
        raise OutputValidationError(f"Output validation failed:\n{error_message}")
    
    logger.info("✅ All CREW 1 outputs validated successfully")
