from backend.app.config import (
    USD_TO_NPR_RATE,
    COST_PER_1K_PROMPT_TOKENS_USD,
    COST_PER_1K_COMPLETION_TOKENS_USD
)

class CostTracker:
    @staticmethod
    def calculate_cost_npr(prompt_tokens: int, completion_tokens: int) -> float:
        cost_usd = (
            (prompt_tokens / 1000.0) * COST_PER_1K_PROMPT_TOKENS_USD +
            (completion_tokens / 1000.0) * COST_PER_1K_COMPLETION_TOKENS_USD
        )
        cost_npr = cost_usd * USD_TO_NPR_RATE
        return round(cost_npr, 4)
