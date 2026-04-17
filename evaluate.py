import json
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from datasets import Dataset

def load_data(path):
    with open(path, 'r') as f:
        data = [json.loads(line) for line in f]
    return data

def fix_pred(pred):
    # Fix missing brackets for T5
    if pred.startswith("[") and not pred.startswith("[{"):
        cleaned = pred.replace('"', '').replace('[', '').replace(']', '').strip()
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
        return calls
    else:
        return json.loads(pred)

def exact_match(pred, target):
    try:
        pred_json = fix_pred(pred)
        target_json = json.loads(target)
        return pred_json == target_json
    except:
        return False

def evaluate():
    data = load_data("dataset.jsonl")
    # Take latest 100 for evaluation
    test_data = data[-100:]
    
    tokenizer = T5Tokenizer.from_pretrained("t5-small")
    
    # 1. Baseline Evaluation (Zero/Few-shot without fine-tuning)
    print("--- Evaluating Baseline (Untuned T5-small) ---")
    baseline_model = T5ForConditionalGeneration.from_pretrained("t5-small")
    baseline_model.eval()
    
    baseline_correct = 0
    # Create a few-shot prompt prefix
    few_shot_prompt = (
        "Translate command to API JSON list. Examples: "
        "Command: turn on the AC -> [{\"api\": \"turn_on\", \"device\": \"AC\"}] | "
        "Command: set the temperature -> [{\"api\": \"ask_user\", \"question\": \"Which room?\", \"missing_parameter\": \"room\"}] | "
    )
    
    for item in test_data[:20]: # Test fewer for baseline to save time
        prompt = few_shot_prompt + f"Context: {item['context']} | Command: {item['command']}"
        inputs = tokenizer(prompt, return_tensors="pt", max_length=256, truncation=True)
        outputs = baseline_model.generate(inputs.input_ids, max_length=128)
        pred = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        if exact_match(pred, item['target']):
            baseline_correct += 1
            
    print(f"Baseline Accuracy (Few-shot, 20 samples): {baseline_correct / 20 * 100:.2f}%\n")
    
    # 2. Fine-tuned model Evaluation
    print("--- Evaluating Fine-Tuned Model ---")
    try:
        ft_model = T5ForConditionalGeneration.from_pretrained("./model/final")
        ft_model.eval()
        
        ft_correct = 0
        for item in test_data:
            prompt = f"Context: {item['context']} | Command: {item['command']}"
            inputs = tokenizer(prompt, return_tensors="pt", max_length=128, truncation=True)
            outputs = ft_model.generate(inputs.input_ids, max_length=128)
            pred = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            if exact_match(pred, item['target']):
                ft_correct += 1
            else:
                if ft_correct == 0:
                    print(f"Target: {item['target']}")
                    print(f"Pred:   {pred}")
                
        print(f"Fine-tuned Accuracy (100 samples): {ft_correct / 100 * 100:.2f}%\n")
    except Exception as e:
        print(f"Could not load fine-tuned model (maybe it hasn't been trained yet): {e}")

if __name__ == "__main__":
    evaluate()
