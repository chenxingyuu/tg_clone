from typing import IO, Any, Dict, Mapping, Optional, Union
from urllib.parse import parse_qs

import httpx
from httpx import Response

from cores.log import LOG


def _log_response(response: Response):
    content_type = response.headers.get("content-type", "")
    if "json" in content_type:
        LOG.debug(f"HTTP response JSON: {response.json()}")
    elif "x-www-form-urlencoded" in content_type:
        parsed_data = parse_qs(response.text)
        LOG.debug(f"HTTP response parsed form data: {parsed_data}")
    else:
        LOG.debug(f"HTTP response content: {response.content}")


async def async_http_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    files: Optional[Mapping[str, Union[IO[bytes], bytes, str]]] = None,
    timeout: Optional[float] = None,
) -> Response:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method,
                url,
                headers=headers,
                params=params,
                json=json,
                files=files,
                data=data,
                timeout=timeout,
            )
            response.raise_for_status()
            _log_response(response)
            return response
        except httpx.HTTPError as e:
            LOG.exception(e)
