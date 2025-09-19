import json
from typing import List, Dict, Any
from app.models import LogEntry


class LogProcessor:
    @staticmethod
    def parse_json_logs(file_content: bytes) -> List[LogEntry]:
        """
        Parse JSON log file content into LogEntry objects
        Supports both single JSON objects and JSONL format
        """
        try:
            content_str = file_content.decode('utf-8')
            logs = []

            # Try to parse as JSONL (one JSON object per line)
            lines = content_str.strip().split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                try:
                    log_data = json.loads(line)
                    log_entry = LogEntry(**log_data)
                    logs.append(log_entry)
                except json.JSONDecodeError:
                    # If single line fails, try parsing entire content as JSON array
                    if len(lines) == 1:
                        try:
                            json_data = json.loads(content_str)
                            if isinstance(json_data, list):
                                for item in json_data:
                                    logs.append(LogEntry(**item))
                            else:
                                logs.append(LogEntry(**json_data))
                        except (json.JSONDecodeError, TypeError):
                            continue
                except Exception as e:
                    print(f"Error parsing log entry: {e}")
                    continue

            return logs

        except Exception as e:
            print(f"Error processing log file: {e}")
            return []

    @staticmethod
    def basic_filter_logs(logs: List[LogEntry], prompt: str) -> List[LogEntry]:
        """
        Basic filtering based on prompt keywords
        This is a pre-filter before LLM analysis
        """
        if not prompt:
            return logs

        keywords = prompt.lower().split()
        filtered = []

        for log in logs:
            log_text = f"{log.containerName} {log.namespace} {log.log}".lower()

            # Check if any keyword matches
            if any(keyword in log_text for keyword in keywords):
                filtered.append(log)

        # If no matches found with keyword filtering, return all logs
        # This ensures we don't miss relevant logs due to strict filtering
        return filtered if filtered else logs