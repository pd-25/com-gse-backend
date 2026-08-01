import unittest

from app.core.rich_text import sanitize_rich_text


class RichTextSanitizerTests(unittest.TestCase):
    def test_keeps_supported_formatting(self):
        value = '<h2>Details</h2><p><strong>Fresh</strong> produce</p><ul><li>Grade A</li></ul>'
        self.assertEqual(sanitize_rich_text(value), value)

    def test_removes_scripts_and_event_handlers(self):
        value = '<p onclick="alert(1)">Safe</p><script>alert(2)</script>'
        self.assertEqual(sanitize_rich_text(value), "<p>Safe</p>")

    def test_rejects_unsafe_links(self):
        value = '<p><a href="javascript:alert(1)">Open</a></p>'
        self.assertEqual(sanitize_rich_text(value), "<p><a>Open</a></p>")

    def test_secures_new_tab_links(self):
        value = '<a href="https://example.com" target="_blank">Example</a>'
        self.assertEqual(
            sanitize_rich_text(value),
            '<a href="https://example.com" target="_blank" rel="noopener noreferrer">Example</a>',
        )

    def test_normalizes_empty_editor_content(self):
        self.assertIsNone(sanitize_rich_text("<p><br></p>"))


if __name__ == "__main__":
    unittest.main()
