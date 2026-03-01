import io
import urllib.request
from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from trafilatura import extract, fetch_url

_USER_AGENT = "Mozilla/5.0 (compatible; DifyBot/1.0)"


def _extract_pdf(url: str, max_length: int) -> str | None:
    """Download a PDF and extract its text content."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            pdf_bytes = resp.read()

        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages: list[str] = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())

        content = "\n\n".join(pages)
        if not content:
            return None

        if max_length and len(content) > max_length:
            content = content[:max_length] + "\n\n...(truncated)"
        return content
    except Exception:
        return None


class WebCrawlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        url = tool_parameters.get("url", "").strip()
        max_length = int(tool_parameters.get("max_length", 5000))
        if not url:
            yield self.create_text_message("URL is required.")
            return

        try:
            # PDF URLs: download and parse directly
            if url.lower().endswith(".pdf"):
                content = _extract_pdf(url, max_length)
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

            if max_length and len(content) > max_length:
                content = content[:max_length] + "\n\n...(truncated)"

            yield self.create_text_message(content)

        except Exception as e:
            yield self.create_text_message(f"Error crawling {url}: {e!s}")
