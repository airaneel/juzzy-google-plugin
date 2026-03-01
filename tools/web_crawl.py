from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from trafilatura import extract, fetch_url


class WebCrawlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        url = tool_parameters.get("url", "").strip()
        max_length = int(tool_parameters.get("max_length", 5000))
        if not url:
            yield self.create_text_message("URL is required.")
            return

        try:
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
