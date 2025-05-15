import pytest
from utils.rate_limiter import RateLimiter

@pytest.mark.asyncio
async def test_rate_limiter():
    limiter = RateLimiter(max_calls=2, period=0.1)
    
    # First two calls should pass
    assert await limiter.wait() is None
    assert await limiter.wait() is None
    
    # Third call should be rate-limited
    wait_time = await limiter.wait()
    assert wait_time is not None
    assert 0.09 <= wait_time <= 0.1  # Should wait ~period duration