#!/usr/bin/env python3
"""
Local Chatbot using trained model
Alternative to Groq API for offline usage
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
from data_fetcher import RedditDataFetcher

class LocalChatbot:
    def __init__(self, model_path="./trained_model"):
        """Initialize with trained local model"""
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.context_data = ""
        
        if os.path.exists(model_path):
            print(f"Loading local model from {model_path}...")
            self.load_model()
        else:
            print(f"❌ No trained model found at {model_path}")
            print("Run 'python train_local_model.py' first to train a model.")
            exit(1)
    
    def load_model(self):
        """Load the trained model and tokenizer"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_path)
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            print("✅ Local model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            exit(1)
    
    def load_reddit_context(self):
        """Load recent Reddit data as context"""
        try:
            fetcher = RedditDataFetcher()
            posts = fetcher.fetch_data(limit=5)  # Get recent posts
            
            if isinstance(posts, list) and len(posts) > 0:
                if hasattr(posts[0], 'title'):  # Reddit posts
                    context = "Recent discussions:\n"
                    for post in posts[:3]:
                        context += f"- {post.title}\n"
                else:  # Sample data
                    context = "Available information:\n" + "\n".join(posts[:3])
                
                self.context_data = context
                print("✅ Loaded recent Reddit context")
            else:
                self.context_data = "No recent data available."
                
        except Exception as e:
            print(f"⚠️ Could not load Reddit context: {e}")
            self.context_data = "Context unavailable."
    
    def get_response(self, user_input):
        """Generate response using local model"""
        try:
            # Prepare input with context
            full_input = f"Context: {self.context_data}\n\nHuman: {user_input}\nAssistant:"
            
            # Tokenize
            inputs = self.tokenizer.encode(full_input, return_tensors="pt")
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 150,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response.replace(full_input, "").strip()
            
            # Clean up response
            if "<|endoftext|>" in response:
                response = response.split("<|endoftext|>")[0]
            
            return response.strip()
            
        except Exception as e:
            return f"Error generating response: {e}"
    
    def start_chat(self):
        """Start interactive chat session"""
        print("\n" + "="*50)
        print("🤖 Elden Ring Local Chatbot")
        print("Type 'quit' to exit, 'refresh' to reload Reddit data")
        print("="*50)
        
        # Load initial context
        self.load_reddit_context()
        
        while True:
            try:
                user_input = input("\n💭 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'refresh':
                    print("🔄 Refreshing Reddit data...")
                    self.load_reddit_context()
                    continue
                
                if not user_input:
                    continue
                
                print("🤖 Bot: ", end="", flush=True)
                response = self.get_response(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function"""
    chatbot = LocalChatbot()
    chatbot.start_chat()

if __name__ == "__main__":
    main()