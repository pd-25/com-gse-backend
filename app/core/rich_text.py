from html import escape, unescape
from html.parser import HTMLParser
import re
from urllib.parse import urlparse


ALLOWED_TAGS = {
    "p",
    "br",
    "h2",
    "h3",
    "h4",
    "strong",
    "em",
    "u",
    "blockquote",
    "ul",
    "ol",
    "li",
    "a",
}
VOID_TAGS = {"br"}
SUPPRESSED_TAGS = {"script", "style", "iframe", "object", "embed"}


def _safe_url(value: str) -> bool:
    value = value.strip()
    if not value:
        return False
    parsed = urlparse(value)
    return not parsed.scheme or parsed.scheme.lower() in {"http", "https", "mailto"}


class _RichTextSanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.suppressed_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in SUPPRESSED_TAGS:
            self.suppressed_depth += 1
            return
        if self.suppressed_depth or tag not in ALLOWED_TAGS:
            return

        safe_attrs: list[tuple[str, str]] = []
        if tag == "a":
            values = {name.lower(): value or "" for name, value in attrs}
            href = values.get("href", "")
            if _safe_url(href):
                safe_attrs.append(("href", href.strip()))
            title = values.get("title", "").strip()
            if title:
                safe_attrs.append(("title", title))
            if values.get("target") == "_blank":
                safe_attrs.extend(
                    [("target", "_blank"), ("rel", "noopener noreferrer")]
                )

        rendered_attrs = "".join(
            f' {name}="{escape(value, quote=True)}"' for name, value in safe_attrs
        )
        self.parts.append(f"<{tag}{rendered_attrs}>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in SUPPRESSED_TAGS:
            self.suppressed_depth = max(0, self.suppressed_depth - 1)
            return
        if not self.suppressed_depth and tag in ALLOWED_TAGS and tag not in VOID_TAGS:
            self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if not self.suppressed_depth:
            self.parts.append(escape(data))


def sanitize_rich_text(value: str | None) -> str | None:
    if value is None:
        return None
    sanitizer = _RichTextSanitizer()
    sanitizer.feed(value.strip())
    sanitizer.close()
    cleaned = "".join(sanitizer.parts).strip()
    visible_text = unescape(re.sub(r"<[^>]+>", "", cleaned)).strip()
    return cleaned if visible_text else None
