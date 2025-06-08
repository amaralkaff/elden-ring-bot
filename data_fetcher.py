import praw
import re
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request

# Load environment variables
load_dotenv()

app = Flask(__name__)

class RedditDataFetcher:
    def __init__(self):
        """Initialize the Reddit API client using environment variables"""
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = os.getenv("REDDIT_USER_AGENT")
        
        # Default subreddit to fetch data from
        self.subreddit_name = "Eldenring"
        
        # Load sample data
        self.sample_data = self.load_sample_data()
    
    def load_sample_data(self):
        """Load sample data from file or use default data"""
        sample_data_path = "data/sample_data.txt"
        if os.path.exists(sample_data_path):
            try:
                with open(sample_data_path, "r", encoding="utf-8") as f:
                    return [line.strip() for line in f.readlines() if line.strip()]
            except Exception as e:
                print(f"Error loading sample data: {e}")
        
    def connect_to_reddit(self):
        """Establish connection to Reddit API"""
        try:
            reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
                check_for_updates=False,
                read_only=True
            )
            return reddit
        except Exception as e:
            print(f"Error connecting to Reddit: {e}")
            return None
    
    def fetch_data(self, limit=None, save_raw=True, search_terms=None):
        """Fetch data from Reddit and save to file"""
        print(f"Fetching data from r/{self.subreddit_name}...")
        
        try:
            reddit = self.connect_to_reddit()
            if not reddit:
                raise Exception("Failed to connect to Reddit API")
            
            subreddit = reddit.subreddit(self.subreddit_name)
            all_posts = []
            
            # Fetch latest posts only (new posts are the most recent)
            try:
                posts = list(subreddit.new(limit=10))
                all_posts.extend(posts)
                print(f"Fetched {len(posts)} latest posts from r/{self.subreddit_name}")
            except Exception as e:
                print(f"Error fetching new posts: {e}")
            
            # Remove duplicates based on post ID
            unique_posts = {}
            for post in all_posts:
                unique_posts[post.id] = post
            all_posts = list(unique_posts.values())
            
            # Filter for Elden Ring related content if search terms provided
            if search_terms:
                filtered_posts = []
                search_keywords = ['elden ring', 'eldenring', 'cheat', 'hack', 'mod', 'trainer']
                for post in all_posts:
                    post_text = f"{post.title} {post.selftext}".lower()
                    if any(keyword in post_text for keyword in search_keywords):
                        filtered_posts.append(post)
                all_posts = filtered_posts
            
            print(f"Fetched {len(all_posts)} unique posts")
            
            # Save raw data
            if save_raw:
                with open("data/raw_data.txt", "w", encoding="utf-8") as file:
                    for post in all_posts:
                        file.write(f"TITLE: {post.title}\n")
                        file.write(f"CONTENT: {post.selftext}\n")
                        file.write(f"SCORE: {post.score}\n")
                        file.write(f"URL: {post.url}\n")
                        file.write("---\n")
            
            return all_posts
            
        except Exception as e:
            print(f"Error fetching data from Reddit: {e}")
            print("Using sample data instead.")
            return self.sample_data
    
    def clean_data(self, posts, output_file="data/cleaned_data.txt"):
        """Clean and process the fetched data"""
        print("Cleaning and processing data...")
        
        try:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Process posts
            if isinstance(posts, list) and len(posts) > 0 and isinstance(posts[0], str):
                # Sample data case
                cleaned_data = posts
            elif isinstance(posts, list) and len(posts) > 0:
                # Reddit posts case
                cleaned_data = []
                for post in posts:
                    # Extract title and content
                    text = f"{post.title} {post.selftext}"
                    # Clean text
                    cleaned_text = re.sub(r"http\S+|www\S+|[^a-zA-Z0-9\s]", "", text)
                    cleaned_data.append(cleaned_text)
            else:
                # Empty posts list or no posts
                cleaned_data = self.sample_data
                print("No posts to process, using sample data")
            
            # Save cleaned data
            with open(output_file, "w", encoding="utf-8") as file:
                for item in cleaned_data:
                    file.write(f"{item.strip()}\n")
            
            print(f"Data cleaned and saved to {output_file}")
            return True
            
        except Exception as e:
            print(f"Error cleaning data: {e}")
            return False

    def fetch_and_clean(self, limit=20):
        """Fetch and clean data in one operation"""
        posts = self.fetch_data(limit=limit)
        return self.clean_data(posts)

@app.route('/api/reddit/fetch', methods=['GET'])
def api_fetch_reddit_data():
    """API endpoint to fetch all Reddit data"""
    try:
        subreddit = request.args.get('subreddit', 'UnKnoWnCheaTs')
        search_elden_ring = request.args.get('filter_elden_ring', 'true').lower() == 'true'
        
        fetcher = RedditDataFetcher()
        fetcher.subreddit_name = subreddit
        posts = fetcher.fetch_data(limit=None, search_terms=search_elden_ring)
        
        if isinstance(posts, list) and len(posts) > 0 and isinstance(posts[0], str):
            # Sample data case
            return jsonify({
                'status': 'success',
                'data': posts,
                'source': 'sample_data',
                'count': len(posts)
            })
        else:
            # Reddit posts case
            formatted_posts = []
            for post in posts:
                formatted_posts.append({
                    'title': post.title,
                    'content': post.selftext,
                    'score': post.score,
                    'url': post.url,
                    'created_utc': post.created_utc,
                    'id': post.id,
                    'author': str(post.author) if post.author else 'deleted'
                })
            
            return jsonify({
                'status': 'success',
                'data': formatted_posts,
                'source': 'reddit_api',
                'count': len(formatted_posts),
                'subreddit': subreddit
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/reddit/clean', methods=['POST'])
def api_clean_reddit_data():
    """API endpoint to clean Reddit data"""
    try:
        data = request.get_json()
        posts = data.get('posts', [])
        
        fetcher = RedditDataFetcher()
        success = fetcher.clean_data(posts)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Data cleaned successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to clean data'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/reddit/fetch-and-clean', methods=['GET'])
def api_fetch_and_clean():
    """API endpoint to fetch and clean all Reddit data in one operation"""
    try:
        subreddit = request.args.get('subreddit', 'UnKnoWnCheaTs')
        search_elden_ring = request.args.get('filter_elden_ring', 'true').lower() == 'true'
        
        fetcher = RedditDataFetcher()
        fetcher.subreddit_name = subreddit
        posts = fetcher.fetch_data(limit=None, search_terms=search_elden_ring)
        success = fetcher.clean_data(posts)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Data fetched and cleaned successfully from r/{subreddit}',
                'posts_processed': len(posts),
                'filter_applied': search_elden_ring
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to fetch and clean data'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# For direct execution
if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
