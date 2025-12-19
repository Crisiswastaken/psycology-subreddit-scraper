"""
Reddit Data Cleaning & Compilation Script
==========================================

USAGE:
    python clean_compile.py

DESCRIPTION:
    Loads all JSON files from the output/ directory, cleans and deduplicates
    Reddit posts, then saves them to a single JSONL file for further analysis
    or model training.

REQUIREMENTS:
    - Python 3.7+
    - Standard library only (no external dependencies)

INPUT:
    - JSON files in ./output/ directory
    - Each file should have 'posts' list containing post dictionaries

OUTPUT:
    - compiled_clean.jsonl: One post per line in JSON format
    - Console logs with processing statistics

AUTHOR: Your Name
DATE: 2025-10-13
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict

# ============================================================================
# CONFIGURATION
# ============================================================================

# Directory containing scraped JSON files
INPUT_DIR = Path("output")

# Output file path
OUTPUT_FILE = Path("compiled_clean.jsonl")

# Minimum body length (characters) to keep a post
MIN_BODY_LEN = 5

# Remove duplicate posts based on title similarity
REMOVE_DUPLICATES = True

# Strings indicating deleted/removed content
DELETED_MARKERS = {
    "[deleted]",
    "[removed]",
    "[removed by reddit]",
    "[deleted by user]",
    "**removed**",
    "**deleted**"
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_json_files(directory: Path) -> List[Dict]:
    """
    Load all JSON files from the specified directory.
    
    Args:
        directory: Path to directory containing JSON files
        
    Returns:
        List of parsed JSON objects
    """
    json_data = []
    json_files = list(directory.glob("*.json"))
    
    if not json_files:
        print(f"⚠️  No JSON files found in {directory}")
        return json_data
    
    print(f"📂 Found {len(json_files)} JSON file(s) in {directory}")
    
    for filepath in json_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                json_data.append(data)
                print(f"   ✓ Loaded: {filepath.name}")
        except json.JSONDecodeError as e:
            print(f"   ✗ Error parsing {filepath.name}: {e}")
        except Exception as e:
            print(f"   ✗ Error reading {filepath.name}: {e}")
    
    return json_data


def clean_text(text: Optional[str]) -> str:
    """
    Clean text content by removing URLs, excess whitespace, and unwanted characters.
    
    Args:
        text: Raw text string
        
    Returns:
        Cleaned text string
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove URLs (http, https, www)
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    text = re.sub(r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove markdown formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
    text = re.sub(r'~~([^~]+)~~', r'\1', text)      # Strikethrough
    
    # Remove excessive newlines and whitespace
    text = re.sub(r'\n\s*\n', '\n', text)  # Multiple newlines to single
    text = re.sub(r'[ \t]+', ' ', text)    # Multiple spaces to single
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def is_valid_post(post: Dict, min_length: int = MIN_BODY_LEN) -> bool:
    """
    Check if a post meets validity criteria.
    
    Args:
        post: Post dictionary
        min_length: Minimum body length in characters
        
    Returns:
        True if post is valid, False otherwise
    """
    body = post.get('body', '').strip()
    title = post.get('title', '').strip()
    
    # Check for deleted/removed content
    if any(marker in body.lower() for marker in DELETED_MARKERS):
        return False
    
    # Check minimum length
    if len(body) < min_length:
        return False
    
    # Check for empty title
    if not title:
        return False
    
    return True


def normalize_title(title: str) -> str:
    """
    Normalize title for duplicate detection.
    
    Args:
        title: Post title
        
    Returns:
        Normalized title (lowercase, no punctuation)
    """
    # Convert to lowercase
    normalized = title.lower()
    
    # Remove punctuation and extra spaces
    normalized = re.sub(r'[^\w\s]', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized)
    
    return normalized.strip()


# ============================================================================
# POST PROCESSING
# ============================================================================

def process_post(post: Dict) -> Optional[Dict]:
    """
    Process and clean a single post.
    
    Args:
        post: Raw post dictionary
        
    Returns:
        Cleaned post dictionary or None if invalid
    """
    # Clean title and body
    cleaned_post = {
        'subreddit': post.get('subreddit', 'unknown'),
        'title': clean_text(post.get('title', '')),
        'body': clean_text(post.get('body', ''))
    }
    
    # Validate post (need to add temp fields for validation)
    temp_post = cleaned_post.copy()
    
    # Validate post
    if not is_valid_post(temp_post):
        return None
    
    return cleaned_post


def deduplicate_posts(posts: List[Dict]) -> Tuple[List[Dict], int]:
    """
    Remove duplicate posts based on normalized title.
    
    Args:
        posts: List of post dictionaries
        
    Returns:
        Tuple of (deduplicated posts list, number of duplicates removed)
    """
    seen_titles: Set[str] = set()
    unique_posts = []
    duplicates = 0
    
    for post in posts:
        normalized = normalize_title(post['title'])
        
        if normalized not in seen_titles:
            seen_titles.add(normalized)
            unique_posts.append(post)
        else:
            duplicates += 1
    
    return unique_posts, duplicates


def calculate_stats(posts: List[Dict]) -> Dict:
    """
    Calculate statistics for the cleaned dataset.
    
    Args:
        posts: List of cleaned post dictionaries
        
    Returns:
        Dictionary containing statistics
    """
    if not posts:
        return {}
    
    # Overall stats
    total_posts = len(posts)
    total_body_length = sum(len(p['body']) for p in posts)
    avg_body_length = total_body_length / total_posts if total_posts > 0 else 0
    
    # Per-subreddit stats
    subreddit_stats = defaultdict(lambda: {'count': 0, 'total_length': 0})
    
    for post in posts:
        sub = post['subreddit']
        subreddit_stats[sub]['count'] += 1
        subreddit_stats[sub]['total_length'] += len(post['body'])
    
    # Calculate averages
    for sub, stats in subreddit_stats.items():
        stats['avg_length'] = stats['total_length'] / stats['count']
    
    return {
        'total_posts': total_posts,
        'avg_body_length': avg_body_length,
        'subreddit_stats': dict(subreddit_stats)
    }


# ============================================================================
# MAIN PROCESSING
# ============================================================================

def main():
    """Main processing pipeline."""
    print("=" * 70)
    print("Reddit Data Cleaning & Compilation")
    print("=" * 70)
    print()
    
    # Check if input directory exists
    if not INPUT_DIR.exists():
        print(f"❌ Input directory not found: {INPUT_DIR}")
        print(f"   Please create the directory and add JSON files.")
        return
    
    # Load JSON files
    print("📥 LOADING DATA")
    print("-" * 70)
    json_data = load_json_files(INPUT_DIR)
    
    if not json_data:
        print("❌ No data loaded. Exiting.")
        return
    
    # Extract all posts
    print()
    print("🔍 EXTRACTING POSTS")
    print("-" * 70)
    all_posts = []
    for data in json_data:
        posts = data.get('posts', [])
        all_posts.extend(posts)
    
    print(f"   Total posts extracted: {len(all_posts)}")
    
    # Clean and filter posts
    print()
    print("🧹 CLEANING & FILTERING")
    print("-" * 70)
    cleaned_posts = []
    skipped = 0
    
    for post in all_posts:
        cleaned = process_post(post)
        if cleaned:
            cleaned_posts.append(cleaned)
        else:
            skipped += 1
    
    print(f"   ✓ Cleaned posts: {len(cleaned_posts)}")
    print(f"   ✗ Skipped posts: {skipped}")
    
    # Deduplicate if enabled
    if REMOVE_DUPLICATES:
        print()
        print("🔄 DEDUPLICATING")
        print("-" * 70)
        cleaned_posts, duplicates = deduplicate_posts(cleaned_posts)
        print(f"   ✓ Unique posts: {len(cleaned_posts)}")
        print(f"   ✗ Duplicates removed: {duplicates}")
    
    # Calculate statistics
    print()
    print("📊 DATASET STATISTICS")
    print("-" * 70)
    stats = calculate_stats(cleaned_posts)
    
    if stats:
        print(f"   Total posts: {stats['total_posts']}")
        print(f"   Average body length: {stats['avg_body_length']:.1f} characters")
        print()
        print("   Per-subreddit breakdown:")
        for sub, sub_stats in sorted(stats['subreddit_stats'].items(), 
                                     key=lambda x: x[1]['count'], 
                                     reverse=True):
            print(f"      • {sub:30s} {sub_stats['count']:4d} posts  "
                  f"(avg: {sub_stats['avg_length']:.0f} chars)")
    
    # Save to JSONL
    print()
    print("💾 SAVING OUTPUT")
    print("-" * 70)
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for post in cleaned_posts:
                json_line = json.dumps(post, ensure_ascii=False)
                f.write(json_line + '\n')
        
        print(f"   ✓ Saved to: {OUTPUT_FILE}")
        print(f"   ✓ File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
    except Exception as e:
        print(f"   ❌ Error saving file: {e}")
        return
    
    # Final summary
    print()
    print("=" * 70)
    print("✅ PROCESSING COMPLETE")
    print("=" * 70)
    print(f"   Input files: {len(json_data)}")
    print(f"   Total posts processed: {len(all_posts)}")
    print(f"   Final clean dataset: {len(cleaned_posts)} posts")
    print(f"   Output: {OUTPUT_FILE}")
    print()


if __name__ == "__main__":
    main()