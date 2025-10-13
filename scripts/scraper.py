"""
Reddit Top Posts Scraper (Psychology & Mental Health)
-----------------------------------------------------
Purpose: Scrape top posts of all time from selected subreddits
         and save post title + body into a JSON file.

Requirements:
- Python 3.8+
- praw (`pip install praw`)
- python-dotenv (`pip install python-dotenv`)

Instructions:
1. Create a Reddit app here: https://www.reddit.com/prefs/apps
   - Choose "script" as the app type.
   - Note down client_id, client_secret, user_agent.
2. Set environment variables or replace placeholders in CONFIG section.
3. Run the script: python reddit_scraper.py
4. Output: reddit_psych_posts.json
"""

import praw
import json
import time
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env in current directory and parent directories
    env_path = Path('.') / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded environment variables from {env_path.absolute()}\n")
    else:
        load_dotenv()  # Try to find .env in parent directories
except ImportError:
    print("⚠ python-dotenv not installed. Install it with: pip install python-dotenv")
    print("  Or set environment variables manually in your shell.\n")

# ---------------- CONFIG ---------------- #
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
USER_AGENT = os.getenv("USER_AGENT", "psych_ai_scraper_v1")

# List of subreddits to scrape
SUBREDDITS = [
    "psychology", "askpsychology", "AcademicPsychology",
    "socialpsychology", "cogsci", "socialengineering",
    "selfimprovement", "IWantToLearn",
    "mentalhealth", "talktherapy", "relationships", "offmychest"
]

# Maximum posts per subreddit (set to None for all available posts)
POST_LIMIT = 1000

# Delay between subreddit scrapes to avoid rate limiting (seconds)
REQUEST_DELAY = 2

# Output file
OUTPUT_FILE = "reddit_psych_posts.json"
# ---------------------------------------- #

def validate_credentials() -> bool:
    """Validate that Reddit API credentials are set."""
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        print("ERROR: Reddit API credentials not found!")
        print("\nTroubleshooting:")
        print("1. Make sure you have a .env file in the current directory")
        print("2. Your .env file should contain:")
        print("   REDDIT_CLIENT_ID=your_client_id_here")
        print("   REDDIT_CLIENT_SECRET=your_client_secret_here")
        print("   USER_AGENT=your_user_agent_here")
        print("\n3. Install python-dotenv: pip install python-dotenv")
        print("\n4. Or set variables in your shell:")
        print("   export REDDIT_CLIENT_ID=your_client_id")
        print("   export REDDIT_CLIENT_SECRET=your_client_secret")
        return False
    
    print(f"✓ Credentials loaded successfully")
    print(f"  Client ID: {REDDIT_CLIENT_ID[:8]}..." if len(REDDIT_CLIENT_ID) > 8 else f"  Client ID: {REDDIT_CLIENT_ID}")
    print(f"  User Agent: {USER_AGENT}\n")
    return True

def init_reddit() -> Optional[praw.Reddit]:
    """Initialize Reddit API connection with read-only mode."""
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=USER_AGENT,
            check_for_async=False,
            ratelimit_seconds=300  # Wait 5 minutes if rate limited
        )
        # Test connection
        _ = reddit.read_only
        print(f"✓ Successfully connected to Reddit API (Read-only: {reddit.read_only})")
        return reddit
    except Exception as e:
        print(f"ERROR: Failed to initialize Reddit API: {e}")
        return None

def scrape_subreddit(reddit: praw.Reddit, subreddit_name: str, limit: int = POST_LIMIT) -> List[Dict]:
    """
    Scrape top posts of all time from a subreddit.
    Returns a list of dictionaries with post metadata.
    """
    scraped_posts = []
    try:
        subreddit = reddit.subreddit(subreddit_name)
        print(f"Scraping r/{subreddit_name}...")

        for post in subreddit.top(time_filter='all', limit=limit):
            # Include posts with text content
            if post.selftext and post.selftext.strip():
                post_data = {
                    "subreddit": subreddit_name,
                    "post_id": post.id,
                    "title": post.title.strip(),
                    "body": post.selftext.strip(),
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "created_utc": post.created_utc,
                    "url": f"https://reddit.com{post.permalink}",
                    "author": str(post.author) if post.author else "[deleted]"
                }
                scraped_posts.append(post_data)
        
        print(f"✓ r/{subreddit_name}: {len(scraped_posts)} posts collected\n")
        
    except praw.exceptions.RedditAPIException as e:
        print(f"⚠ Reddit API error for r/{subreddit_name}: {e}")
    except Exception as e:
        print(f"⚠ Error scraping r/{subreddit_name}: {e}")

    return scraped_posts

def save_to_json(data: List[Dict], filename: str) -> bool:
    """Save scraped data to JSON file with metadata."""
    try:
        output = {
            "metadata": {
                "scrape_date": datetime.utcnow().isoformat(),
                "total_posts": len(data),
                "subreddits": SUBREDDITS,
                "post_limit_per_subreddit": POST_LIMIT
            },
            "posts": data
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Successfully saved {len(data)} posts to {filename}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to save JSON: {e}")
        return False

def main():
    """Main function to scrape all subreddits and save JSON output."""
    print("=" * 60)
    print("Reddit Psychology & Mental Health Scraper")
    print("=" * 60 + "\n")
    
    # Validate credentials
    if not validate_credentials():
        return
    
    # Initialize Reddit API
    reddit = init_reddit()
    if not reddit:
        return
    
    print(f"\nTarget subreddits: {', '.join(SUBREDDITS)}")
    print(f"Posts per subreddit: {POST_LIMIT if POST_LIMIT else 'all available'}")
    print(f"Request delay: {REQUEST_DELAY}s\n")
    print("-" * 60 + "\n")
    
    all_posts = []
    
    # Scrape each subreddit
    for i, sub in enumerate(SUBREDDITS, 1):
        print(f"[{i}/{len(SUBREDDITS)}] ", end="")
        posts = scrape_subreddit(reddit, sub, limit=POST_LIMIT)
        all_posts.extend(posts)
        
        # Rate limiting delay (except after last subreddit)
        if i < len(SUBREDDITS):
            time.sleep(REQUEST_DELAY)
    
    # Save results
    print("-" * 60)
    print(f"\nScraping complete! Total posts collected: {len(all_posts)}")
    
    if all_posts:
        if save_to_json(all_posts, OUTPUT_FILE):
            print(f"Output file: {OUTPUT_FILE}")
            
            # Print summary statistics
            print("\nSummary by subreddit:")
            subreddit_counts = {}
            for post in all_posts:
                sub = post['subreddit']
                subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1
            
            for sub, count in sorted(subreddit_counts.items()):
                print(f"  r/{sub}: {count} posts")
    else:
        print("⚠ No posts were collected. Check credentials and subreddit names.")

if __name__ == "__main__":
    main()