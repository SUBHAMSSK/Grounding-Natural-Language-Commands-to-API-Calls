# 🤖 NL → API Call Grounding System

This project implements a system that maps Natural Language (NL) commands to structured, executable API calls. It is heavily inspired by the methodologies evaluated in the paper *"Few-Shot Semantic Parsing with Language Models Trained on Code"* by Shin & Van Durme.

The system compares two parallel approaches to semantic parsing:
1. **Few-Shot Prompting:** Utilizing a Large Language Model (Gemini) with dynamic in-context retrieval to predict API structures on the fly.
2. **Fine-Tuning:** Training a local sequence-to-sequence model (`google/flan-t5-small`) to map inputs to API JSON schemas.

We also demonstrate **Constrained Decoding** (using `outlines`) to mathematically guarantee that local models output syntactically valid JSON matching our Pydantic schemas.

---

## 📂 Project Structure

```text

├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
├── data/
│   ├── dataset.py          # Synthetic dataset generator
│   └── synthetic_pairs.json# Generated NL -> API pairs
├── apis/
│   └── mock_apis.py        # 5 Mock Services & execution logic
├── approaches/
│   ├── fewshot_prompt.py   # RAG-based few-shot prompt system (Gemini)
│   └── finetune_t5.py      # HuggingFace Trainer for FLAN-T5
├── constrained/
│   └── json_constrained.py # Constrained decoding using outlines (GPT-2 fallback demo)
├── eval/
│   └── metrics.py          # Evaluation metrics (Exact Match, Slot Accuracy, etc.)
└── demo.py                 # Interactive Gradio web interface
```

---

## 🛠 Setup & Installation

1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Export your Google Gemini API key (needed for the few-shot prompting and demo):
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

---

## 🚀 Usage

### 1. Generating Data
Generate the base JSON pairing file representing complex NL commands (Single, Multi, and Ambiguous steps).
```bash
python data/dataset.py
```

### 2. Testing the Mock APIs & Metrics
We've mocked out 5 distinct services (calendar, outbox, reminders, files, tasks). Test the structural accuracy and execution effects:
```bash
python eval/metrics.py
```

### 3. Evaluating Constrained Decoding
Watch the `outlines` library enforce structured JSON output on a local HuggingFace model.
```bash
python constrained/json_constrained.py
```

### 4. Running the Few-Shot Pipeline
Test the Semantic Parser leveraging dynamic vector retrieval (`sentence-transformers`) and `gemini-2.0-flash`.
```bash
python approaches/fewshot_prompt.py
```

### 5. Training the Fine-Tuned Local Model
If you want to train your own deterministic parser without relying on an external API, trigger the FLAN-T5 fine-tuning process:
```bash
python approaches/finetune_t5.py
```

### 6. Launch the Gradio App
Run the interactive UI to visually query the NL -> API Grounding System:
```bash
python demo.py
```

---

## 📊 Evaluation Metrics

The system measures the efficacy of the generated parsed outputs against four distinct metrics:
- **Exact Match:** Strict string-for-string JSON equivalency.
- **Function Match:** Ensure the LLM picked the correct remote tool.
- **Slot Accuracy:** The percentage of correctly parsed arguments inside the schema.
- **Execution Match:** Validates the semantic equality by simulating the side-effect output in our Mock Application layer.
