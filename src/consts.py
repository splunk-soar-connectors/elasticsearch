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
# Shared endpoints, response keys, and user-facing messages.
ELASTICSEARCH_JSON_ROUTING = "routing"
ELASTICSEARCH_JSON_TIMED_OUT = "timed_out"
ELASTICSEARCH_EMPTY_RESPONSE_STATUS_CODES = [200, 204]
ELASTICSEARCH_CLUSTER_HEALTH = "/_cluster/health"
ELASTICSEARCH_GET_INDEXES = "/_cat/indices"
ELASTICSEARCH_QUERY_SEARCH_WITH_INDEX = "/{0}/_search"
ELASTICSEARCH_DEFAULT_TIMEOUT = 60

ELASTICSEARCH_ERROR_CONNECTIVITY_TEST = "Test Connectivity Failed"
ELASTICSEARCH_SUCCESS_CONNECTIVITY_TEST = "Test Connectivity Passed"
ELASTICSEARCH_MESSAGE_CLUSTER_HEALTH = "Querying cluster health to check connectivity"
ELASTICSEARCH_ERROR_SERVER_MESSAGE = "Connection failed"
ELASTICSEARCH_ERROR_FROM_SERVER = "API failed, Status code: {status}, Detail: {detail}"
ELASTICSEARCH_ERROR_API_UNSUPPORTED_METHOD = "Unsupported HTTP method"
ELASTICSEARCH_ERROR_JSON_PARSE = (
    "Unable to parse reply as a Json, raw string reply: '{raw_text}'"
)
ELASTICSEARCH_ON_POLL_ERROR_MESSAGE = "Ingestion requires a configured index and query."
ELASTICSEARCH_ERROR_INVALID_ACTION_PARAM = (
    "Please provide a valid value in the '{key}' parameter"
)
ELASTICSEARCH_ERROR_INVALID_INDEX = "Invalid Elasticsearch index name: {index}"
ELASTICSEARCH_ERROR_QUERY_JSON = "Unable to load query json. Error: {error}"
ELASTICSEARCH_ERROR_RELATIVE_ENDPOINT = (
    "Endpoint must be relative to the configured Elasticsearch URL"
)
ELASTICSEARCH_ERROR_INVALID_TIMEOUT = "Timeout must be a positive integer"
ELASTICSEARCH_ERROR_EMPTY_RESPONSE = (
    "Status code: {status}. Empty response and no information in the header"
)
ELASTICSEARCH_ERROR_UNSUPPORTED_RESPONSE = "Can't process response from server. Status Code: {status} Response from server: {text}"
ELASTICSEARCH_ERROR_HTML_RESPONSE = (
    "Status Code: {status}. Response from server:\n{text}\n"
)
ELASTICSEARCH_ERROR_HTML_FALLBACK = (
    "Error occurred while connecting to the Elastic server"
)
ELASTICSEARCH_ERROR_INVALID_JSON = "Invalid JSON {name}"
ELASTICSEARCH_ERROR_JSON_OBJECT = "{name} must be a JSON object"
ELASTICSEARCH_ERROR_HEADER_VALUES = "Header values must be strings"
ELASTICSEARCH_ERROR_LEGACY_PARSER = "Custom ingestion parsers are no longer supported. Remove the legacy ingest_parser asset value before running this connector."
