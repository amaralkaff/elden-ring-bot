# Elden Ring Chat Bot

An AI-powered chatbot that provides answers to questions about Elden Ring using the latest data from multiple Reddit communities. The bot fetches information about game mechanics, builds, hacks, mods, and cheats from subreddits including r/Eldenring, r/EldenRingMods, r/cheatengine, and r/GuidedHacking.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Add your API keys to `.env` file:
```
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret  
REDDIT_USER_AGENT="EldenRingBot/1.0"
GROQ_API_KEY=your_key
```

3. Run the web app:
```bash
python web.py
```

Open http://localhost:8000 and start chatting!

## Features

- Ask any Elden Ring questions / hackings / cheating  / modding
- Fetches latest posts from Reddit
- Multiple AI models available
- Clean web interface with copy/paste

## Commands

```bash
python web.py           # Start web interface
python main.py fetch    # Get Reddit data
python main.py chat     # Terminal chat
```

That's it! 