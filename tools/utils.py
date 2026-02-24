import json
from pathlib import Path
from typing import Any, Set, List
from urllib.parse import urlparse

from loguru import logger
from pydantic import BaseModel, Field

PROJECT_PATH = Path(__file__).parent

TOOL_INVOKE_TPL = """
Here are the search results in XML format:

```xml
<search_results>
{context}
</search_results>
```
"""

TOOL_INVOKE_SEGMENT_TPL = """
<search_result index="{i}">
  <title>{title}</title>
  <url>{url}</url>
  <source>{source}</source>
  <snippet>
    {snippet}
  </snippet>
</search_result>
"""


class SearchRef(BaseModel):
    title: str | None = ""
    url: str | None = ""
    content: str | None = ""
    site_name: str | None = ""

    def model_post_init(self, context: Any, /) -> None:
        if not self.site_name and self.url:
            try:
                u = urlparse(self.url)
                self.site_name = u.netloc
            except Exception as e:
                logger.warning(f"Failed to parse URL '{self.url}': {e}")


class InstantSearchResponse(BaseModel):
    refs: List[SearchRef] = Field(default_factory=list)
    webpage_context: str = ""
    total: int = 0

    def model_post_init(self, context: Any, /) -> None:
        self.total = len(self.refs)
        self.webpage_context = self.to_webpage_context()

    def to_webpage_context(self) -> str:
        if not self.refs:
            return ""

        webpage_segments = [
            TOOL_INVOKE_SEGMENT_TPL.format(
                i=i + 1, title=ref.title, url=ref.url, source=ref.site_name, snippet=ref.content
            ).strip()
            for i, ref in enumerate(self.refs)
        ]
        search_results_xml = TOOL_INVOKE_TPL.format(context="\n".join(webpage_segments))
        return search_results_xml

    def to_dify_json_message(self) -> dict:
        if not self.refs:
            return {"search_results": [], "description": "No search results found"}
        return {"search_results": [ref.model_dump(mode="json") for ref in self.refs]}

    def to_dify_text_message(self) -> str:
        return self.webpage_context


def load_valid_countries(filepath: Path) -> set | None:
    try:
        if countries := json.loads(filepath.read_text(encoding="utf8")):
            return {country["country_code"] for country in countries}
    except Exception as e:
        logger.error(f"Failed to load valid countries from '{filepath}': {e}")
    return None


def load_valid_languages(filepath: Path) -> set | None:
    try:
        if languages := json.loads(filepath.read_text(encoding="utf8")):
            return {language["language_code"] for language in languages}
    except Exception as e:
        logger.error(f"Failed to load valid languages from '{filepath}': {e}")
    return None


def to_refs(response: dict) -> List[SearchRef]:
    """Parse Google Custom Search API response items into SearchRef list."""
    refs = []
    for item in response.get("items", []):
        snippet = item.get("snippet", "")
        if not snippet:
            continue
        refs.append(
            SearchRef(
                url=item.get("link", ""),
                title=item.get("title", ""),
                content=snippet,
                site_name=item.get("displayLink", ""),
            )
        )
    return refs


VALID_COUNTRIES: Set[str] | None = load_valid_countries(
    PROJECT_PATH.joinpath("google-countries.json")
)
VALID_LANGUAGES: Set[str] | None = load_valid_languages(
    PROJECT_PATH.joinpath("google-languages.json")
)
