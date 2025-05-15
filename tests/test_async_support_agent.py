import asyncio
import pytest
from agents.support_agent import support_agent


@pytest.mark.asyncio
async def test_async_agent_response():
    result = await support_agent("test")
    assert result.confidence >= 0


from datetime import datetime, timedelta


class RateLimiter:
    def __init__(self, max_calls=5, period=1):
        self.calls = []
        self.max_calls = max_calls
        self.period = period  # seconds

    async def wait(self):
        now = datetime.now()
        self.calls = [t for t in self.calls if now - t < timedelta(seconds=self.period)]
        if len(self.calls) >= self.max_calls:
            await asyncio.sleep(
                (self.calls[0] + timedelta(seconds=self.period) - now).total_seconds()
            )
        self.calls.append(now)
