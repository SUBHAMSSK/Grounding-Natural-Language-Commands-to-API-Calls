import json
from datetime import datetime

class MockServices:
    def __init__(self):
        self.state = {
            "calendar": [],
            "outbox": [],
            "reminders": [],
            "files": [
                {"name": "project_report.pdf", "type": "pdf", "date": "2024-01-10"},
                {"name": "budget.xlsx", "type": "xlsx", "date": "2024-01-12"}
            ],
            "tasks": []
        }

    def schedule_meeting(self, title: str, attendees: list[str], date: str, time: str, duration_min: int) -> str:
        event = {"title": title, "attendees": attendees, "date": date, "time": time, "duration": duration_min}
        self.state["calendar"].append(event)
        return f"Meeting '{title}' added"

    def send_email(self, to: str, subject: str, body: str, cc: list[str] = []) -> str:
        email = {"to": to, "subject": subject, "body": body, "cc": cc}
        self.state["outbox"].append(email)
        return f"Email queued to {to}"

    def set_reminder(self, message: str, datetime: str, repeat: str) -> str:
        reminder = {"message": message, "datetime": datetime, "repeat": repeat}
        self.state["reminders"].append(reminder)
        return f"Reminder set: '{message}' at {datetime}"

    def search_files(self, query: str, file_type: str, date_range: str) -> str:
        results = [f for f in self.state["files"] if (query.lower() in f["name"].lower() or file_type == f["type"])]
        return f"Found {len(results)} files matching query '{query}'"

    def create_task(self, title: str, assignee: str, due_date: str, priority: str) -> str:
        task = {"title": title, "assignee": assignee, "due_date": due_date, "priority": priority}
        self.state["tasks"].append(task)
        return f"Task '{title}' assigned to {assignee}"

services = MockServices()

def execute_api_call(parsed_json: dict) -> str:
    try:
        fn = parsed_json.get("function")
        args = parsed_json.get("args", {})
        
        if fn == "schedule_meeting":
            return services.schedule_meeting(**args)
        elif fn == "send_email":
            return services.send_email(**args)
        elif fn == "set_reminder":
            return services.set_reminder(**args)
        elif fn == "search_files":
            return services.search_files(**args)
        elif fn == "create_task":
            return services.create_task(**args)
        else:
            return f"Error: Unknown function {fn}"
    except Exception as e:
        return f"Execution Error: {str(e)}"
