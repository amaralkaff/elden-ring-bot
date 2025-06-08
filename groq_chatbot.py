import os
import time
import random
import requests
import json
from dotenv import load_dotenv

# Load environment variables from @.env first, then .env if not found
if os.path.exists("@.env"):
    load_dotenv("@.env")
else:
    load_dotenv()

class GroqChatbot:
    def __init__(self, local_only=False):
        """Initialize the Groq chatbot"""
        # Local only mode - skip API calls entirely
        self.local_only = local_only
        
        # Get API key from environment or use the provided one
        self.api_key = os.getenv("GROQ_API_KEY")
        
        # API configuration
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"  # Default model
        
        # Print configuration info
        if not self.local_only:
            print(f"Configured Groq API with model: {self.model}")
        
        # Load context data if available
        self.context_data = self.load_context_data()
        
        # Rate limiting tracking
        self.rate_limited = False
        self.last_rate_limit_time = 0
    
    def reload_context_data(self):
        """Reload context data from file"""
        self.context_data = self.load_context_data()
        return self.context_data is not None
    
    def load_context_data(self, file_path="data/cleaned_data.txt"):
        """Load context data from cleaned file if available"""
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                # Try alternative paths
                alternative_paths = [
                    "data/sample_data.txt",
                    "cleaned_elden_ring_cheats_data.txt"
                ]
                
                for path in alternative_paths:
                    if os.path.exists(path):
                        print(f"Using alternative context data from {path}")
                        with open(path, "r", encoding="utf-8") as f:
                            return f.read()
                
                print(f"Context file not found. Checked paths:")
                print(f" - {file_path}")
                for path in alternative_paths:
                    print(f" - {path}")
                return None
        except Exception as e:
            print(f"Could not load context data: {e}")
            return None
    
    def get_response(self, user_input, use_context=True, max_retries=2):
        """Get response from Groq with Elden Ring cheat context"""
        # If in local-only mode, skip API and use fallback immediately
        if self.local_only:
            return self.fallback_response(user_input)
            
        # Check if we're rate limited
        if self.rate_limited:
            # If we were rate limited less than 30 seconds ago, use fallback
            if time.time() - self.last_rate_limit_time < 30:
                print("Still rate limited, using fallback response.")
                return self.fallback_response(user_input)
            else:
                # Try again after waiting
                self.rate_limited = False
        
        try:
            # Create context prompt for Elden Ring assistance
            system_message = """You are a helpful Elden Ring assistant providing information about:
            - Game guides and walkthroughs
            - Boss strategies and tips
            - Character builds and equipment
            - Lore and story explanations
            - Game mechanics and systems
            - General gameplay help and advice
            
            Provide helpful, accurate information based on the latest community discussions and data.
            Focus on legitimate gameplay assistance and avoid promoting cheating or exploits.
            Be friendly and informative in your responses."""
            
            # Prepare messages for the API
            messages = [
                {"role": "system", "content": system_message}
            ]
            
            # Add context data if available and requested
            if use_context and self.context_data:
                messages.append({
                    "role": "system", 
                    "content": f"Context from community data: {self.context_data}"
                })
            
            # Add user's question
            messages.append({
                "role": "user", 
                "content": user_input
            })
            
            # Prepare request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            # Retry logic for rate limits
            retries = 0
            while retries <= max_retries:
                try:
                    response = requests.post(
                        self.api_url,
                        headers=headers,
                        data=json.dumps(data),
                        timeout=30
                    )
                    
                    # Check if the request was successful
                    if response.status_code == 200:
                        # Parse the response
                        result = response.json()
                        return result['choices'][0]['message']['content']
                    elif response.status_code == 429:
                        # Rate limit hit
                        self.rate_limited = True
                        self.last_rate_limit_time = time.time()
                        
                        wait_time = (2 ** retries) * 5  # Exponential backoff: 5, 10, 20 seconds
                        print(f"Rate limited (429). Waiting {wait_time} seconds before retry...")
                        
                        if retries < max_retries:
                            time.sleep(wait_time)
                            retries += 1
                        else:
                            print("Max retries reached. Falling back to local responses.")
                            return self.fallback_response(user_input)
                    else:
                        # Other error
                        print(f"API error: {response.status_code} - {response.text}")
                        return self.fallback_response(user_input)
                        
                except requests.exceptions.RequestException as e:
                    print(f"Request error: {e}")
                    if retries < max_retries:
                        wait_time = (2 ** retries) * 5
                        print(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        retries += 1
                    else:
                        return self.fallback_response(user_input)
                        
        except Exception as e:
            print(f"Error with Groq API: {e}")
            return self.fallback_response(user_input)
    
    def fallback_response(self, user_input):
        """Provide detailed fallback responses when Groq API fails"""
        user_input = user_input.lower()
        
        # Primary responses for specific keywords
        responses = {
            "god mode": [
                "For god mode in Elden Ring, you can use Cheat Engine with specific scripts or trainers like FLiNG/WeMod. This makes your character invulnerable to all damage.",
                "God mode hacks work by freezing your health value in memory so it never decreases. Popular tools include Cheat Engine and WeMod."
            ],
            "infinite health": [
                "Infinite health can be achieved through memory editors like Cheat Engine by freezing health values. Look for 'HP' or 'CurrentHP' values in Cheat Engine.",
                "To get infinite health, use Cheat Engine to scan for your current health value, then for the new value after taking damage. Once found, right-click and select 'freeze value'."
            ],
            "unlimited stamina": [
                "Stamina hacks prevent stamina depletion during combat using memory editing tools. This allows endless running, attacking, and dodging.",
                "For unlimited stamina, use Cheat Engine to find your stamina value (often changes when running or attacking), then freeze it at maximum."
            ],
            "infinite runes": [
                "Rune hacks modify currency values through memory editors - be careful with online play as this can get you banned.",
                "To duplicate runes, use Cheat Engine to locate and modify your rune count. Some trainers also offer a 'multiply runes from kills' feature."
            ],
            "item duplication": [
                "Item duplication uses save file manipulation or specific glitches to multiply items. One method involves backing up your save, giving items to a friend, then restoring your save.",
                "For item duplication, the safest method is to back up your save file, drop items for a friend, then restore your save while keeping the original items."
            ],
            "teleport": [
                "Teleportation hacks use coordinate editors to instantly move around the map. These can be found in advanced Cheat Engine tables.",
                "Teleportation cheats work by modifying your character's X, Y, Z position values in memory. Be careful not to teleport inside terrain or you may get stuck."
            ],
            "one hit kill": [
                "One-hit kill mods modify damage multipliers through memory editing. This lets you defeat any enemy with a single attack.",
                "For one-hit kills, look for damage multiplier values in Cheat Engine or use trainers with a 'super damage' feature."
            ],
            "speed hack": [
                "Speed hacks increase movement and attack speed using Cheat Engine's speed hack feature or by modifying animation timers.",
                "To use speed hacks, enable Cheat Engine's speed hack feature (usually under 'Edit' menu) and adjust the multiplier. Values between 1.5-2x are usually safest."
            ]
        }
        
        # Secondary responses for general cheat types
        secondary_responses = {
            "cheat engine": "Cheat Engine is the most popular tool for Elden Ring cheats. Download it from the official website, then find a Cheat Engine table specifically for Elden Ring.",
            "trainer": "Trainers like WeMod or FLiNG offer user-friendly interfaces for cheats without needing to understand memory editing.",
            "memory editing": "Memory editing involves finding and changing game values in your computer's RAM while the game is running.",
            "save file": "Save file manipulation is safer than memory editing for offline play. Elden Ring saves are typically located in %appdata%/EldenRing/",
            "pvp": "Using cheats in PvP will likely get your account banned. It's recommended to use cheats in offline mode only.",
            "ban": "To avoid bans, play in offline mode when using cheats, and never use cheats that give obvious advantages in online play."
        }
        
        # Check for primary keyword matches
        for keyword, answer_list in responses.items():
            if keyword in user_input:
                return random.choice(answer_list)
        
        # Check for secondary keyword matches
        for keyword, answer in secondary_responses.items():
            if keyword in user_input:
                return answer
        
        # Check for general game terms
        if any(word in user_input for word in ["boss", "build", "guide", "help", "strategy"]):
            return "I can help with Elden Ring! Try asking about: boss strategies, character builds, game guides, lore, weapons, armor, or general gameplay tips."
        
        # Default response
        return "I'm your Elden Ring assistant! I can help with game guides, boss strategies, character builds, lore, and general gameplay questions. What would you like to know?"

    def start_chat(self):
        """Start an interactive chat session"""
        print("Elden Ring Cheats Bot - Type 'quit' to exit")
        
        # Show mode information
        if self.local_only:
            print("Running in LOCAL ONLY mode - using built-in responses without API calls")
        else:
            print(f"Running in ONLINE mode with Groq API (model: {self.model})")
            
        print("Ask me about Elden Ring cheats, hacks, and modifications!")
        
        if self.context_data:
            print("Loaded community data for enhanced responses.")
        else:
            print("No community data loaded. Responses will be based on built-in knowledge.")
        
        # Warn if we're using fallback mode due to previous rate limiting
        if self.rate_limited:
            print("NOTE: API is currently rate limited. Using local responses until limits reset.")
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye!")
                break
            
            response = self.get_response(user_input)
            print(f"Bot: {response}")

# For direct execution
if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Elden Ring Cheats Bot using Groq API")
    parser.add_argument("--local", action="store_true", help="Run in local-only mode (no API calls)")
    parser.add_argument("--model", type=str, help="Specify a different Groq model to use")
    args = parser.parse_args()
    
    # Create chatbot
    chatbot = GroqChatbot(local_only=args.local)
    
    # Override model if specified
    if args.model:
        chatbot.model = args.model
        print(f"Using custom model: {args.model}")
    
    # Start chat session
    chatbot.start_chat() 