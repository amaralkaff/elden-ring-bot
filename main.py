#!/usr/bin/env python3
import os
import sys
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import local modules
from data_fetcher import RedditDataFetcher
from groq_chatbot import GroqChatbot

def create_data_directory():
    """Create data directory if it doesn't exist"""
    os.makedirs("data", exist_ok=True)

def fetch_data(args):
    """Fetch data from Reddit"""
    print("=== Fetching Data from Reddit ===")
    
    # Create data fetcher
    fetcher = RedditDataFetcher()
    
    # Fetch and clean data
    success = fetcher.fetch_and_clean(limit=args.limit)
    
    if success:
        print("Data fetching and cleaning completed successfully!")
    else:
        print("Failed to fetch and clean data.")

def run_chatbot(args):
    """Run the Groq chatbot"""
    print("=== Elden Ring Cheats Bot ===")
    
    # Create Groq chatbot
    chatbot = GroqChatbot(local_only=args.local)
    
    # Set custom model if specified
    if args.model:
        chatbot.model = args.model
        print(f"Using custom model: {args.model}")
    
    # Start chat session
    chatbot.start_chat()

def main():
    """Main function"""
    # Create argument parser
    parser = argparse.ArgumentParser(description="Elden Ring Cheats Bot")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Fetch data command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch data from Reddit")
    fetch_parser.add_argument("--limit", type=int, default=20, help="Number of posts to fetch")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start the chatbot")
    chat_parser.add_argument("--local", action="store_true", help="Run in local-only mode (no API calls)")
    chat_parser.add_argument("--model", type=str, help="Specify a custom Groq model")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create data directory
    create_data_directory()
    
    # Run command
    if args.command == "fetch":
        fetch_data(args)
    elif args.command == "chat":
        run_chatbot(args)
    else:
        # No command specified, show menu
        while True:
            print("\n" + "="*50)
            print("🎮 ELDEN RING CHAT BOT")
            print("="*50)
            print("1. Fetch data from Reddit")
            print("2. Start chatbot with Groq API (Recommended)")
            print("3. Start chatbot in local-only mode")
            print("4. Train local model from Reddit data")
            print("5. Start local trained chatbot")
            print("6. Start web interface")
            print("7. Exit")
            print("="*50)
            
            choice = input("\nEnter your choice (1-7): ")
            
            if choice == "1":
                # Create args object with default values
                class Args:
                    limit = 20
                fetch_data(Args())
            elif choice == "2":
                # Create args object for Groq API
                class Args:
                    local = False
                    model = None
                run_chatbot(Args())
            elif choice == "3":
                # Create args object for local mode
                class Args:
                    local = True
                    model = None
                run_chatbot(Args())
            elif choice == "4":
                print("\n=== Training Local Model ===")
                try:
                    from train_local_model import main as train_main
                    train_main()
                except ImportError:
                    print("❌ Training dependencies not available.")
                    print("Make sure transformers, torch, and datasets are installed.")
                except Exception as e:
                    print(f"❌ Training error: {e}")
                input("\nPress Enter to continue...")
            elif choice == "5":
                print("\n=== Starting Local Trained Chatbot ===")
                try:
                    from local_chatbot import main as local_main
                    local_main()
                except ImportError:
                    print("❌ Local model dependencies not available.")
                except Exception as e:
                    print(f"❌ Error: {e}")
            elif choice == "6":
                print("\n=== Starting Web Interface ===")
                print("🌐 Starting web server at http://localhost:8000")
                try:
                    from web import app
                    port = int(os.environ.get('PORT', 8000))
                    app.run(debug=True, host='0.0.0.0', port=port)
                except Exception as e:
                    print(f"❌ Web server error: {e}")
            elif choice == "7":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter a number between 1-7.")

if __name__ == "__main__":
    main()
