# filepath: f:\Code\newspaper-bot-tg\post.py
from telegraph_api import post_to_telegraph
from dotenv import load_dotenv
import os

load_dotenv()

def postToTelegraph(postTitle, authorName, sourceImageUrl, postHtml, actual_article_url):
    """
    Post content to Telegraph using our custom Telegraph API implementation.
    
    Args:
        postTitle: Title of the article
        authorName: Name of the author
        sourceImageUrl: URL of the main image
        postHtml: HTML content of the article
        actual_article_url: Source URL of the article
        
    Returns:
        Dictionary with the Telegraph URL and path
    """
    # Use our custom Telegraph API implementation
    return post_to_telegraph(
        title=postTitle,
        author_name=authorName,
        image_url=sourceImageUrl,
        html_content=postHtml,
        source_url=actual_article_url
    )

