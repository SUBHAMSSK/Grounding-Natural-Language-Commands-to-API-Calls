import json
import numpy as np
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import os

class FewShotSemanticParser:
    def __init__(self, data_path="data/synthetic_pairs.json", model_name="gemini-2.0-flash"):
        with open(data_path, 'r') as f:
            self.examples = json.load(f)
            
        print("Loading sentence transformer...")
        self.retriever_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        self.commands = [ex["command"] for ex in self.examples]
        print("Encoding examples for retrieval...")
        self.embeddings = self.retriever_model.encode(self.commands)
        
        # Make sure to set GEMINI_API_KEY in your env
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        self.generation_model = genai.GenerativeModel(model_name)
        
    def retrieve_examples(self, query, top_k=10):
        query_embedding = self.retriever_model.encode([query])[0]
        
        # Calculate cosine similarities
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [self.examples[idx] for idx in top_indices]
        
    def parse(self, command, num_shots=5):
        similar_examples = self.retrieve_examples(command, top_k=num_shots)
        
        prompt = "You are a semantic parser that maps natural language to JSON API calls.\n\n"
        for ex in similar_examples:
            prompt += f"Command: {ex['command']}\n"
            prompt += f"API Call: {json.dumps(ex['target'])}\n\n"
            
        prompt += f"Command: {command}\nAPI Call: "
        
        try:
            response = self.generation_model.generate_content(prompt)
            # Try to extract JSON from response
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].strip()
                
            return json.loads(text)
        except Exception as e:
            return {"error": str(e), "raw_response": response.text if 'response' in locals() else None}

if __name__ == "__main__":
    parser = FewShotSemanticParser()
    test_cmd = "Schedule a Sync with David next Wednesday at 10:00 AM"
    print(f"Testing command: {test_cmd}")
    res = parser.parse(test_cmd, num_shots=5)
    print("Parsed Output:")
    print(json.dumps(res, indent=2))
