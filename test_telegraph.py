import os
from dotenv import load_dotenv
from telegraph_api import TelegraphAPI, html_to_node, post_to_telegraph

def test_telegraph_api():
    """Test the custom Telegraph API implementation"""
    # Create a test HTML content
    html_content = """
    <h3>Test Article Heading</h3>
    <p>This is a test paragraph for the Telegraph API.</p>
    <p>It contains <b>bold</b> and <i>italic</i> text.</p>
    """
    
    # Test the html_to_node conversion
    nodes = html_to_node(html_content)
    print("[test_telegraph.py] Converted HTML to nodes:")
    print(nodes)
    
    # Test posting to Telegraph if access token is available
    load_dotenv()
    if os.getenv('TELEGRAPH_ACCESS_TOKEN'):
        print("[test_telegraph.py] \nTesting post to Telegraph...")
        result = post_to_telegraph(
            title="Test Article",
            author_name="Telegraph API Tester",
            image_url="https://picsum.photos/800/600",  # Random image from Lorem Picsum
            html_content=html_content,
            source_url="https://example.com"
        )
        print(f"[test_telegraph.py] Created Telegraph page: {result['url']}")
    else:
        print("[test_telegraph.py] \nSkipping Telegraph post test - no access token found")

if __name__ == "__main__":
    test_telegraph_api()
