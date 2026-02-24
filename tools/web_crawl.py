import json
from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from trafilatura import fetch_url, extract


class WebCrawlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        url = tool_parameters.get("url", "").strip()
        if not url:
            yield self.create_text_message("URL is required.")
            return

        try:
            html = fetch_url(url)
            if not html:
                yield self.create_text_message(f"Failed to fetch content from {url}")
                return

            # Extract metadata as JSON
            meta_json = extract(html, output_format="json", with_metadata=True)
            meta = json.loads(meta_json) if meta_json else {}

            # Extract clean markdown content
            content = extract(
                html,
                output_format="markdown",
                include_links=True,
                include_tables=True,
                include_images=False,
                include_formatting=True,
                deduplicate=True,
                favor_precision=True,
                with_metadata=False,
            )

            if not content:
                yield self.create_text_message(f"No main content could be extracted from {url}")
                return

            title = meta.get("title", "")
            author = meta.get("author", "")
            date = meta.get("date", "")
            sitename = meta.get("sitename", "")
            description = meta.get("description", "")

            header_parts = []
            if title:
                header_parts.append(f"# {title}")
            meta_parts = []
            if sitename:
                meta_parts.append(f"Source: {sitename}")
            if author:
                meta_parts.append(f"Author: {author}")
            if date:
                meta_parts.append(f"Date: {date}")
            if meta_parts:
                header_parts.append(" | ".join(meta_parts))
            if description:
                header_parts.append(f"> {description}")

            text_output = "\n\n".join(header_parts + [content]) if header_parts else content

            yield self.create_text_message(text_output)
            yield self.create_json_message(
                {
                    "url": url,
                    "title": title,
                    "author": author,
                    "date": date,
                    "sitename": sitename,
                    "description": description,
                    "content": content,
                }
            )

        except Exception as e:
            yield self.create_text_message(f"Error crawling {url}: {str(e)}")
