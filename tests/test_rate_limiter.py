"""Test rate limiter functionality"""

import time
from b2b_content_agent.rate_limiter import RateLimiter, RateLimitConfig


def test_basic_rate_limiting():
    """Test basic rate limiting with request spacing"""
    config = RateLimitConfig(
        min_request_gap=0.5,  # 500ms between requests
        verbose=True
    )
    limiter = RateLimiter(config)
    
    print("Testing basic rate limiting...")
    start = time.time()
    
    # Make 5 requests
    for i in range(5):
        wait_time = limiter.wait_if_needed()
        limiter.log_request(success=True)
        print(f"Request {i+1}: waited {wait_time:.2f}s")
    
    total_time = time.time() - start
    print(f"\nTotal time for 5 requests: {total_time:.2f}s")
    print(f"Expected minimum: {0.5 * 4:.2f}s (4 gaps)")
    
    stats = limiter.get_stats()
    print(f"\nStats: {stats}")
    
    assert total_time >= 2.0, "Should take at least 2 seconds (4 * 0.5s gaps)"
    assert stats['total_requests'] == 5
    assert stats['successful_requests'] == 5
    
    print("✅ Basic rate limiting test passed!")


def test_rate_limit_error_handling():
    """Test handling of rate limit errors"""
    config = RateLimitConfig(
        max_retries=3,
        initial_backoff=0.1,
        verbose=True
    )
    limiter = RateLimiter(config)
    
    print("\n\nTesting rate limit error handling...")
    
    # Simulate a function that fails with rate limit error
    attempt_count = [0]
    
    def flaky_function():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise Exception("429 RESOURCE_EXHAUSTED - Rate limit exceeded")
        return "Success!"
    
    try:
        result = limiter.execute_with_retry(
            flaky_function,
            context="Test function"
        )
        print(f"\nResult after {attempt_count[0]} attempts: {result}")
        assert result == "Success!"
        assert attempt_count[0] == 3
        print("✅ Rate limit error handling test passed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise


def test_budget_limit():
    """Test API call budget limit"""
    config = RateLimitConfig(
        max_api_calls=3,
        warn_threshold=2,
        verbose=True
    )
    limiter = RateLimiter(config)
    
    print("\n\nTesting budget limit...")
    
    # Make 2 requests (should warn)
    for i in range(2):
        assert limiter.check_budget()
        limiter.log_request(success=True)
        print(f"Request {i+1} logged")
    
    # Make 3rd request (should still work but be at limit)
    assert limiter.check_budget()
    limiter.log_request(success=True)
    print("Request 3 logged")
    
    # 4th request should fail
    assert not limiter.check_budget()
    print("✅ Budget limit test passed!")


if __name__ == "__main__":
    test_basic_rate_limiting()
    test_rate_limit_error_handling()
    test_budget_limit()
    
    print("\n" + "="*80)
    print("✅ ALL RATE LIMITER TESTS PASSED!")
    print("="*80)
