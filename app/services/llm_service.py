from typing import List, Dict, Any
import openai
from fastapi import HTTPException
from app.config.settings import settings
from app.config.costs import model_costs


class LLMService:
    def __init__(self):
        openai.api_key = settings.openai_api_key
        self.model = settings.analysis_model

    async def analyze_logs(self, logs: List[Dict[str, Any]], prompt: str) -> Dict[str, Any]:
        """Analyze filtered logs using LLM"""
        if not logs:
            return {
                "analysis": "No relevant logs found for the given prompt",
                "cost": 0,
                "logs_analyzed": 0
            }

        # Limit logs for cost control
        analysis_logs = logs[:settings.max_logs_for_analysis]

        # Prepare context for LLM
        log_context = self._prepare_flexible_log_context(analysis_logs)
        analysis_prompt = self._create_analysis_prompt(prompt, log_context)

        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system",
                     "content": "You are an expert log analyzer helping with incident investigation. Provide concise, actionable insights."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )

            cost = self._calculate_analysis_cost(analysis_prompt, response.choices[0].message.content)

            return {
                "analysis": response.choices[0].message.content,
                "cost": cost,
                "logs_analyzed": len(analysis_logs)
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error analyzing logs with LLM: {str(e)}")

    def _prepare_flexible_log_context(self, logs: List[Dict[str, Any]]) -> str:
        """Prepare log entries for LLM analysis - works with any log format"""
        log_lines = []
        for i, log in enumerate(logs, 1):
            # Get similarity score if available
            similarity = log.get('_similarity_score', 0)

            # Try to extract timestamp from common field names
            timestamp = self._extract_timestamp(log)

            # Try to extract main message/content
            main_content = self._extract_main_content(log)

            # Format for LLM
            log_line = f"Log {i} (similarity: {similarity:.3f}):"
            if timestamp:
                log_line += f" [{timestamp}]"
            log_line += f" {main_content}"

            log_lines.append(log_line)

        return "\n".join(log_lines)

    def _extract_timestamp(self, log: Dict[str, Any]) -> str:
        """Extract timestamp from various possible fields"""
        timestamp_fields = ['timestamp', 'time', '@timestamp', 'date', 'datetime', 'created_at']
        for field in timestamp_fields:
            if field in log and log[field]:
                return str(log[field])
        return ""

    def _extract_main_content(self, log: Dict[str, Any]) -> str:
        """Extract the main content/message from the log"""
        # Try message fields first
        message_fields = ['message', 'msg', 'log', 'content', 'description']
        for field in message_fields:
            if field in log and log[field]:
                return str(log[field])

        # If no message field, create a summary of key-value pairs
        excluded_fields = {'_similarity_score', '_extracted_text', 'timestamp', '@timestamp', 'time'}
        parts = []
        for key, value in log.items():
            if key not in excluded_fields and value and len(str(value)) < 100:
                parts.append(f"{key}={value}")

        return "; ".join(parts[:5])  # Limit to first 5 fields

    def _create_analysis_prompt(self, user_prompt: str, log_context: str) -> str:
        """Create the analysis prompt for the LLM"""
        return f"""
        Analyze the following logs for the incident: "{user_prompt}"

        Logs (ordered by semantic relevance to the incident):
        {log_context}

        Please provide:
        1. **Summary**: What's happening based on these logs?
        2. **Root Cause**: Most likely cause of the incident
        3. **Critical Logs**: Which specific log entries are most important?
        4. **Recommended Actions**: What should be done to resolve this?

        Be concise and focus on actionable insights. The logs are already filtered for relevance.
        """

    def _calculate_analysis_cost(self, input_text: str, output_text: str) -> float:
        """Calculate cost for LLM analysis using centralized costs"""
        # Estimate token counts
        input_tokens = model_costs.estimate_token_count(input_text)
        output_tokens = model_costs.estimate_token_count(output_text)

        # Use centralized cost calculation
        return round(model_costs.calculate_chat_completion_cost(self.model, input_tokens, output_tokens), 6)