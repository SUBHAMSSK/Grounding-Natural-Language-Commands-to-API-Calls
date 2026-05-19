import json
import torch
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Trainer, TrainingArguments

def load_data(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def preprocess_function(examples, tokenizer, max_length=128):
    inputs = [f"Parse this command to an API call: {cmd}" for cmd in examples["command"]]
    # The targets should be json strings
    targets = [json.dumps(tgt) for tgt in examples["target"]]
    
    model_inputs = tokenizer(inputs, max_length=max_length, truncation=True, padding="max_length")
    labels = tokenizer(text_target=targets, max_length=max_length, truncation=True, padding="max_length")
        
    labels["input_ids"] = [
        [(l if l != tokenizer.pad_token_id else -100) for l in label] for label in labels["input_ids"]
    ]
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

def fine_tune(model_name="google/flan-t5-small", output_dir="./model/flan_t5_finetuned"):
    print(f"Fine-tuning {model_name}...")
    data = load_data("data/synthetic_pairs.json")
    dataset = Dataset.from_list(data)
    dataset = dataset.train_test_split(test_size=0.1)
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    
    tokenized_datasets = dataset.map(lambda x: preprocess_function(x, tokenizer), batched=True)
    
    training_args = TrainingArguments(
        output_dir=output_dir,
        eval_strategy="epoch",
        learning_rate=2e-4,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
        save_total_limit=1,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["test"],
    )
    
    trainer.train()
    
    model.save_pretrained(f"{output_dir}/final")
    tokenizer.save_pretrained(f"{output_dir}/final")
    print(f"Model saved to {output_dir}/final")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="google/flan-t5-small", help="Model to finetune (e.g., t5-small, google/flan-t5-small)")
    args = parser.add_argument("--out", type=str, default="./model/flan_t5_finetuned", help="Output directory")
    args = parser.parse_args()
    fine_tune(model_name=args.model, output_dir=args.out)
