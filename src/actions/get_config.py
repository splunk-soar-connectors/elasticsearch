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
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.params import Params

from ..app import Asset, app
from ..consts import ELASTICSEARCH_GET_INDEXES
from ..helper import request_json


class GetConfigOutput(ActionOutput):
    index: str | None = OutputField(
        column_name="Index", cef_types=["elasticsearch index"]
    )
    health: str | None = OutputField(column_name="Health")
    status: str | None = OutputField(column_name="Status")
    document_count: str | None = OutputField(column_name="Document Count")
    store_size: str | None = OutputField(column_name="Store Size")


class GetConfigSummary(ActionOutput):
    total_indices: int


@app.action(
    action_type="investigate",
    read_only=True,
    summary_type=GetConfigSummary,
    render_as="table",
)
def get_config(params: Params, soar: SOARClient, asset: Asset) -> list[GetConfigOutput]:
    """Returns the list of indices and their information currently configured on the ElasticSearch instance."""
    response = request_json(asset, ELASTICSEARCH_GET_INDEXES)
    soar.set_summary(GetConfigSummary(total_indices=len(response)))
    return [
        GetConfigOutput(
            index=item.get("index"),
            health=item.get("health"),
            status=item.get("status"),
            document_count=item.get("docs.count"),
            store_size=item.get("store.size"),
        )
        for item in response
    ]
