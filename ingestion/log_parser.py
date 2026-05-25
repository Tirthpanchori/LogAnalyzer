import json
import re

def parse_python_log(line):
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+) (\w+) ([\w-]+): (.+)'
    match = re.match(pattern, line)
    if match:
        return {
            "timestamp": match.group(1),
            "log_level": match.group(2),
            "service_name": match.group(3),
            "message": match.group(4)
        }
    return None

def parse_nginx_log(line):
    pattern = r'(\S+) - - \[(.+?)\] "(\S+) (\S+) (\d+) ([\d.]+)"'
    match = re.match(pattern, line)
    if match:
        return {
            "timestamp": match.group(2),
            "method": match.group(3),
            "path": match.group(4),
            "status_code": match.group(5),
            "response_time": match.group(6),
            "service_name": "nginx",
            "log_level": "ERROR" if match.group(5).startswith("5") else "INFO"
        }
    return None

def parse_json_log(line):
    try:
        log_entry = json.loads(line)
        return {
            "timestamp": log_entry.get("timestamp", ""),
            "log_level": log_entry.get("log_level", ""),
            "service_name": log_entry.get("service_name", ""),
            "message": log_entry.get("message", "")
        }
    except json.JSONDecodeError:
        return None