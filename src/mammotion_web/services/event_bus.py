from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import AsyncIterator, DefaultDict, Dict


class EventBus:
    """Simple asyncio pub-sub event bus.

    Topics are strings, payloads arbitrary JSON-serializable objects.
    """

    def __init__(self) -> None:
        self._topics: DefaultDict[str, asyncio.Queue] = defaultdict(asyncio.Queue)

    async def publish(self, topic: str, payload) -> None:
        await self._topics[topic].put(payload)

    async def subscribe(self, topic: str) -> AsyncIterator:
        queue = self._topics[topic]
        while True:
            item = await queue.get()
            yield item
