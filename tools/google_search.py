from collections.abc import Generator
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from loguru import logger

from tools.utils import to_refs, VALID_LANGUAGES, VALID_COUNTRIES, InstantSearchResponse


class GoogleSearchTool(Tool):
    @staticmethod
    def _set_params_language_code(params: dict, tool_parameters: dict):
        try:
            language_code = tool_parameters.get("language_code") or tool_parameters.get("hl")
            if (
                language_code
                and isinstance(language_code, str)
                and isinstance(VALID_LANGUAGES, set)
                and language_code in VALID_LANGUAGES
            ):
                params["hl"] = language_code
        except Exception as e:
            logger.warning(f"Failed to set language code parameter: {e}")

    @staticmethod
    def _set_params_country_code(params: dict, tool_parameters: dict):
        try:
            country_code = tool_parameters.get("country_code") or tool_parameters.get("gl")
            if (
                country_code
                and isinstance(country_code, str)
                and VALID_COUNTRIES
                and isinstance(VALID_COUNTRIES, set)
                and country_code in VALID_COUNTRIES
            ):
                params["gl"] = country_code
        except Exception as e:
            logger.warning(f"Failed to set country code parameter: {e}")

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        as_agent_tool = tool_parameters.get("as_agent_tool", False)
        query = tool_parameters.get("query", "")

        api_key = self.runtime.credentials["google_api_key"]
        cx_id = self.runtime.credentials["google_cx_id"]
        num = min(max(int(tool_parameters.get("num", 10)), 1), 10)

        optional_params: dict[str, str] = {}
        self._set_params_country_code(optional_params, tool_parameters)
        self._set_params_language_code(optional_params, tool_parameters)

        try:
            service = build("customsearch", "v1", developerKey=api_key)
            result = service.cse().list(q=query, cx=cx_id, num=num, **optional_params).execute()

            isr = InstantSearchResponse(refs=to_refs(result))

            if not as_agent_tool:
                yield self.create_json_message(json=isr.to_dify_json_message())
            else:
                yield self.create_text_message(text=isr.to_dify_text_message())

        except HttpError as e:
            yield self.create_text_message(f"Google API error ({e.resp.status}): {e._get_reason()}")
        except Exception as e:
            yield self.create_text_message(f"An error occurred while invoking the tool: {str(e)}.")
