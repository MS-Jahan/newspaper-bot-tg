# Custom Telegraph API Integration

This document explains the custom Telegraph API integration for the newspaper-bot-tg project, which replaces the previously used third-party library.

## Overview

The Telegraph API integration provides functionality to:
- Create Telegraph pages for news articles
- Convert HTML content to Telegraph-compatible node format
- Manage Telegraph account settings
- Track page statistics

## Files

- **telegraph_api.py**: Main implementation of the Telegraph API client
- **post.py**: Adapter that maintains backward compatibility with the existing code

## Usage Examples

### Basic Usage

```python
from telegraph_api import post_to_telegraph

# Post content to Telegraph
result = post_to_telegraph(
    title="Article Title",
    author_name="Author Name",
    image_url="https://example.com/image.jpg",
    html_content="<p>Article content</p>",
    source_url="https://example.com/article"
)

# Get the Telegraph URL
telegraph_url = result["url"]
```

### Advanced Usage

```python
from telegraph_api import TelegraphAPI

# Create a Telegraph API client instance
telegraph = TelegraphAPI(access_token="your_access_token")

# Get account info
account_info = telegraph.get_account_info()
print(f"Account name: {account_info.get('short_name')}")

# Create a new page
content = [
    {"tag": "p", "children": ["Hello, world!"]},
    {"tag": "img", "attrs": {"src": "https://example.com/image.jpg"}}
]

page = telegraph.create_page(
    title="Test Page",
    content=content,
    author_name="Test Author"
)

print(f"Created page: {page.get('url')}")
```

### Converting HTML to Telegraph Nodes

```python
from telegraph_api import html_to_node

html_content = """
<h3>Article Title</h3>
<p>This is a <b>paragraph</b> with <i>formatting</i>.</p>
<img src="https://example.com/image.jpg" />
"""

nodes = html_to_node(html_content)
```

## Environment Variables

The implementation uses the following environment variable:

- `TELEGRAPH_ACCESS_TOKEN`: Your Telegraph access token

## API Methods

The `TelegraphAPI` class provides the following methods:

- `create_account(short_name, author_name, author_url)`
- `get_account_info(fields)`
- `edit_account_info(short_name, author_name, author_url)`
- `revoke_access_token()`
- `create_page(title, content, author_name, author_url, return_content)`
- `edit_page(path, title, content, author_name, author_url, return_content)`
- `get_page(path, return_content)`
- `get_page_list(offset, limit)`
- `get_views(path, year, month, day, hour)`

## Content Format

Telegraph uses a DOM-based format for page content. Each node can be:

1. A string (for text nodes)
2. A node object with:
   - `tag`: HTML tag name (e.g., "p", "a", "img")
   - `attrs`: Object with attributes ("href" for links, "src" for images)
   - `children`: Array of child nodes

## Supported Tags

The following HTML tags are supported by Telegraph:
`a`, `aside`, `b`, `blockquote`, `br`, `code`, `em`, `figcaption`, `figure`, `h3`, `h4`, `hr`, `i`, `iframe`, `img`, `li`, `ol`, `p`, `pre`, `s`, `strong`, `u`, `ul`, `video`

## Error Handling

All API methods raise exceptions with descriptive messages if the Telegraph API returns an error. Common errors include:
- Invalid access token
- Missing required parameters
- Content size exceeds limits (64 KB)

## References

- [Official Telegraph API Documentation](https://telegra.ph/api)
