#
# Copyright (c) 2016-2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.
"""Shared authenticated HTTP transport and Elasticsearch query validation."""

import json
from urllib.parse import quote, urlsplit

from soar_sdk.auth import BasicAuth
from soar_sdk.exceptions import ActionFailure

from .consts import (
    ELASTICSEARCH_DEFAULT_TIMEOUT,
    ELASTICSEARCH_EMPTY_RESPONSE_STATUS_CODES,
    ELASTICSEARCH_ERROR_API_UNSUPPORTED_METHOD,
    ELASTICSEARCH_ERROR_EMPTY_RESPONSE,
    ELASTICSEARCH_ERROR_FROM_SERVER,
    ELASTICSEARCH_ERROR_HTML_FALLBACK,
    ELASTICSEARCH_ERROR_HTML_RESPONSE,
    ELASTICSEARCH_ERROR_INVALID_ACTION_PARAM,
    ELASTICSEARCH_ERROR_INVALID_INDEX,
    ELASTICSEARCH_ERROR_INVALID_TIMEOUT,
    ELASTICSEARCH_ERROR_JSON_PARSE,
    ELASTICSEARCH_ERROR_QUERY_JSON,
    ELASTICSEARCH_ERROR_RELATIVE_ENDPOINT,
    ELASTICSEARCH_ERROR_SERVER_MESSAGE,
    ELASTICSEARCH_ERROR_UNSUPPORTED_RESPONSE,
    ELASTICSEARCH_JSON_ROUTING,
    ELASTICSEARCH_QUERY_SEARCH_WITH_INDEX,
)


def request(
    asset,
    endpoint,
    *,
    method="GET",
    headers=None,
    params=None,
    body=None,
    json_body=None,
    timeout=None,
    verify=None,
    follow_redirects=False,
):
    import httpx

    try:
        parts = urlsplit(endpoint)
    except ValueError as exc:
        raise ActionFailure(ELASTICSEARCH_ERROR_RELATIVE_ENDPOINT) from exc
    if parts.scheme or parts.netloc or parts.fragment or "\\" in endpoint:
        raise ActionFailure(ELASTICSEARCH_ERROR_RELATIVE_ENDPOINT)
    if method.upper() not in {
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "HEAD",
        "OPTIONS",
    }:
        raise ActionFailure(ELASTICSEARCH_ERROR_API_UNSUPPORTED_METHOD)
    if timeout is not None and timeout <= 0:
        raise ActionFailure(ELASTICSEARCH_ERROR_INVALID_TIMEOUT)
    auth = (
        BasicAuth(asset.username, asset.password)
        if asset.username and asset.password
        else None
    )
    request_headers = {"Accept": "application/json", "Content-Type": "application/json"}
    request_headers.update(headers or {})
    try:
        with httpx.Client(
            auth=auth,
            verify=asset.verify_server_cert if verify is None else verify,
            timeout=timeout or ELASTICSEARCH_DEFAULT_TIMEOUT,
            follow_redirects=follow_redirects,
        ) as client:
            return client.request(
                method,
                f"{asset.url.rstrip('/')}/{endpoint.lstrip('/')}",
                headers=request_headers,
                params=params,
                content=body,
                json=json_body,
            )
    except (httpx.RequestError, httpx.InvalidURL) as exc:
        raise ActionFailure(
            f"{ELASTICSEARCH_ERROR_SERVER_MESSAGE}. Error Message: {exc}"
        ) from exc


def request_json(asset, endpoint, **kwargs):
    response = request(asset, endpoint, follow_redirects=True, **kwargs)
    content_type = response.headers.get("Content-Type", "")
    if "json" in content_type:
        try:
            data = response.json() if response.text else {}
        except ValueError as exc:
            raise ActionFailure(
                ELASTICSEARCH_ERROR_JSON_PARSE.format(raw_text=response.text)
            ) from exc
        if 200 <= response.status_code < 300:
            return data
        details = json.dumps(data).replace("{", "").replace("}", "")
        raise ActionFailure(
            ELASTICSEARCH_ERROR_FROM_SERVER.format(
                status=response.status_code, detail=details
            )
        )
    if "html" in content_type:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(response.text, "html.parser")
        for element in soup(["script", "style", "footer", "nav"]):
            element.extract()
        text = "\n".join(
            line.strip() for line in soup.text.splitlines() if line.strip()
        )
        message = ELASTICSEARCH_ERROR_HTML_RESPONSE.format(
            status=response.status_code, text=text
        )
        raise ActionFailure(
            message if len(message) <= 500 else ELASTICSEARCH_ERROR_HTML_FALLBACK
        )
    if not response.text:
        if response.status_code in ELASTICSEARCH_EMPTY_RESPONSE_STATUS_CODES:
            return {}
        raise ActionFailure(
            ELASTICSEARCH_ERROR_EMPTY_RESPONSE.format(status=response.status_code)
        )
    raise ActionFailure(
        ELASTICSEARCH_ERROR_UNSUPPORTED_RESPONSE.format(
            status=response.status_code, text=response.text
        )
    )


def search(asset, index, query=None, routing=None):
    query_json = None
    if query:
        try:
            query_json = json.loads(query)
        except ValueError as exc:
            raise ActionFailure(
                ELASTICSEARCH_ERROR_QUERY_JSON.format(error=exc)
            ) from exc
    indexes = list(
        dict.fromkeys(item.strip() for item in index.split(",") if item.strip())
    )
    if not indexes:
        raise ActionFailure(
            ELASTICSEARCH_ERROR_INVALID_ACTION_PARAM.format(key="index")
        )
    for item in indexes:
        if item in {"*", "_all"}:
            continue
        if (
            item != item.lower()
            or item[0] in "-_+"
            or any(char in frozenset('/\\?"<>| #') for char in item)
        ):
            raise ActionFailure(ELASTICSEARCH_ERROR_INVALID_INDEX.format(index=item))
    endpoint = ELASTICSEARCH_QUERY_SEARCH_WITH_INDEX.format(
        quote(",".join(indexes), safe=",*")
    )
    # Preserve the legacy routing encoding for existing assets and playbooks.
    params = {ELASTICSEARCH_JSON_ROUTING: quote(routing)} if routing else None
    return request_json(
        asset, endpoint, method="POST", json_body=query_json, params=params
    )
