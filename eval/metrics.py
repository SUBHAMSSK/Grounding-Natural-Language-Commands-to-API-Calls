import json
import sys
import os

# Add parent dir to path to import mock_apis
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from apis.mock_apis import execute_api_call

def exact_match(pred: dict, target: dict) -> bool:
    """Check if the predicted JSON matches target JSON perfectly."""
    return pred == target

def function_match(pred: dict, target: dict) -> bool:
    """Check if the predicted function name matches target function name."""
    return pred.get("function") == target.get("function")

def slot_accuracy(pred: dict, target: dict) -> float:
    """Calculate the percentage of correct arguments/slots."""
    pred_args = pred.get("args", {})
    target_args = target.get("args", {})
    
    if not target_args:
        return 1.0 if not pred_args else 0.0
        
    correct_slots = 0
    total_slots = len(target_args)
    
    for k, v in target_args.items():
        if k in pred_args and pred_args[k] == v:
            correct_slots += 1
            
    return correct_slots / total_slots

def execution_match(pred: dict, target: dict) -> bool:
    """
    Check if the side effect of execution matches.
    Since we are mocking, we can check if both return the same string.
    In a real scenario, we would check the state dict of MockServices.
    """
    pred_result = execute_api_call(pred)
    target_result = execute_api_call(target)
    
    # Simple check: do they yield the same execution message?
    # If there's an error in pred, it will return an error string which won't match target.
    return pred_result == target_result and "Error" not in pred_result

def evaluate_predictions(predictions, targets):
    """
    Evaluate a list of predictions against a list of targets.
    predictions and targets are lists of dicts.
    """
    metrics = {
        "exact_match": 0.0,
        "function_match": 0.0,
        "slot_accuracy": 0.0,
        "execution_match": 0.0
    }
    
    n = len(targets)
    if n == 0:
        return metrics
        
    for p, t in zip(predictions, targets):
        if exact_match(p, t):
            metrics["exact_match"] += 1
        if function_match(p, t):
            metrics["function_match"] += 1
        metrics["slot_accuracy"] += slot_accuracy(p, t)
        if execution_match(p, t):
            metrics["execution_match"] += 1
            
    # Calculate percentages
    for k in metrics:
        metrics[k] = (metrics[k] / n) * 100
        
    return metrics

if __name__ == "__main__":
    t = {
        "function": "schedule_meeting",
        "args": {
            "title": "Sync",
            "attendees": ["David"],
            "date": "tomorrow",
            "time": "10:00 AM",
            "duration_min": 30
        }
    }
    
    # perfect match
    p1 = dict(t)
    
    # wrong time (slot error)
    p2 = {
        "function": "schedule_meeting",
        "args": {
            "title": "Sync",
            "attendees": ["David"],
            "date": "tomorrow",
            "time": "11:00 AM",
            "duration_min": 30
        }
    }
    
    # wrong function
    p3 = {
        "function": "send_email",
        "args": {"to": "david@example.com"}
    }
    
    print("Evaluating p1 (Perfect):", evaluate_predictions([p1], [t]))
    print("Evaluating p2 (Wrong Slot):", evaluate_predictions([p2], [t]))
    print("Evaluating p3 (Wrong Func):", evaluate_predictions([p3], [t]))
