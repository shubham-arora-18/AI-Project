class OpenAICostCalculator:
    # Updated pricing as of September 2025
    # Source: https://openai.com/api/pricing/
    PRICING = {
        "gpt-4o-mini": {
            "input": 0.15 / 1000000,  # $0.15 per 1M input tokens
            "output": 0.60 / 1000000  # $0.60 per 1M output tokens
        },
        "gpt-4o": {
            "input": 2.50 / 1000000,  # $2.50 per 1M input tokens
            "output": 10.00 / 1000000  # $10.00 per 1M output tokens
        },
        "gpt-5": {
            "input": 1.25 / 1000000,  # $1.25 per 1M input tokens
            "output": 10.00 / 1000000  # $10.00 per 1M output tokens
        },
        "gpt-5-mini": {
            "input": 0.25 / 1000000,  # $0.25 per 1M input tokens
            "output": 1.00 / 1000000  # $1.00 per 1M output tokens
        },
        "gpt-3.5-turbo": {
            "input": 0.50 / 1000000,  # $0.50 per 1M input tokens
            "output": 1.50 / 1000000  # $1.50 per 1M output tokens
        },
        "o1-mini": {
            "input": 1.10 / 1000000,  # $1.10 per 1M input tokens
            "output": 4.40 / 1000000  # $4.40 per 1M output tokens
        },
        "o1": {
            "input": 15.00 / 1000000,  # $15.00 per 1M input tokens
            "output": 60.00 / 1000000  # $60.00 per 1M output tokens
        }
    }

    @classmethod
    def calculate_cost(cls, model: str, input_tokens: int, output_tokens: int) -> float:
        if model not in cls.PRICING:
            # Default to most cost-effective option for unknown models
            model = "gpt-4o-mini"

        input_cost = input_tokens * cls.PRICING[model]["input"]
        output_cost = output_tokens * cls.PRICING[model]["output"]

        return round(input_cost + output_cost, 8)  # Increased precision for lower costs