import json
import torch
from datasets import Dataset
from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments

def load_data(path):
    with open(path, 'r') as f:
        data = [json.loads(line) for line in f]
    return data

def preprocess_function(examples, tokenizer, max_length=128):
    inputs = [f"Context: {ctx} | Command: {cmd}" for ctx, cmd in zip(examples["context"], examples["command"])]
    targets = examples["target"]
    
    model_inputs = tokenizer(inputs, max_length=max_length, truncation=True, padding="max_length")
    labels = tokenizer(text_target=targets, max_length=max_length, truncation=True, padding="max_length")
        
    labels["input_ids"] = [
        [(l if l != tokenizer.pad_token_id else -100) for l in label] for label in labels["input_ids"]
    ]
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

def fine_tune():
    data = load_data("dataset.jsonl")
    dataset = Dataset.from_list(data)
    dataset = dataset.train_test_split(test_size=0.1)
    
    tokenizer = T5Tokenizer.from_pretrained("t5-small")
    model = T5ForConditionalGeneration.from_pretrained("t5-small")
    
    tokenized_datasets = dataset.map(lambda x: preprocess_function(x, tokenizer), batched=True)
    
    training_args = TrainingArguments(
        output_dir="./model",
        eval_strategy="epoch",
        learning_rate=2e-4,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=1,
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
    
    model.save_pretrained("./model/final")
    tokenizer.save_pretrained("./model/final")

if __name__ == "__main__":
    fine_tune()
