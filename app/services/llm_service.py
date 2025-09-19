import openai
import json
from typing import List, Dict, Any, Tuple
from app.models import LogEntry, FilteredLog
from app.utils.cost_calculator import OpenAICostCalculator
import os
from dotenv import load_dotenv

load_dotenv()


class LLMService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"  # Updated to use cost-effective model
        self.total_cost = 0.0

    def analyze_logs(self, logs: List[LogEntry], user_prompt: str) -> Tuple[List[FilteredLog], float, str]:
        """
        Analyze logs using LLM to find relevant entries and highlight important ones
        """
        if not logs:
            return [], 0.0, "No logs to analyze"

        # Convert logs to a more readable format for the LLM
        logs_text = self._format_logs_for_llm(logs)

        # Create the analysis prompt
        analysis_prompt = f"""
        You are a log analysis expert. Analyze the following logs for incidents related to: "{user_prompt}"

        For each log entry, determine:
        1. Relevance score (0.0 to 1.0) - how relevant this log is to the incident
        2. Brief reason for the relevance score

        Only include logs with relevance score > 0.3 in your response.

        Logs to analyze:
        {logs_text}

        Respond with a JSON object in this exact format:
        {{
            "filtered_logs": [
                {{
                    "log_index": 0,
                    "relevance_score": 0.8,
                    "relevance_reason": "Shows error in cart service"
                }}
            ],
            "summary": "Brief summary of findings"
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert log analyst. Always respond with valid JSON."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )

            # Calculate cost
            cost = OpenAICostCalculator.calculate_cost(
                self.model,
                response.usage.prompt_tokens,
                response.usage.completion_tokens
            )
            self.total_cost += cost

            # Parse the response
            response_content = response.choices[0].message.content
            analysis_result = json.loads(response_content)

            # Build filtered logs list
            filtered_logs = []
            for item in analysis_result.get("filtered_logs", []):
                log_index = item["log_index"]
                if 0 <= log_index < len(logs):
                    filtered_log = FilteredLog(
                        log_entry=logs[log_index],
                        relevance_score=item["relevance_score"],
                        relevance_reason=item["relevance_reason"]
                    )
                    filtered_logs.append(filtered_log)

            summary = analysis_result.get("summary", "Analysis completed")

            return filtered_logs, cost, summary

        except Exception as e:
            print(f"Error in LLM analysis: {e}")
            return [], 0.0, f"Error during analysis: {str(e)}"

    def _format_logs_for_llm(self, logs: List[LogEntry]) -> str:
        """Format logs in a readable way for LLM analysis"""
        formatted = []
        for i, log in enumerate(logs):
            formatted.append(f"[{i}] Container: {log.containerName} | Namespace: {log.namespace} | Log: {log.log}")
        return "\n".join(formatted)