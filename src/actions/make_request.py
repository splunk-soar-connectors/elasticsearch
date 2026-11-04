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
import json
from urllib.parse import parse_qsl

from soar_sdk.action_results import MakeRequestOutput
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import MakeRequestParams

from ..app import Asset, app
from ..consts import (
    ELASTICSEARCH_ERROR_HEADER_VALUES,
    ELASTICSEARCH_ERROR_INVALID_JSON,
    ELASTICSEARCH_ERROR_JSON_OBJECT,
)
from ..helper import request


def json_object(value, name):
    try:
        result = json.loads(value)
    except ValueError as exc:
        raise ActionFailure(ELASTICSEARCH_ERROR_INVALID_JSON.format(name=name)) from exc
    if not isinstance(result, dict):
        raise ActionFailure(ELASTICSEARCH_ERROR_JSON_OBJECT.format(name=name))
    if name == "headers" and any(
        not isinstance(value, str) for value in result.values()
    ):
        raise ActionFailure(ELASTICSEARCH_ERROR_HEADER_VALUES)
    return result


@app.make_request()
def make_request(params: MakeRequestParams, asset: Asset) -> MakeRequestOutput:
    """Make an authenticated request relative to the configured Elasticsearch URL."""
    headers = json_object(params.headers, "headers") if params.headers else None
    query = None
    if params.query_parameters:
        value = params.query_parameters
        query = (
            json_object(value, "query parameters")
            if value.lstrip().startswith(("{", "["))
            else parse_qsl(value.lstrip("?"), keep_blank_values=True)
        )
    response = request(
        asset,
        params.endpoint,
        method=params.http_method,
        headers=headers,
        params=query,
        body=params.body,
        timeout=params.timeout,
        verify=params.verify_ssl,
    )
    return MakeRequestOutput(
        status_code=response.status_code, response_body=response.text
    )
