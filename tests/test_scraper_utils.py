import unittest

from scraper_utils import iter_story_items, normalize_bbc_url


class TestScraperUtils(unittest.TestCase):
    def test_iter_story_items_skips_invalid(self):
        data = [
            {"items": [{"story": {"url": "https://example.com/1"}}, {"story": None}]},
            {"story": {"url": "https://example.com/2"}},
            {"items": [{"story": "invalid"}]},
        ]

        urls = [story.get("url") for story in iter_story_items(data)]

        self.assertEqual(urls, ["https://example.com/1", "https://example.com/2"])

    def test_normalize_bbc_url_filters_external(self):
        self.assertEqual(
            normalize_bbc_url("https://www.bbc.com/bengali", "/bengali/abc"),
            "https://www.bbc.com/bengali/abc",
        )
        self.assertIsNone(
            normalize_bbc_url(
                "https://www.bbc.com/bengali", "https://whatsapp.com/channel/123"
            ),
        )

    def test_iter_story_items_handles_nested(self):
        data = [
            {"items": [{"story": {"url": "https://example.com/1", "headline": "A"}}]},
            {"story": {"url": "https://example.com/2", "headline": "B"}},
        ]

        headlines = [story.get("headline") for story in iter_story_items(data)]

        self.assertEqual(headlines, ["A", "B"])


if __name__ == "__main__":
    unittest.main()
