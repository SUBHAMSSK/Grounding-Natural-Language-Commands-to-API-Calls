import json
import random

def generate_synthetic_data(num_samples=300):
    dataset = []
    
    # schedule_meeting
    names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank"]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "tomorrow", "next week"]
    times = ["10:00 AM", "1:00 PM", "3:30 PM", "noon", "9:00 AM"]
    titles = ["Project Sync", "1:1 Review", "Team Standup", "Brainstorming", "Client Call"]
    
    # send_email
    subjects = ["Update", "Report", "Meeting Notes", "Invoice", "Welcome"]
    
    for _ in range(num_samples):
        api_choice = random.choice(["schedule_meeting", "send_email", "set_reminder", "search_files", "create_task"])
        
        if api_choice == "schedule_meeting":
            person = random.choice(names)
            day = random.choice(days)
            time = random.choice(times)
            title = random.choice(titles)
            cmd = f"Schedule a {title} with {person} on {day} at {time}"
            target = {
                "function": "schedule_meeting",
                "args": {
                    "title": title,
                    "attendees": [person],
                    "date": day,
                    "time": time,
                    "duration_min": 30
                }
            }
        elif api_choice == "send_email":
            person = random.choice(names)
            subject = random.choice(subjects)
            cmd = f"Send an email to {person} about {subject}"
            target = {
                "function": "send_email",
                "args": {
                    "to": f"{person.lower()}@example.com",
                    "subject": subject,
                    "body": f"Hi {person}, here is the information about {subject}.",
                    "cc": []
                }
            }
        elif api_choice == "set_reminder":
            msg = random.choice(["buy milk", "call mom", "submit report", "pay bills"])
            day = random.choice(days)
            cmd = f"Remind me to {msg} {day}"
            target = {
                "function": "set_reminder",
                "args": {
                    "message": msg,
                    "datetime": day,
                    "repeat": "none"
                }
            }
        elif api_choice == "search_files":
            query = random.choice(["budget", "report", "presentation", "invoice"])
            ftype = random.choice(["pdf", "xlsx", "docx"])
            cmd = f"Find {ftype} files related to {query}"
            target = {
                "function": "search_files",
                "args": {
                    "query": query,
                    "file_type": ftype,
                    "date_range": "any"
                }
            }
        else: # create_task
            title = random.choice(["Fix bug", "Write docs", "Review PR", "Deploy app"])
            assignee = random.choice(names)
            priority = random.choice(["high", "medium", "low"])
            cmd = f"Create a {priority} priority task for {assignee} to {title.lower()}"
            target = {
                "function": "create_task",
                "args": {
                    "title": title,
                    "assignee": assignee,
                    "due_date": "next week",
                    "priority": priority
                }
            }
            
        dataset.append({"command": cmd, "target": target})
        
    return dataset

if __name__ == "__main__":
    import os
    dataset = generate_synthetic_data(300)
    
    output_path = os.path.join(os.path.dirname(__file__), "synthetic_pairs.json")
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(dataset, f, indent=2)
    print(f"Generated 300 synthetic pairs in {output_path}")
