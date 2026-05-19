from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import outlines

print("Testing constrained generation with outlines...")

class APICall(BaseModel):
    function: str
    arguments: dict

model_name = "gpt2"

tokenizer = AutoTokenizer.from_pretrained(model_name)
hf_model = AutoModelForCausalLM.from_pretrained(model_name)

# 1. Load the model via Outlines' Transformers wrapper
model = outlines.models.Transformers(hf_model, tokenizer)

# 2. In Outlines 1.3.0+, generation is done via outlines.Generator
# passing the Pydantic schema as output_type
generator = outlines.Generator(model, output_type=APICall)

prompt = """
Convert the following command into an API call JSON.

Command: Schedule a meeting with Alice tomorrow at 3 PM
"""

# Generate the result
result = generator(prompt)

print(result)
