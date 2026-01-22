"""
Custom implementation of Telegraph API client for the newspaper-bot project.
Based on the Telegraph API documentation: https://telegra.ph/api
"""

import json
import os
from curl_cffi import requests
from typing import Dict, List, Optional, Union, Any
from dotenv import load_dotenv

# API Base URL
API_BASE_URL = "https://api.telegra.ph"


class TelegraphAPI:
    """Custom Telegraph API client"""

    def __init__(self, access_token: Optional[str] = None):
        """Initialize Telegraph API client with optional access token"""
        load_dotenv()
        self.access_token = access_token or os.getenv("TELEGRAPH_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError(
                "Telegraph access token is required. Set TELEGRAPH_ACCESS_TOKEN in .env file."
            )

    def _make_request(
        self, method: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Make a request to Telegraph API"""
        url = f"{API_BASE_URL}/{method}"
        print(f"[telegraph_api.py] Making Telegraph API request to: {method}")

        try:
            if method.startswith("get"):
                print(f"[telegraph_api.py] Sending GET request with params: {params}")
                response = requests.get(
                    url, params=params, impersonate="chrome110", timeout=30
                )
            else:
                print(f"[telegraph_api.py] Sending POST request with data: {params}")
                response = requests.post(
                    url, json=params, impersonate="chrome110", timeout=30
                )

            print(
                f"[telegraph_api.py] Telegraph API response status code: {response.status_code}"
            )
            response.raise_for_status()

            result = response.json()
            if not result.get("ok", False):
                error_msg = (
                    f"Telegraph API error: {result.get('error', 'Unknown error')}"
                )
                print(f"[telegraph_api.py] ERROR: {error_msg}")
                raise ValueError(error_msg)

            print(f"[telegraph_api.py] Telegraph API request successful: {method}")
            return result.get("result", {})
        except Exception as e:
            print(f"[telegraph_api.py] Telegraph API request failed: {str(e)}")
            raise

    def create_account(
        self, short_name: str, author_name: str = "", author_url: str = ""
    ) -> Dict[str, Any]:
        """Create a new Telegraph account"""
        params = {
            "short_name": short_name,
            "author_name": author_name,
            "author_url": author_url,
        }
        return self._make_request("createAccount", params)

    def get_account_info(self, fields: List[str] = None) -> Dict[str, Any]:
        """Get information about the current Telegraph account"""
        fields = fields or ["short_name", "author_name", "author_url"]
        params = {"access_token": self.access_token, "fields": json.dumps(fields)}
        return self._make_request("getAccountInfo", params)

    def edit_account_info(
        self, short_name: str = None, author_name: str = None, author_url: str = None
    ) -> Dict[str, Any]:
        """Update information about the current Telegraph account"""
        params = {"access_token": self.access_token}
        if short_name:
            params["short_name"] = short_name
        if author_name:
            params["author_name"] = author_name
        if author_url:
            params["author_url"] = author_url

        return self._make_request("editAccountInfo", params)

    def revoke_access_token(self) -> Dict[str, Any]:
        """Revoke the current access token and generate a new one"""
        params = {"access_token": self.access_token}
        result = self._make_request("revokeAccessToken", params)
        # Update token with the new one
        self.access_token = result.get("access_token", self.access_token)
        return result

    def create_page(
        self,
        title: str,
        content: List[Dict[str, Any]],
        author_name: str = "",
        author_url: str = "",
        return_content: bool = False,
    ) -> Dict[str, Any]:
        """Create a new Telegraph page"""
        params = {
            "access_token": self.access_token,
            "title": title,
            "content": json.dumps(content),
            "return_content": return_content,
        }

        if author_name:
            params["author_name"] = author_name
        if author_url:
            params["author_url"] = author_url

        return self._make_request("createPage", params)

    def edit_page(
        self,
        path: str,
        title: str,
        content: List[Dict[str, Any]],
        author_name: str = "",
        author_url: str = "",
        return_content: bool = False,
    ) -> Dict[str, Any]:
        """Edit an existing Telegraph page"""
        params = {
            "access_token": self.access_token,
            "path": path,
            "title": title,
            "content": json.dumps(content),
            "return_content": return_content,
        }

        if author_name:
            params["author_name"] = author_name
        if author_url:
            params["author_url"] = author_url

        return self._make_request("editPage", params)

    def get_page(self, path: str, return_content: bool = False) -> Dict[str, Any]:
        """Get a Telegraph page"""
        params = {"path": path, "return_content": return_content}
        return self._make_request("getPage", params)

    def get_page_list(self, offset: int = 0, limit: int = 50) -> Dict[str, Any]:
        """Get a list of pages belonging to the Telegraph account"""
        params = {"access_token": self.access_token, "offset": offset, "limit": limit}
        return self._make_request("getPageList", params)

    def get_views(
        self,
        path: str,
        year: int = None,
        month: int = None,
        day: int = None,
        hour: int = None,
    ) -> Dict[str, Any]:
        """Get the number of views for a Telegraph article"""
        params = {"path": path}

        if year:
            params["year"] = year
        if month:
            params["month"] = month
        if day:
            params["day"] = day
        if hour:
            params["hour"] = hour

        return self._make_request("getViews", params)


# HTML to Telegraph Node converter
def html_to_node(html_content: str) -> List[Dict[str, Any]]:
    """
    Convert HTML content to Telegraph Node format.
    This is a simplified version that handles basic HTML tags.
    For a more comprehensive solution, use a proper HTML parser.
    """
    from bs4 import BeautifulSoup

    print("[telegraph_api.py] Starting HTML to Telegraph Node conversion")
    print(f"[telegraph_api.py] HTML content length: {len(html_content)} characters")

    soup = BeautifulSoup(html_content, "html.parser")
    print("[telegraph_api.py] Successfully parsed HTML with BeautifulSoup")

    # Count the number of elements for logging
    total_elements = len(list(soup.descendants))
    print(f"[telegraph_api.py] Found {total_elements} total HTML elements to process")

    # Counter for logging
    processed_elements = 0

    def process_element(element):
        nonlocal processed_elements
        processed_elements += 1

        if processed_elements % 50 == 0:  # Log every 50 elements
            print(
                f"[telegraph_api.py] Processed {processed_elements}/{total_elements} elements"
            )

        if element.name is None:
            # Text node
            return element.string if element.string and element.string.strip() else ""

        # Supported tags by Telegraph
        supported_tags = [
            "a",
            "aside",
            "b",
            "blockquote",
            "br",
            "code",
            "em",
            "figcaption",
            "figure",
            "h3",
            "h4",
            "hr",
            "i",
            "iframe",
            "img",
            "li",
            "ol",
            "p",
            "pre",
            "s",
            "strong",
            "u",
            "ul",
            "video",
        ]

        if element.name not in supported_tags:
            # Replace unsupported tags with paragraphs or just return the text content
            if element.name in ["h1", "h2", "h5", "h6", "div", "section"]:
                print(
                    f"[telegraph_api.py] Converting unsupported tag '{element.name}' to 'p'"
                )
                element.name = "p"
            else:
                print(
                    f"[telegraph_api.py] Ignoring unsupported tag '{element.name}' and processing its children"
                )
                return "".join(
                    process_element(child) for child in element.children if child
                )

        print(f"[telegraph_api.py] Processing '{element.name}' element")
        node = {"tag": element.name}

        # Handle attributes (only href and src are supported)
        attrs = {}
        if element.get("href"):
            attrs["href"] = element["href"]
            print(
                f"[telegraph_api.py] Added href attribute: {element['href'][:50]}{'...' if len(element['href']) > 50 else ''}"
            )
        if element.get("src"):
            attrs["src"] = element["src"]
            print(
                f"[telegraph_api.py] Added src attribute: {element['src'][:50]}{'...' if len(element['src']) > 50 else ''}"
            )

        if attrs:
            node["attrs"] = attrs

        # Process children
        children = [process_element(child) for child in element.children if child]
        # Filter out empty strings and None values
        children = [child for child in children if child]

        if children:
            node["children"] = children
            print(
                f"[telegraph_api.py] Added {len(children)} children to {element.name} element"
            )

        return node

    # Process the body content
    result = []
    root_elements = list(soup.body.children if soup.body else soup.children)
    print(f"[telegraph_api.py] Processing {len(root_elements)} root elements")

    for element in root_elements:
        if element.name or (element.string and element.string.strip()):
            processed = process_element(element)
            if processed:
                if isinstance(processed, list):
                    result.extend(processed)
                    print(
                        f"[telegraph_api.py] Added list of {len(processed)} elements to result"
                    )
                elif not isinstance(processed, str) or processed.strip():
                    result.append(processed)
                    if isinstance(processed, dict):
                        print(
                            f"[telegraph_api.py] Added {processed.get('tag', 'unknown')} element to result"
                        )
                    else:
                        print("[telegraph_api.py] Added text content to result")

    print(
        f"[telegraph_api.py] HTML to Node conversion complete: {len(result)} top-level nodes generated"
    )
    return result


# Utility function to post content to Telegraph
def post_to_telegraph(
    title: str, author_name: str, image_url: str, html_content: str, source_url: str
) -> Dict[str, str]:
    """
    Post content to Telegraph with image, content, and source link.
    Returns a dict with the Telegraph URL and path.
    """
    print(f"[telegraph_api.py] Preparing to post content to Telegraph: '{title}'")
    print(f"[telegraph_api.py] Author: {author_name}")

    try:
        telegraph = TelegraphAPI()
        print("[telegraph_api.py] Successfully initialized Telegraph API client")

        # Process HTML content into Telegraph format
        from datetime import datetime
        import pytz

        # Add time and source URL to the content
        timeZ_Dhaka = pytz.timezone("Asia/Dhaka")
        bd_time = datetime.now(timeZ_Dhaka)
        print(f"[telegraph_api.py] Current Bangladesh time: {bd_time}")

        # Calculate content length for logging
        content_length = len(html_content)
        print(
            f"[telegraph_api.py] Original content length: {content_length} characters"
        )

        # Prepare the full HTML content with image, article, and footer
        print(f"[telegraph_api.py] Adding image: {image_url}")
        full_html = f"""
        <img src="{image_url}"/>
        {html_content}
        <br/><br/>
        <a href="{source_url}">Go to Original Article</a>
        <p>Scraped at: {bd_time}</p>
        """

        print("[telegraph_api.py] Converting HTML to Telegraph node format")
        # Convert to Telegraph node format
        content = html_to_node(full_html)
        print(f"[telegraph_api.py] Generated {len(content)} content nodes")

        print(f"[telegraph_api.py] Creating Telegraph page with title: {title}")
        # Create the page on Telegraph
        result = telegraph.create_page(
            title=title, author_name=author_name, content=content
        )

        print(
            f"[telegraph_api.py] Successfully created Telegraph page: {result.get('url', '')}"
        )
        return {
            "url": result.get("url", ""),
            "path": result.get("path", ""),
            "title": result.get("title", ""),
        }
    except Exception as e:
        print(f"[telegraph_api.py] ERROR creating Telegraph page: {str(e)}")
        raise
