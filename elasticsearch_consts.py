# File: elasticsearch_consts.py
# Copyright (c) 2016-2021 Splunk Inc.
#
# SPLUNK CONFIDENTIAL - Use or disclosure of this material in whole or in part
# without a valid written license from Splunk Inc. is PROHIBITED.
#
# --

ELASTICSEARCH_JSON_DEVICE_URL = "url"
ELASTICSEARCH_JSON_QUERY = "query"
ELASTICSEARCH_JSON_INDEX = "index"
ELASTICSEARCH_JSON_TYPE = "type"
ELASTICSEARCH_JSON_ROUTING = "routing"
ELASTICSEARCH_JSON_TOTAL_HITS = "total_hits"
ELASTICSEARCH_JSON_TIMED_OUT = "timed_out"

ELASTICSEARCH_ERR_CONNECTIVITY_TEST = "Test Connectivity Failed"
ELASTICSEARCH_SUCC_CONNECTIVITY_TEST = "Test Connectivity Passed"
ELASTICSEARCH_ERR_SERVER_CONNECTION = "Connection failed"
ELASTICSEARCH_ERR_FROM_SERVER = "API failed, Status code: {status}, Detail: {detail}"
ELASTICSEARCH_MSG_CLUSTER_HEALTH = "Querying cluster health to check connectivity"
ELASTICSEARCH_ERR_API_UNSUPPORTED_METHOD = "Unsupported method"
ELASTICSEARCH_USING_BASE_URL = "Using url: {base_url}"
ELASTICSEARCH_ERR_JSON_PARSE = "Unable to parse reply as a Json, raw string reply: '{raw_text}'"
