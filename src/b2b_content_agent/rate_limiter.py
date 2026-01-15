"""Rate Limiting and Retry Logic for API Calls

This module provides intelligent rate limiting and error recovery for LLM API calls:
- Request spacing to prevent bursts
- Exponential backoff for 429 errors
- Request tracking and statistics
- Configurable limits for different API tiers
"""

import time
import logging
from collections import deque
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting behavior"""
    
    # Request rate limits
    requests_per_minute: int = 50  # Conservative default for free tier
    min_request_gap: float = 5.0   # Minimum 5 seconds between requests (for Groq TPM limit)
    
    # Retry configuration
    max_retries: int = 5
    initial_backoff: float = 3.0    # Initial retry delay in seconds (increased from 2.0)
    backoff_multiplier: float = 2.0  # Exponential backoff multiplier
    max_backoff: float = 300.0      # Maximum backoff (5 minutes)
    
    # Budget controls
    max_api_calls: Optional[int] = None  # Stop after N calls (None = unlimited)
    warn_threshold: Optional[int] = None  # Warn when approaching limit
    
    # Logging
    verbose: bool = False  # Show detailed rate limiting info
    log_every_n: int = 10  # Log summary every N requests


@dataclass
class RateLimitStats:
    """Statistics tracking for rate limiting"""
    
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0
    total_wait_time: float = 0.0
    total_retry_time: float = 0.0
    request_times: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def log_summary(self):
        """Log summary statistics"""
        logger.info("=" * 80)
        logger.info("RATE LIMITING STATISTICS")
        logger.info("=" * 80)
        logger.info(f"Total API Requests: {self.total_requests}")
        logger.info(f"  ✅ Successful: {self.successful_requests}")
        logger.info(f"  ❌ Failed: {self.failed_requests}")
        logger.info(f"  ⏸️  Rate Limited: {self.rate_limited_requests}")
        logger.info(f"Total Wait Time: {self.total_wait_time:.1f}s")
        logger.info(f"Total Retry Time: {self.total_retry_time:.1f}s")
        
        if len(self.request_times) > 1:
            recent_requests = len(self.request_times)
            time_span = self.request_times[-1] - self.request_times[0]
            if time_span > 0:
                rate = recent_requests / time_span * 60
                logger.info(f"Recent Request Rate: {rate:.1f} requests/minute")
        
        logger.info("=" * 80)


class RateLimiter:
    """Intelligent rate limiter for API calls with retry logic"""
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        Initialize rate limiter
        
        Args:
            config: Rate limiting configuration (uses defaults if None)
        """
        self.config = config or RateLimitConfig()
        self.stats = RateLimitStats()
        self._last_request_time: Optional[float] = None
        
        logger.info(f"Rate Limiter initialized: {self.config.requests_per_minute} req/min")
        if self.config.max_api_calls:
            logger.info(f"Budget limit: {self.config.max_api_calls} requests")
    
    def wait_if_needed(self) -> float:
        """
        Wait before making next request if needed to respect rate limits
        
        Returns:
            Time waited in seconds
        """
        if self._last_request_time is None:
            return 0.0
        
        # Calculate time since last request
        time_since_last = time.time() - self._last_request_time
        
        # Check if we need to wait based on minimum gap
        if time_since_last < self.config.min_request_gap:
            wait_time = self.config.min_request_gap - time_since_last
            
            if self.config.verbose:
                logger.info(f"⏸️  Rate limiting: waiting {wait_time:.2f}s before next request")
            
            time.sleep(wait_time)
            self.stats.total_wait_time += wait_time
            return wait_time
        
        # Check requests per minute limit
        if len(self.stats.request_times) >= self.config.requests_per_minute:
            oldest_request = self.stats.request_times[0]
            time_window = time.time() - oldest_request
            
            if time_window < 60:
                # We've hit the rate limit, wait until we can make another request
                wait_time = 60 - time_window
                
                logger.warning(
                    f"⏸️  Rate limit approaching: {len(self.stats.request_times)} "
                    f"requests in {time_window:.1f}s. Waiting {wait_time:.1f}s..."
                )
                
                time.sleep(wait_time)
                self.stats.total_wait_time += wait_time
                return wait_time
        
        return 0.0
    
    def check_budget(self) -> bool:
        """
        Check if we're within API call budget
        
        Returns:
            True if within budget, False if budget exhausted
        """
        if self.config.max_api_calls is None:
            return True
        
        # Check if budget exhausted
        if self.stats.total_requests >= self.config.max_api_calls:
            logger.error(
                f"❌ API call budget exhausted: {self.stats.total_requests}/{self.config.max_api_calls}"
            )
            return False
        
        # Warn if approaching limit
        if self.config.warn_threshold:
            if self.stats.total_requests >= self.config.warn_threshold:
                remaining = self.config.max_api_calls - self.stats.total_requests
                logger.warning(
                    f"⚠️  Approaching API call budget: {self.stats.total_requests}/{self.config.max_api_calls} "
                    f"({remaining} remaining)"
                )
        
        return True
    
    def log_request(self, success: bool = True):
        """
        Log a request for tracking
        
        Args:
            success: Whether the request was successful
        """
        now = time.time()
        self._last_request_time = now
        self.stats.request_times.append(now)
        self.stats.total_requests += 1
        
        if success:
            self.stats.successful_requests += 1
        else:
            self.stats.failed_requests += 1
        
        # Periodic logging
        if self.config.verbose and self.stats.total_requests % self.config.log_every_n == 0:
            logger.info(
                f"📊 API Requests: {self.stats.total_requests} total "
                f"({self.stats.successful_requests} successful, "
                f"{self.stats.failed_requests} failed)"
            )
    
    def handle_rate_limit_error(
        self,
        error: Exception,
        attempt: int,
        context: str = ""
    ) -> tuple[bool, float]:
        """
        Handle rate limit error with exponential backoff
        
        Args:
            error: The exception that was raised
            attempt: Current retry attempt number (0-indexed)
            context: Description of what operation failed
            
        Returns:
            Tuple of (should_retry, wait_time)
        """
        self.stats.rate_limited_requests += 1
        
        # Check if we should retry
        if attempt >= self.config.max_retries:
            logger.error(
                f"❌ Max retries ({self.config.max_retries}) exceeded for {context}. "
                f"Giving up."
            )
            return False, 0.0
        
        # Calculate exponential backoff
        wait_time = min(
            self.config.initial_backoff * (self.config.backoff_multiplier ** attempt),
            self.config.max_backoff
        )
        
        # Try to extract retry delay from error message
        error_msg = str(error)
        if "retry in" in error_msg.lower():
            try:
                # Extract suggested delay from error message
                # Format: "Please retry in 6.208361554s."
                parts = error_msg.split("retry in")[1].split("s")[0].strip()
                suggested_delay = float(parts)
                wait_time = max(wait_time, suggested_delay)
            except (ValueError, IndexError):
                pass  # Use calculated backoff if parsing fails
        
        logger.warning(
            f"⏳ Rate limit hit (attempt {attempt + 1}/{self.config.max_retries}): {context}. "
            f"Retrying in {wait_time:.1f}s..."
        )
        
        time.sleep(wait_time)
        self.stats.total_retry_time += wait_time
        
        return True, wait_time
    
    def execute_with_retry(
        self,
        func: Callable,
        *args,
        context: str = "API call",
        **kwargs
    ) -> Any:
        """
        Execute a function with automatic retry on rate limit errors
        
        Args:
            func: Function to execute
            *args: Positional arguments for func
            context: Description of the operation
            **kwargs: Keyword arguments for func
            
        Returns:
            Result of func
            
        Raises:
            Exception: If all retries are exhausted or budget exceeded
        """
        # Check budget before starting
        if not self.check_budget():
            raise RuntimeError("API call budget exhausted")
        
        # Wait if needed for rate limiting
        self.wait_if_needed()
        
        attempt = 0
        last_error = None
        
        while attempt <= self.config.max_retries:
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Log successful request
                self.log_request(success=True)
                
                return result
                
            except Exception as e:
                last_error = e
                error_msg = str(e)
                
                # Check if it's a rate limit error or quota exhausted
                is_rate_limit = (
                    "429" in error_msg or
                    "RESOURCE_EXHAUSTED" in error_msg or
                    "quota" in error_msg.lower() or
                    "rate limit" in error_msg.lower()
                )
                
                # Check if it's a quota exhausted error (not just throttling)
                is_quota_exhausted = (
                    "quota exceeded" in error_msg.lower() or
                    "current quota" in error_msg.lower() or
                    ("RESOURCE_EXHAUSTED" in error_msg and "quota" in error_msg.lower())
                )
                
                if is_quota_exhausted:
                    # Quota fully exhausted - need to switch providers
                    logger.error(
                        f"❌ API quota exhausted for {context}!\n"
                        f"   Error: {error_msg[:200]}...\n"
                        f"   This requires switching to a fallback LLM provider."
                    )
                    self.log_request(success=False)
                    # Re-raise with clear message that provider needs to switch
                    raise RuntimeError(
                        f"API quota exhausted. Please add a fallback provider API key "
                        f"(GROQ_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY) to .env"
                    ) from e
                
                elif is_rate_limit:
                    # Temporary rate limiting - retry with backoff
                    self.log_request(success=False)
                    
                    # Handle with exponential backoff
                    should_retry, wait_time = self.handle_rate_limit_error(
                        e, attempt, context
                    )
                    
                    if not should_retry:
                        raise
                    
                    attempt += 1
                else:
                    # Not a rate limit error, raise immediately
                    self.log_request(success=False)
                    raise
        
        # All retries exhausted
        logger.error(f"❌ All retries exhausted for {context}")
        raise last_error
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get current statistics
        
        Returns:
            Dictionary of statistics
        """
        return {
            "total_requests": self.stats.total_requests,
            "successful_requests": self.stats.successful_requests,
            "failed_requests": self.stats.failed_requests,
            "rate_limited_requests": self.stats.rate_limited_requests,
            "total_wait_time": self.stats.total_wait_time,
            "total_retry_time": self.stats.total_retry_time,
            "recent_request_count": len(self.stats.request_times)
        }
    
    def reset_stats(self):
        """Reset statistics (useful between crew runs)"""
        self.stats = RateLimitStats()
        logger.info("Rate limiter statistics reset")


# Global rate limiter instance (can be configured via environment or config)
_global_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter(config: Optional[RateLimitConfig] = None) -> RateLimiter:
    """
    Get or create global rate limiter instance
    
    Args:
        config: Configuration (only used on first call)
        
    Returns:
        Global RateLimiter instance
    """
    global _global_rate_limiter
    
    if _global_rate_limiter is None:
        _global_rate_limiter = RateLimiter(config)
    
    return _global_rate_limiter


def reset_rate_limiter():
    """Reset global rate limiter (useful for testing)"""
    global _global_rate_limiter
    _global_rate_limiter = None
