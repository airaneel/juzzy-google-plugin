from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class GoogleProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            api_key = credentials["google_api_key"]
            cx_id = credentials["google_cx_id"]
            service = build("customsearch", "v1", developerKey=api_key)
            service.cse().list(q="test", cx=cx_id, num=1).execute()
        except HttpError as e:
            raise ToolProviderCredentialValidationError(
                f"Google API error: {e.resp.status} - {e._get_reason()}"
            ) from e
        except KeyError as e:
            raise ToolProviderCredentialValidationError(f"Missing credential: {str(e)}") from e
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e)) from e
