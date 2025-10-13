import praw

reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="my_psych_scraper_v1"
)

# Test: print top post from r/psychology
for post in reddit.subreddit("psychology").top(limit=1):
    print(post.title)
    print(post.selftext)
