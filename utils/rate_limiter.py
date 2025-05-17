import asyncio
import time
from typing import Optional, List
from dataclasses import dataclass
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

@dataclass
class RateLimitConfig:
    max_calls: int = 5
    period: float = 1.0  # in seconds
    max_retries: int = 3
    backoff_base: float = 1.5

class RateLimitExceededError(Exception):
    pass

class EnhancedRateLimiter:
    def __init__(self, config: RateLimitConfig = RateLimitConfig()):
        self.config = config
        self.calls: List[float] = []
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger("rate_limiter")

    async def wait(self) -> Optional[float]:
        """Enhanced rate limiting with better error handling"""
        for attempt in range(self.config.max_retries):
            try:
                async with self.lock:
                    now = time.time()
                    
                    # Clean up old calls
                    self.calls = [t for t in self.calls if now - t < self.config.period]
                    
                    if len(self.calls) < self.config.max_calls:
                        self.calls.append(now)
                        return None
                        
                    # Calculate wait time with backoff
                    wait_time = self._calculate_wait_time(now, attempt)
                    self.logger.debug(f"Rate limit hit, waiting {wait_time:.2f}s (attempt {attempt + 1})")
                    await asyncio.sleep(wait_time)
                    
            except Exception as e:
                self.logger.error(f"Rate limiter error: {type(e).__name__} - {str(e)}")
                if attempt == self.config.max_retries - 1:
                    raise RateLimitExceededError("Max retries exceeded")
                await asyncio.sleep(self.config.backoff_base ** attempt)
                
        return None

    def _calculate_wait_time(self, current_time: float, attempt: int) -> float:
        """Calculate wait time with exponential backoff"""
        base_wait = max(0, self.config.period - (current_time - self.calls[0]))
        return base_wait * (self.config.backoff_base ** attempt)

    async def __aenter__(self):
        await self.wait()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

# Pre-configured limiters for different agent types
SUPPORT_AGENT_LIMITER = EnhancedRateLimiter(
    RateLimitConfig(
        max_calls=10,
        period=1.0,
        max_retries=5
    )
)

PREMIUM_AGENT_LIMITER = EnhancedRateLimiter(
    RateLimitConfig(
        max_calls=20,
        period=1.0,
        max_retries=3
    )
)