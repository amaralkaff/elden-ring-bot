#!/usr/bin/env python3
"""
Local Model Training for Elden Ring Bot
For users who want to train their own models using Reddit data
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from datasets import Dataset
import json
from data_fetcher import RedditDataFetcher

class LocalModelTrainer:
    def __init__(self, model_name="microsoft/DialoGPT-medium"):
        """Initialize trainer with a base model"""
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Add padding token if it doesn't exist
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def prepare_reddit_data(self, limit_posts=100):
        """Fetch and prepare Reddit data for training"""
        print("Fetching Reddit data for training...")
        
        fetcher = RedditDataFetcher()
        # Fetch from multiple subreddits
        subreddits = ['Eldenring', 'EldenRingMods', 'cheatengine', 'GuidedHacking']
        
        all_conversations = []
        
        for subreddit in subreddits:
            fetcher.subreddit_name = subreddit
            posts = fetcher.fetch_data(limit=limit_posts//len(subreddits))
            
            if isinstance(posts, list) and len(posts) > 0:
                for post in posts:
                    if hasattr(post, 'title') and hasattr(post, 'selftext'):
                        # Create conversation format
                        conversation = {
                            'input': f"Tell me about: {post.title}",
                            'output': post.selftext if post.selftext else post.title
                        }
                        all_conversations.append(conversation)
        
        print(f"Prepared {len(all_conversations)} conversations for training")
        return all_conversations
    
    def create_dataset(self, conversations):
        """Convert conversations to tokenized dataset"""
        def tokenize_function(examples):
            # Combine input and output for training
            full_texts = []
            for inp, out in zip(examples['input'], examples['output']):
                full_text = f"Human: {inp}\nAssistant: {out}<|endoftext|>"
                full_texts.append(full_text)
            
            # Tokenize
            tokenized = self.tokenizer(
                full_texts,
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors="pt"
            )
            
            # For causal LM, labels are the same as input_ids
            tokenized["labels"] = tokenized["input_ids"].clone()
            
            return tokenized
        
        # Create dataset
        dataset = Dataset.from_dict({
            'input': [conv['input'] for conv in conversations],
            'output': [conv['output'] for conv in conversations]
        })
        
        # Tokenize
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names
        )
        
        return tokenized_dataset
    
    def train_model(self, dataset, output_dir="./trained_model"):
        """Train the model on Reddit data"""
        print("Starting model training...")
        
        training_args = TrainingArguments(
            output_dir=output_dir,
            overwrite_output_dir=True,
            num_train_epochs=3,
            per_device_train_batch_size=2,
            gradient_accumulation_steps=2,
            warmup_steps=100,
            logging_steps=50,
            save_steps=500,
            eval_strategy="no",  # Fixed: changed from evaluation_strategy
            save_total_limit=2,
            prediction_loss_only=True,
            remove_unused_columns=False,
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
            tokenizer=self.tokenizer,
        )
        
        # Train
        trainer.train()
        
        # Save model
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        print(f"Model saved to {output_dir}")
        return output_dir
    
    def test_model(self, model_path, test_input="How do I beat Margit?"):
        """Test the trained model"""
        print(f"Testing model with: {test_input}")
        
        # Load trained model
        model = AutoModelForCausalLM.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Generate response
        input_text = f"Human: {test_input}\nAssistant:"
        inputs = tokenizer.encode(input_text, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=inputs.shape[1] + 100,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response.replace(input_text, "").strip()
        
        print(f"Model response: {response}")
        return response

def main():
    """Main training pipeline"""
    print("=== Local Model Training for Elden Ring Bot ===")
    
    # Check if user wants to proceed
    response = input("This will download models and train locally. Continue? (y/n): ")
    if response.lower() != 'y':
        print("Training cancelled.")
        return
    
    try:
        # Initialize trainer
        trainer = LocalModelTrainer()
        
        # Prepare data
        conversations = trainer.prepare_reddit_data(limit_posts=200)
        if not conversations:
            print("No data found! Make sure your Reddit API keys are set.")
            return
        
        # Create dataset
        dataset = trainer.create_dataset(conversations)
        
        # Train model
        model_path = trainer.train_model(dataset)
        
        # Test model
        trainer.test_model(model_path)
        
        print("\n✅ Training complete!")
        print(f"Your model is saved in: {model_path}")
        print("You can now use it in a local chatbot setup.")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        print("Make sure you have enough RAM and GPU (optional) for training.")

if __name__ == "__main__":
    main()