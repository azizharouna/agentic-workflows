import asyncio
import time
from typing import Optional

class RateLimiter:
    def __init__(self, max_calls: int = 5, period: float = 1.0):
        """
        Args:
            max_calls: Maximum calls allowed per period
            period: Time window in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.lock = asyncio.Lock()

    async def wait(self) -> Optional[float]:
        """Returns wait time if rate limit is hit"""
        async with self.lock:
            now = time.time()
            
            # Remove calls outside current period
            self.calls = [t for t in self.calls if now - t < self.period]
            
            if len(self.calls) >= self.max_calls:
                wait_time = self.period - (now - self.calls[0])
                await asyncio.sleep(wait_time)
                return wait_time
            
            self.calls.append(now)
            return None