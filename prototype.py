import json
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from mock_apis import execute_calls

def main():
    print("Loading model...")
    try:
        tokenizer = T5Tokenizer.from_pretrained("./model/final")
        model = T5ForConditionalGeneration.from_pretrained("./model/final")
    except:
        print("Fine-tuned model not found in ./model/final. Falling back to t5-small (will perform poorly without training).")
        tokenizer = T5Tokenizer.from_pretrained("t5-small")
        model = T5ForConditionalGeneration.from_pretrained("t5-small")
        
    model.eval()
    
    print("\n--- NL to API Interactive Prototype ---")
    print("Available devices: AC, lights, heater, TV")
    print("Available rooms: living room, bedroom, kitchen, office")
    print("Supported APIs: turn on/off, set temperature, schedule meeting")
    print("Try a sequence like: 'turn on the AC', then 'turn it off' to test memory.")
    print("Try 'set the temperature' to test ambiguity handling.")
    print("Type 'exit' to quit.\n")
    
    context_history = []
    
    while True:
        command = input("User >> ")
        if command.lower() == 'exit':
            break
            
        context_str = " | ".join(context_history[-3:]) # keep last 3 turns
        prompt = f"Context: {context_str} | Command: {command}"
        
        inputs = tokenizer(prompt, return_tensors="pt", max_length=256, truncation=True)
        outputs = model.generate(inputs.input_ids, max_length=128)
        pred = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        print(f"[Model Raw Output]: {pred}")
        
        try:
            # T5 often drops the `{` and `}` brackets. Try to insert them if missing.
            if pred.startswith("[") and not pred.startswith("[{"):
                cleaned = pred.replace('"', '').replace('[', '').replace(']', '').strip()
                # Split roughly logic
                pairs = cleaned.split("api: ")
                calls = []
                for p in pairs:
                    if not p: continue
                    p = "api: " + p
                    call_dict = {}
                    kv_pairs = p.split(", ")
                    for kv in kv_pairs:
                        if ": " in kv:
                            k, v = kv.split(": ", 1)
                            call_dict[k.strip()] = v.strip()
                    if call_dict:
                        calls.append(call_dict)
            else:
                calls = json.loads(pred)

            if isinstance(calls, list):
                execute_calls(calls)
                context_history.append(f"[User] {command} [System] {pred}")
            else:
                print("Model returned valid mapping, but not a list as expected.")
        except Exception as e:
            print(f"[Error] Could not parse model output: {e}")

if __name__ == "__main__":
    main()
