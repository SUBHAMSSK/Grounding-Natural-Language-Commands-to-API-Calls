import gradio as gr
import json
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apis.mock_apis import execute_api_call
from approaches.fewshot_prompt import FewShotSemanticParser

# Initialize few-shot parser (requires GEMINI_API_KEY)
try:
    fewshot_parser = FewShotSemanticParser()
except Exception as e:
    print(f"Warning: Could not initialize FewShotSemanticParser. Make sure GEMINI_API_KEY is set. Error: {e}")
    fewshot_parser = None

def process_command(command, approach):
    if not command.strip():
        return "Please enter a command.", ""
        
    try:
        if approach == "Few-Shot (Gemini)":
            if not fewshot_parser:
                return "Error: FewShot parser not initialized. Check API key.", ""
            
            # Use few-shot parser
            parsed_json = fewshot_parser.parse(command, num_shots=5)
            
            # Execute
            execution_result = execute_api_call(parsed_json)
            
            return json.dumps(parsed_json, indent=2), execution_result
            
        elif approach == "Fine-Tuned (Local T5 Mock)":
            # Here we would normally load the fine-tuned T5 model and run inference
            # For demonstration, we'll return a mock structured response
            # In a real app, integrate the HF pipeline from approaches/finetune_t5.py
            
            # Simple heuristic for mock
            if "meeting" in command.lower() or "sync" in command.lower():
                parsed_json = {
                    "function": "schedule_meeting",
                    "args": {"title": "Meeting", "attendees": ["Team"], "date": "today", "time": "12:00 PM", "duration_min": 30}
                }
            elif "email" in command.lower():
                parsed_json = {
                    "function": "send_email",
                    "args": {"to": "team@example.com", "subject": "Update", "body": "Hello team", "cc": []}
                }
            elif "remind" in command.lower():
                parsed_json = {
                    "function": "set_reminder",
                    "args": {"message": "task", "datetime": "tomorrow", "repeat": "none"}
                }
            elif "task" in command.lower():
                parsed_json = {
                    "function": "create_task",
                    "args": {"title": "New Task", "assignee": "User", "due_date": "next week", "priority": "medium"}
                }
            else:
                parsed_json = {
                    "function": "search_files",
                    "args": {"query": "document", "file_type": "any", "date_range": "any"}
                }
                
            execution_result = execute_api_call(parsed_json)
            
            return json.dumps(parsed_json, indent=2), execution_result
            
    except Exception as e:
        return f"Error: {str(e)}", ""

# Create Gradio UI
with gr.Blocks(title="NL to API Grounding System") as demo:
    gr.Markdown("# 🤖 NL → API Call Grounding System")
    gr.Markdown("Translate natural language commands into executable API calls.")
    
    with gr.Row():
        with gr.Column():
            command_input = gr.Textbox(
                label="Enter Command", 
                placeholder="e.g. Schedule a Sync with David next Wednesday at 10:00 AM",
                lines=3
            )
            approach_dropdown = gr.Dropdown(
                choices=["Few-Shot (Gemini)", "Fine-Tuned (Local T5 Mock)"],
                value="Few-Shot (Gemini)",
                label="Approach"
            )
            submit_btn = gr.Button("Parse & Execute", variant="primary")
            
            gr.Examples(
                examples=[
                    "Schedule a Sync with David next Wednesday at 10:00 AM",
                    "Send an email to Alice about the project report",
                    "Remind me to call mom tomorrow",
                    "Find pdf files related to budget",
                    "Create a high priority task for Frank to fix bug"
                ],
                inputs=command_input
            )
            
        with gr.Column():
            json_output = gr.Code(label="Parsed JSON (Meaning Representation)", language="json")
            exec_output = gr.Textbox(label="Execution Result (Observable Effect)", lines=2)

    submit_btn.click(
        fn=process_command,
        inputs=[command_input, approach_dropdown],
        outputs=[json_output, exec_output]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", share=False)
