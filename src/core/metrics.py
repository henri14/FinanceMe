import json

import aiofiles
from loguru import logger


class MetricsCollector:
    def __init__(self):
        pass

    async def collect(self, usage, cost, latency):
        text = f"[stats] Tokens prompt: {usage.input_tokens}, completion: {usage.output_tokens}, cost: ${cost:.6f}, latency: {latency:.2f}ms"
        logger.info(text)
        data = {
            "prompt_tokens": usage.input_tokens,
            "completion_tokens": usage.output_tokens,
            "cost": cost,
            "latency": latency,
        }
        async with aiofiles.open("data/metrics.jsonl", "a") as f:
            await f.write(json.dumps(data) + "\n")
