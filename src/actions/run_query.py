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
from pydantic import SkipValidation
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from soar_sdk.params import Param, Params

from ..app import Asset, app
from ..consts import ELASTICSEARCH_JSON_TIMED_OUT
from ..helper import search


class RunQueryParams(Params):
    index: str = Param(
        description="Comma-separated list of indexes to query on",
        required=True,
        primary=True,
        cef_types=["elasticsearch index"],
    )
    routing: str | None = Param(
        description="Shards to query on (routing value)", default=None
    )
    query: str | None = Param(
        description="Query to run (in ElasticSearch language)",
        default=None,
        primary=True,
        cef_types=["elasticsearch query"],
    )


class ShardsOutput(ActionOutput):
    failed: int | None = None
    skipped: int | None = None
    successful: int | None = None
    total: int | None = None


class HitOutput(PermissiveActionOutput):
    id: str | None = OutputField(alias="_id")
    index: str | None = OutputField(alias="_index")
    score: float | None = OutputField(alias="_score")
    source: str | None = OutputField(alias="_source")
    fields: float | None = None


class TotalOutput(ActionOutput):
    relation: str | None = None
    value: int | None = None


class HitsOutput(PermissiveActionOutput):
    hits: list[HitOutput]
    max_score: float | None = None
    total: TotalOutput


class RunQueryOutput(PermissiveActionOutput):
    # Nested models describe legacy datapaths; retain API JSON without validating
    # or mutating arbitrary document payloads and optional nested response fields.
    shards: SkipValidation[ShardsOutput] = OutputField(alias="_shards")
    hits: SkipValidation[HitsOutput]
    took: int | None = None


class RunQuerySummary(ActionOutput):
    timed_out: bool
    total_hits: int


@app.action(
    action_type="investigate",
    read_only=True,
    summary_type=RunQuerySummary,
    render_as="json",
    verbose='The action executes the query on an Elasticsearch installation by doing a POST on the REST endpoint \'<b>base_url</b>/<b>index</b>/_search\' with the input <b>query</b> as the data, if specified. Please see the Elasticseach website for query format and documentation.<br>The <b>routing</b> parameter is appended as a parameter in the REST call if specified.<br>As an e.g. the following query returns only the <i>id</i> and <i>name</i> of all the items from the given <b>index</b><br>{ "query": { "match_all": {} }, "_source": ["id", "name"]}.',
)
def run_query(params: RunQueryParams, soar: SOARClient, asset: Asset) -> RunQueryOutput:
    """Run a search query on the Elasticsearch installation. Please escape any quotes that are part of the query string."""
    response = search(asset, params.index, params.query, params.routing)
    total = response.get("hits", {}).get("total", {})
    count = total.get("value", 0) if isinstance(total, dict) else total
    soar.set_summary(
        RunQuerySummary(
            total_hits=count,
            timed_out=response.get(ELASTICSEARCH_JSON_TIMED_OUT, False),
        )
    )
    # Preserve arbitrary _source, fields and aggregation payloads and their original
    # nested datapaths. The SDK's permissive output retains raw response JSON.
    return RunQueryOutput(**response)
