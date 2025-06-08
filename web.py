#!/usr/bin/env python3
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import local modules
from groq_chatbot import GroqChatbot
from data_fetcher import RedditDataFetcher

# Initialize Flask app
app = Flask(__name__)

# Initialize chatbot and data fetcher
chatbot = GroqChatbot(local_only=False)
data_fetcher = RedditDataFetcher()

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        # Get user message from request
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get response from chatbot
        response = chatbot.get_response(user_message)
        
        # Return response
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/models')
def models():
    """Get available models"""
    models = [
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "llama2-70b-4096", 
        "mixtral-8x7b-32768"
    ]
    return jsonify({'models': models})

@app.route('/set_model', methods=['POST'])
def set_model():
    """Set the model to use"""
    try:
        data = request.json
        model = data.get('model', '')
        
        if not model:
            return jsonify({'error': 'No model provided'}), 400
        
        # Update chatbot model
        chatbot.model = model
        
        return jsonify({'success': True, 'model': model})
    except Exception as e:
        print(f"Error setting model: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reddit/fetch-and-clean', methods=['GET'])
def fetch_and_clean_data():
    """Fetch and clean Reddit data from multiple subreddits"""
    try:
        # Define multiple subreddits to fetch from
        subreddits = ['Eldenring', 'Nightreign', 'EldenRingMods', 'macgaming', 'cheatengine', 'GuidedHacking']
        filter_elden_ring = request.args.get('filter_elden_ring', 'true').lower() == 'true'
        
        all_posts = []
        processed_subreddits = []
        
        # Fetch from each subreddit
        for subreddit in subreddits:
            try:
                # Update data fetcher subreddit
                data_fetcher.subreddit_name = subreddit
                
                # Fetch new data (limited to 10 posts per subreddit)
                posts = data_fetcher.fetch_data(limit=10, search_terms=filter_elden_ring)
                
                if isinstance(posts, list) and len(posts) > 0:
                    all_posts.extend(posts)
                    processed_subreddits.append(subreddit)
                    print(f"Fetched {len(posts)} posts from r/{subreddit}")
                
            except Exception as e:
                print(f"Error fetching from r/{subreddit}: {e}")
                continue
        
        # Clean and save combined data
        if all_posts:
            success = data_fetcher.clean_data(all_posts)
            
            if success:
                # Reload chatbot context with new data
                chatbot.reload_context_data()
                
                return jsonify({
                    'status': 'success',
                    'message': f'Data fetched and cleaned successfully from {len(processed_subreddits)} subreddits',
                    'posts_processed': len(all_posts),
                    'subreddits': processed_subreddits,
                    'filter_applied': filter_elden_ring
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to clean data'
                }), 500
        else:
            return jsonify({
                'status': 'warning',
                'message': 'No posts found from any subreddit',
                'posts_processed': 0,
                'subreddits': processed_subreddits
            })
            
    except Exception as e:
        print(f"Error in fetch_and_clean_data: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/reddit/fetch', methods=['GET'])
def fetch_reddit_data():
    """Fetch Reddit data from multiple subreddits without cleaning"""
    try:
        # Define multiple subreddits to fetch from
        subreddits = ['Eldenring', 'Nightreign', 'EldenRingMods', 'macgaming', 'cheatengine', 'GuidedHacking']
        filter_elden_ring = request.args.get('filter_elden_ring', 'true').lower() == 'true'
        
        all_formatted_posts = []
        processed_subreddits = []
        
        # Fetch from each subreddit
        for subreddit in subreddits:
            try:
                # Update data fetcher subreddit
                data_fetcher.subreddit_name = subreddit
                
                # Fetch data (limited to 10 posts per subreddit)
                posts = data_fetcher.fetch_data(limit=10, search_terms=filter_elden_ring)
                
                if isinstance(posts, list) and len(posts) > 0:
                    if isinstance(posts[0], str):
                        # Sample data case - skip for multi-subreddit fetch
                        continue
                    else:
                        # Reddit posts case
                        for post in posts:
                            all_formatted_posts.append({
                                'title': post.title,
                                'content': post.selftext,
                                'score': post.score,
                                'url': post.url,
                                'created_utc': post.created_utc,
                                'id': post.id,
                                'author': str(post.author) if post.author else 'deleted',
                                'subreddit': subreddit
                            })
                        processed_subreddits.append(subreddit)
                        print(f"Fetched {len(posts)} posts from r/{subreddit}")
                
            except Exception as e:
                print(f"Error fetching from r/{subreddit}: {e}")
                continue
        
        return jsonify({
            'status': 'success',
            'data': all_formatted_posts,
            'source': 'reddit_api_multi',
            'count': len(all_formatted_posts),
            'subreddits': processed_subreddits,
            'filter_applied': filter_elden_ring
        })
            
    except Exception as e:
        print(f"Error in fetch_reddit_data: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Get port from environment variable for deployment
    port = int(os.environ.get('PORT', 8000))
    
    # Run Flask app
    app.run(debug=False, host='0.0.0.0', port=port)