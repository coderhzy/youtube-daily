"""
Helper utility functions
"""

import re
from typing import List, Dict, Any

def clean_text(text: str) -> str:
    """
    Clean text content

    Args:
        text: Raw text

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Remove extra whitespace
    text = ' '.join(text.split())

    # Remove special characters
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

    return text.strip()

def extract_title(content: str, max_length: int = 60) -> str:
    """
    Extract title from content

    Args:
        content: News content
        max_length: Maximum title length

    Returns:
        Extracted title
    """
    # Clean content first
    content = clean_text(content)

    # Try to get first sentence
    if '。' in content:
        title = content.split('。')[0] + '。'
    elif '.' in content and len(content.split('.')[0]) < max_length:
        title = content.split('.')[0] + '.'
    else:
        title = content[:max_length]

    # Add ellipsis if truncated
    if len(title) >= max_length and not title.endswith(('。', '.', '!', '！')):
        title = title[:max_length-3] + '...'

    return title

def deduplicate_news(news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate news items based on content similarity

    Args:
        news_list: List of news items

    Returns:
        Deduplicated news list
    """
    if not news_list:
        return []

    seen_contents = set()
    unique_news = []

    for news in news_list:
        # Use first 100 characters of content as dedup key
        content = news.get('content', '')
        content_key = content[:100].lower().strip()

        if content_key and content_key not in seen_contents:
            seen_contents.add(content_key)
            unique_news.append(news)

    return unique_news

def filter_quality_news(news_list: List[Dict[str, Any]], min_length: int = 30) -> List[Dict[str, Any]]:
    """
    Filter out low-quality news

    Args:
        news_list: List of news items
        min_length: Minimum content length

    Returns:
        Filtered news list
    """
    quality_news = []

    for news in news_list:
        title = news.get('title', '')
        content = news.get('content', '')

        # Skip if title or content is empty
        if not title or not content:
            continue

        # Skip if content is too short
        if len(content) < min_length:
            continue

        quality_news.append(news)

    return quality_news
