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

        if hl not in VALID_LANGUAGES:
            yield self.create_text_message(
                f"Invalid 'hl' parameter: {hl}. Please use a valid language code (e.g., en, es, fr)."
            )
            return

        if gl not in VALID_COUNTRIES:
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

            items = response.get("items", [])
            markdown_result = "\n\n"
            json_result = []
            for item in items:
                image_info = item.get("image", {})
                image_url = item.get("link", "")
                parsed = {
                    "title": item.get("title", ""),
                    "image": image_url,
                    "thumbnail": image_info.get("thumbnailLink", ""),
                    "url": image_info.get("contextLink", ""),
                    "height": image_info.get("height", ""),
                    "width": image_info.get("width", ""),
                    "source": item.get("displayLink", ""),
                }
                markdown_result += f"![{parsed['title']}]({image_url})"
                json_result.append(self.create_json_message(parsed))
            yield from [self.create_text_message(markdown_result)] + json_result

        except HttpError as e:
            yield self.create_text_message(f"Google API error ({e.resp.status}): {e._get_reason()}")
        except Exception as e:
            yield self.create_text_message(f"An error occurred while invoking the tool: {str(e)}.")
