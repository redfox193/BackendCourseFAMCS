import asyncio
import pytest


async def get_answer_after_delay(delay: float) -> int:
    await asyncio.sleep(delay)
    return 42


@pytest.mark.asyncio
async def test_get_answer_after_delay():
    result = await get_answer_after_delay(0)
    assert result == 42