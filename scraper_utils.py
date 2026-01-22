"""
Shared utilities for all scrapers in the newspaper-bot project.
Centralizes common patterns: HTTP requests, URL handling, file I/O.
"""

import codecs
import os
from typing import Dict, Iterable, Iterator, List, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from curl_cffi import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "bn,en;q=0.9",
}

BBC_ALLOWED_DOMAINS = ("bbc.com", "bbc.co.uk")

# ---------------------------------------------------------------------------
# HTTP Utilities
# ---------------------------------------------------------------------------


def get_html(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
    impersonate: str = "chrome110",
) -> BeautifulSoup:
    """
    Fetch a URL and return parsed BeautifulSoup object.
    Uses curl_cffi with browser impersonation to bypass bot protection.
    """
    response = requests.get(
        url,
        headers=headers or DEFAULT_HEADERS,
        impersonate=impersonate,
        timeout=timeout,
    )
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def fetch_url(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
    impersonate: str = "chrome110",
    verify: bool = True,
) -> requests.Response:
    """
    Fetch a URL and return the raw response object.
    Useful when you need access to response content, headers, etc.
    """
    response = requests.get(
        url,
        headers=headers or DEFAULT_HEADERS,
        impersonate=impersonate,
        timeout=timeout,
        verify=verify,
    )
    response.raise_for_status()
    return response


# ---------------------------------------------------------------------------
# URL Normalization
# ---------------------------------------------------------------------------


def normalize_bbc_url(base_url: str, href: Optional[str]) -> Optional[str]:
    """
    Normalize a BBC URL using urljoin and filter out external links.
    Returns None if href is empty or points to a non-BBC domain.
    """
    if not href:
        return None
    normalized = urljoin(base_url, href)
    hostname = urlparse(normalized).hostname or ""
    if not any(hostname.endswith(domain) for domain in BBC_ALLOWED_DOMAINS):
        return None
    return normalized.rstrip("/")


# ---------------------------------------------------------------------------
# Prothom Alo JSON Parsing
# ---------------------------------------------------------------------------


def iter_story_items(collection_items: Iterable[Dict]) -> Iterator[Dict]:
    """
    Safely iterate over Prothom Alo collection items, yielding story dicts.
    Handles nested structures and skips items with null/missing stories.
    """
    for block in collection_items or []:
        if not isinstance(block, dict):
            continue
        story = block.get("story")
        if isinstance(story, dict):
            yield story
        for item in block.get("items", []) or []:
            if not isinstance(item, dict):
                continue
            story = item.get("story")
            if isinstance(story, dict):
                yield story


# ---------------------------------------------------------------------------
# File I/O Utilities
# ---------------------------------------------------------------------------


def load_urls_from_file(file_path: str) -> List[str]:
    """
    Load URLs from a file, one per line.
    Handles FileNotFoundError and UnicodeDecodeError gracefully.
    """
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except UnicodeDecodeError:
        # Fallback for files with mixed encodings
        try:
            with codecs.open(file_path, "r", "utf-8", errors="ignore") as f:
                return [line.strip() for line in f if line.strip()]
        except Exception:
            return []
    except Exception:
        return []


def save_urls_to_file(file_path: str, urls: List[str], mode: str = "w") -> None:
    """
    Save URLs to a file, one per line.
    mode='w' overwrites, mode='a' appends.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, mode, encoding="utf-8") as f:
        for url in urls:
            f.write(f"{url}\n")


def append_urls_to_file(file_path: str, urls: List[str]) -> None:
    """Append URLs to a file."""
    save_urls_to_file(file_path, urls, mode="a")


def trim_url_file(
    file_path: str, max_urls: int = 300, trim_count: int = 60
) -> List[str]:
    """
    If URL file exceeds max_urls, remove the oldest trim_count entries.
    Returns the current list of URLs (after trimming if applicable).
    """
    urls = load_urls_from_file(file_path)
    if len(urls) > max_urls:
        urls = urls[trim_count:]
        save_urls_to_file(file_path, urls)
    return urls
