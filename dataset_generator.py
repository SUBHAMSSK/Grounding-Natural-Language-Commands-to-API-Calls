import json
import random

def generate_dataset(num_samples=2000):
    dataset = []
    
    devices = ["AC", "lights", "heater", "TV"]
    rooms = ["living room", "bedroom", "kitchen", "office"]
    people = ["Alice", "Bob", "Charlie", "David"]
    times = ["3pm", "tomorrow morning", "next Wednesday", "at noon"]
    
    for _ in range(num_samples):
        scenario = random.choice(["single", "multi", "context", "ambiguous"])
        
        if scenario == "single":
            device = random.choice(devices)
            room = random.choice(rooms)
            action = random.choice(["turn on", "turn off"])
            api_name = "turn_on" if action == "turn on" else "turn_off"
            
            # 50% chance to include room
            if random.random() > 0.5:
                command = f"{action} the {device} in the {room}"
                output = [{"api": api_name, "device": device, "room": room}]
            else:
                command = f"{action} the {device}"
                output = [{"api": api_name, "device": device}]
                
            dataset.append({
                "context": "",
                "command": command,
                "target": json.dumps(output)
            })
            
        elif scenario == "multi":
            device1 = random.choice(devices)
            device2 = random.choice(devices)
            while device1 == device2:
                device2 = random.choice(devices)
                
            action1 = random.choice(["turn on", "turn off"])
            action2 = random.choice(["turn on", "turn off"])
            
            api1 = "turn_on" if action1 == "turn on" else "turn_off"
            api2 = "turn_on" if action2 == "turn on" else "turn_off"
            
            command = f"{action1} the {device1} and {action2} the {device2}"
            output = [
                {"api": api1, "device": device1},
                {"api": api2, "device": device2}
            ]
            dataset.append({
                "context": "",
                "command": command,
                "target": json.dumps(output)
            })
            
        elif scenario == "context":
            device = random.choice(devices)
            
            # Setup context
            context_cmd = f"turn on the {device}"
            context_out = [{"api": "turn_on", "device": device}]
            context_str = f"[User] {context_cmd} [System] {json.dumps(context_out)}"
            
            # Follow up targeting same device
            command = "turn it off"
            output = [{"api": "turn_off", "device": device}]
            
            dataset.append({
                "context": context_str,
                "command": command,
                "target": json.dumps(output)
            })
            
        elif scenario == "ambiguous":
            # Just say "set temperature" -> needs room
            command = random.choice(["set the temperature", "change the temp"])
            output = [{"api": "ask_user", "question": "Which room?", "missing_parameter": "room"}]
            
            dataset.append({
                "context": "",
                "command": command,
                "target": json.dumps(output)
            })
            
    return dataset

if __name__ == "__main__":
    dataset = generate_dataset(2500)
    with open("dataset.jsonl", "w") as f:
        for item in dataset:
            f.write(json.dumps(item) + "\n")
    print(f"Generated dataset with {len(dataset)} items in dataset.jsonl")
