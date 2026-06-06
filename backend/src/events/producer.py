from datetime import datetime
from typing import Any, Dict
import json
import asyncpg


class EventProducer:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def publish(self, event_type: str, payload: Dict[str, Any], actor_id=None, actor_type=None, source="backend", correlation_id=None):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO events (event_type, actor_id, actor_type, source, correlation_id, payload, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, NOW())
                """,
                event_type,
                actor_id,
                actor_type,
                source,
                correlation_id,
                json.dumps(payload),
            )
