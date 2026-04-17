import json

class MockSmartHome:
    def __init__(self):
        self.state = {
            "AC": {"status": "off", "room": "living room"},
            "lights": {"status": "off", "room": "living room", "brightness": 0},
            "temperature": 70
        }

    def turn_on(self, device, room=None):
        if device in self.state:
            self.state[device]["status"] = "on"
            if room:
                self.state[device]["room"] = room
            print(f"[API EXEC] Turned on {device}" + (f" in {room}" if room else ""))
            return True
        print(f"[API ERROR] Unknown device {device}")
        return False

    def turn_off(self, device, room=None):
        if device in self.state:
            self.state[device]["status"] = "off"
            print(f"[API EXEC] Turned off {device}")
            return True
        print(f"[API ERROR] Unknown device {device}")
        return False

    def set_temperature(self, room=None, temperature=70):
        self.state["temperature"] = temperature
        print(f"[API EXEC] Set temperature to {temperature}" + (f" in {room}" if room else ""))
        return True

    def schedule_meeting(self, person, time):
        print(f"[API EXEC] Scheduled meeting with {person} at {time}")
        return True

    def ask_user(self, question, missing_parameter=None):
        print(f"[SYSTEM ASKS] {question}")
        return True

home = MockSmartHome()

def execute_api_call(call):
    api = call.get("api")
    if api == "turn_on":
        home.turn_on(call.get("device"), call.get("room"))
    elif api == "turn_off":
        home.turn_off(call.get("device"), call.get("room"))
    elif api == "set_temperature":
        home.set_temperature(call.get("room"), call.get("temperature"))
    elif api == "schedule_meeting":
        home.schedule_meeting(call.get("person"), call.get("time"))
    elif api == "ask_user":
        home.ask_user(call.get("question", "Could you provide more details?"), call.get("missing_parameter"))
    else:
        print(f"[API ERROR] Unknown API: {api}")

def execute_calls(calls):
    for call in calls:
        execute_api_call(call)
