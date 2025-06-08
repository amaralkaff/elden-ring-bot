# Elden Ring Chat Bot

An AI-powered chatbot that provides answers to questions about Elden Ring using the latest data from multiple Reddit communities. The bot fetches information about game mechanics, builds, hacks, mods, and cheats from subreddits including r/Eldenring, r/EldenRingMods, r/cheatengine, and r/GuidedHacking.

## 🚀 Two Usage Options

### Option 1: Quick & Easy (Recommended)
Uses Groq API for instant responses - no training needed!

### Option 2: Local Training 
Train your own model on Reddit data for offline usage.

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

3. Choose your approach:

**Quick Start (API):**
```bash
python web.py           # Start web interface
```

**Or train local model:**
```bash
python main.py          # Choose option 4 to train
```

## 🎯 Features

### Web Interface
- Modern ChatGPT-style UI with dark theme
- Chat history with local storage
- Copy/paste functionality
- Real-time Reddit data fetching
- Multiple AI models

### Local Training Option
- Train custom models on Reddit data
- Offline usage after training
- PyTorch & Transformers support
- Custom fine-tuning on Elden Ring content

## 📋 Commands

```bash
# Web Interface (Recommended)
python web.py           # Start web interface at localhost:8000

# Menu Interface  
python main.py          # Interactive menu with all options

# Direct Commands
python main.py fetch    # Get latest Reddit data
python main.py chat     # Terminal chat with API
python main.py chat --local  # Terminal chat offline mode

# Local Training (Advanced)
python train_local_model.py  # Train your own model
python local_chatbot.py      # Use trained local model
```

## 🔧 For Developers

The project includes both approaches so you can:
- **Fork & use API**: Quick setup for most users
- **Fork & train locally**: Full control and offline usage
- **Mix both**: Use API for quick responses, train for specific use cases

## 🌐 Deploy for Free

Ready-to-deploy to:
- Render.com (render.yaml included)
- Railway.app (railway.json included) 
- Heroku (Procfile included)
- Fly.io

Just connect your GitHub repo to any platform!

That's it! 🎮 