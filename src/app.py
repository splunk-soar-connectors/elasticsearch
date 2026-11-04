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
from collections.abc import Iterator

from pydantic import ConfigDict, model_validator
from soar_sdk.abstract import SOARClient
from soar_sdk.app import App
from soar_sdk.asset import AssetField, BaseAsset, FieldCategory
from soar_sdk.exceptions import ActionFailure
from soar_sdk.logging import getLogger
from soar_sdk.models.container import Container
from soar_sdk.params import OnPollParams


from .consts import (
    ELASTICSEARCH_CLUSTER_HEALTH,
    ELASTICSEARCH_ERROR_CONNECTIVITY_TEST,
    ELASTICSEARCH_ERROR_LEGACY_PARSER,
    ELASTICSEARCH_MESSAGE_CLUSTER_HEALTH,
    ELASTICSEARCH_ON_POLL_ERROR_MESSAGE,
    ELASTICSEARCH_SUCCESS_CONNECTIVITY_TEST,
)


class Asset(BaseAsset):
    model_config = ConfigDict(hide_input_in_errors=True)

    url: str = AssetField(
        description="Device URL including the port, e.g. https://myelastic.enterprise.com:9200",
        required=True,
    )
    verify_server_cert: bool = AssetField(
        description="Verify server certificate", default=True
    )
    username: str | None = AssetField(description="Username", default=None)
    password: str | None = AssetField(
        description="Password", default=None, sensitive=True
    )
    ingest_index: str | None = AssetField(
        description="Ingestion index", default=None, category=FieldCategory.INGEST
    )
    ingest_routing: str | None = AssetField(
        description="Ingestion routing", default=None, category=FieldCategory.INGEST
    )
    ingest_query: str | None = AssetField(
        description="Ingestion query", default=None, category=FieldCategory.INGEST
    )

    @model_validator(mode="before")
    @classmethod
    def reject_legacy_parser(cls, values):
        if isinstance(values, dict) and values.get("ingest_parser"):
            raise ValueError(ELASTICSEARCH_ERROR_LEGACY_PARSER)
        return values


app = App(
    name="Elasticsearch",
    app_type="siem",
    logo="logo_elastic.svg",
    logo_dark="logo_elastic_dark.svg",
    product_vendor="Elastic",
    product_name="Elasticsearch",
    publisher="Splunk",
    appid="fde8b9da-d38c-45c2-832a-1e1c543ed287",
    fips_compliant=True,
    asset_cls=Asset,
)
logger = getLogger()


@app.test_connectivity()
def test_connectivity(asset: Asset) -> None:
    """Validate the asset configuration for connectivity."""
    from .helper import request_json

    logger.progress(ELASTICSEARCH_MESSAGE_CLUSTER_HEALTH)
    try:
        request_json(asset, ELASTICSEARCH_CLUSTER_HEALTH)
    except ActionFailure:
        logger.info(ELASTICSEARCH_ERROR_CONNECTIVITY_TEST)
        raise
    logger.info(ELASTICSEARCH_SUCCESS_CONNECTIVITY_TEST)


@app.on_poll()
def on_poll(
    params: OnPollParams, soar: SOARClient, asset: Asset
) -> Iterator[Container]:
    """Run the configured query and ingest its hits using the bundled parser.

    The query controls time ranges and pagination, as in the legacy connector.
    """
    from .helper import search
    from .parser import ingest_parser

    if not asset.ingest_index or asset.ingest_query is None:
        raise ActionFailure(ELASTICSEARCH_ON_POLL_ERROR_MESSAGE)
    response = search(
        asset, asset.ingest_index, asset.ingest_query, asset.ingest_routing
    )
    records = ingest_parser(response)
    if params.is_manual_poll() and params.container_count:
        records = records[: params.container_count]
    for record in records:
        yield Container(**record["container"], artifacts=record["artifacts"])


from .actions import get_config, make_request, run_query  # noqa: F401
