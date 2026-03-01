import urllib.request
from typing import Any, Generator

import pymupdf
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from trafilatura import extract, fetch_url

_USER_AGENT = "Mozilla/5.0 (compatible; DifyBot/1.0)"
_MAX_PDF_BYTES = 10 * 1024 * 1024  # 10 MB
_TOP_K_PAGES = 5


def _extract_pdf(url: str, max_length: int, query: str) -> str | None:
    """Download a PDF (up to 10 MB) and extract relevant text content."""
    if not query:
        return None

    try:
        req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            content_length = resp.headers.get("Content-Length")
            if content_length and int(content_length) > _MAX_PDF_BYTES:
                return None
            pdf_bytes = resp.read(_MAX_PDF_BYTES + 1)
            if len(pdf_bytes) > _MAX_PDF_BYTES:
                return None

        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

        selected: list[tuple[int, str]] = []
        for page in doc:
            if page.search_for(query):
                text = page.get_text().strip()
                if text:
                    selected.append((page.number + 1, text))
                    if len(selected) >= _TOP_K_PAGES:
                        break

        doc.close()

        if not selected:
            return None

        parts = [f"--- Page {num} ---\n{text}" for num, text in selected]
        content = "\n\n".join(parts)

        if max_length and len(content) > max_length:
            content = content[:max_length] + "\n\n...(truncated)"
        return content
    except Exception:
        return None


class WebCrawlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        url = tool_parameters.get("url", "").strip()
        max_length = int(tool_parameters.get("max_length", 5000))
        query = str(tool_parameters.get("query", "") or "").strip()
        if not url:
            yield self.create_text_message("URL is required.")
            return

        try:
            # PDF URLs: download and parse directly
            if url.lower().endswith(".pdf"):
                content = _extract_pdf(url, max_length, query)
                if content:
                    yield self.create_text_message(content)
                else:
                    yield self.create_text_message(f"Failed to extract content from PDF: {url}")
                return

            # Standard HTML extraction
            html = fetch_url(url)
            if not html:
                yield self.create_text_message(f"Failed to fetch content from {url}")
                return

            content = extract(
                html,
                url=url,
                include_tables=True,
                deduplicate=True,
                favor_precision=True,
                with_metadata=True,
            )

            if not content:
                yield self.create_text_message(f"No main content could be extracted from {url}")
                return

            # Check if content contains any of the query words
            if query:
                content_lower = content.lower()
                query_words = query.lower().split()
                if not any(word in content_lower for word in query_words):
                    yield self.create_text_message(f"Page content not relevant to query: {url}")
                    return

            if max_length and len(content) > max_length:
                content = content[:max_length] + "\n\n...(truncated)"

            yield self.create_text_message(content)

        except Exception as e:
            yield self.create_text_message(f"Error crawling {url}: {e!s}")
