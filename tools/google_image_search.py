from typing import Any, Generator

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool

from tools.utils import VALID_COUNTRIES, VALID_LANGUAGES


class GoogleImageSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        hl = tool_parameters.get("hl", "en")
        gl = tool_parameters.get("gl", "us")
        max_results = min(int(tool_parameters.get("max_results", 3)), 10)
        img_size = tool_parameters.get("imgsz", "")

        if VALID_LANGUAGES is None or hl not in VALID_LANGUAGES:
            yield self.create_text_message(
                f"Invalid 'hl' parameter: {hl}. Please use a valid language code (e.g., en, es, fr)."
            )
            return

        if VALID_COUNTRIES is None or gl not in VALID_COUNTRIES:
            yield self.create_text_message(
                f"Invalid 'gl' parameter: {gl}. Please use a valid country code (e.g., us, uk, fr)."
            )
            return

        api_key = self.runtime.credentials["google_api_key"]
        cx_id = self.runtime.credentials["google_cx_id"]

        optional_params: dict[str, Any] = {}
        if img_size:
            optional_params["imgSize"] = img_size

        try:
            service = build("customsearch", "v1", developerKey=api_key)
            response = (
                service.cse()
                .list(
                    q=tool_parameters["query"],
                    cx=cx_id,
                    searchType="image",
                    gl=gl,
                    hl=hl,
                    num=max_results,
                    **optional_params,
                )
                .execute()
            )

            yield self.create_json_message(response)

        except HttpError as e:
            yield self.create_text_message(f"Google API error ({e.resp.status}): {e._get_reason()}")
        except Exception as e:
            yield self.create_text_message(f"An error occurred while invoking the tool: {str(e)}.")
