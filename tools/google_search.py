from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from tools.utils import VALID_COUNTRIES, VALID_LANGUAGES


class GoogleSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        query = tool_parameters.get("query", "")

        api_key = self.runtime.credentials["google_api_key"]
        cx_id = self.runtime.credentials["google_cx_id"]
        num = min(max(int(tool_parameters.get("num", 10)), 1), 10)

        optional_params: dict[str, str] = {}
        hl = tool_parameters.get("language_code") or tool_parameters.get("hl")
        if isinstance(hl, str) and VALID_LANGUAGES and hl in VALID_LANGUAGES:
            optional_params["hl"] = hl
        gl = tool_parameters.get("country_code") or tool_parameters.get("gl")
        if isinstance(gl, str) and VALID_COUNTRIES and gl in VALID_COUNTRIES:
            optional_params["gl"] = gl

        try:
            service = build("customsearch", "v1", developerKey=api_key)
            result = service.cse().list(q=query, cx=cx_id, num=num, **optional_params).execute()
            items = [
                {"title": item.get("title", ""), "url": item.get("link", ""), "snippet": item.get("snippet", "")}
                for item in result.get("items", [])
                if item.get("snippet")
            ]
            yield self.create_json_message(items)

        except HttpError as e:
            yield self.create_text_message(f"Google API error ({e.resp.status}): {e._get_reason()}")
        except Exception as e:
            yield self.create_text_message(f"Error: {e!s}")
