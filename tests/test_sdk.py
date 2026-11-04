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
from unittest.mock import Mock

import httpx
import pytest
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import MakeRequestParams, OnPollParams, Params

from src.app import Asset, on_poll, test_connectivity as connectivity
from src.actions.get_config import get_config
from src.actions.run_query import RunQueryParams, run_query
from src.actions.make_request import make_request
from src import helper


@pytest.fixture
def asset():
    return Asset(
        url="https://elastic.example:9200",
        username="user",
        password="secret",  # pragma: allowlist secret
    )


@pytest.mark.parametrize(
    "index", ["", " , ", "UPPER", "../secret", "bad/name", "-bad", "bad#name"]
)
def test_invalid_indexes(asset, index):
    with pytest.raises(ActionFailure, match=r".+"):
        helper.search(asset, index)


def test_query_encoding_and_summary(asset, monkeypatch):
    payload = {
        "_shards": {"total": 1},
        "hits": {
            "total": {"value": 2, "relation": "eq"},
            "hits": [{"_id": "1", "_source": {"nested": [1, 2]}, "fields": {"a": [1]}}],
        },
        "aggregations": {"count": 2},
        "timed_out": False,
    }
    call = Mock(return_value=payload)
    monkeypatch.setattr(helper, "request_json", call)
    soar = Mock()
    result = run_query.__wrapped__(
        RunQueryParams(index="logs,logs,*", query='{"size":2}', routing="a b"),
        soar,
        asset,
    )
    assert result.model_dump() == payload
    soar.set_summary.assert_called_once()
    assert soar.set_summary.call_args.args[0].total_hits == 2
    assert call.call_args.args[1] == "/logs,*/_search"
    assert call.call_args.kwargs == {
        "method": "POST",
        "json_body": {"size": 2},
        "params": {"routing": "a%20b"},
    }


def test_bad_query(asset):
    with pytest.raises(ActionFailure, match="Unable to load query json"):
        helper.search(asset, "logs", "{")


@pytest.mark.parametrize(
    "status,headers,text,expected",
    [
        (200, {"Content-Type": "application/json"}, '{"ok": true}', {"ok": True}),
        (204, {}, "", {}),
        (201, {"Content-Type": "application/json"}, "", {}),
    ],
)
def test_response_success(asset, monkeypatch, status, headers, text, expected):
    monkeypatch.setattr(
        helper,
        "request",
        Mock(return_value=httpx.Response(status, headers=headers, text=text)),
    )
    assert helper.request_json(asset, "/") == expected


@pytest.mark.parametrize(
    "status,content_type,text,message",
    [
        (400, "application/json", '{"error":"bad"}', "API failed"),
        (200, "application/json", "{", "Unable to parse"),
        (502, "text/html", "<script>secret()</script><p>Proxy down</p>", "Proxy down"),
        (500, "text/plain", "", "Empty response"),
        (200, "text/plain", "hello", "Can't process"),
    ],
)
def test_response_errors(asset, monkeypatch, status, content_type, text, message):
    monkeypatch.setattr(
        helper,
        "request",
        Mock(
            return_value=httpx.Response(
                status, headers={"Content-Type": content_type}, text=text
            )
        ),
    )
    with pytest.raises(ActionFailure, match=message):
        helper.request_json(asset, "/")


def test_config(asset, monkeypatch):
    from src.actions import get_config as module

    monkeypatch.setattr(
        module,
        "request_json",
        Mock(return_value=[{"index": "logs", "docs.count": "2", "store.size": "3kb"}]),
    )
    soar = Mock()
    result = get_config.__wrapped__(Params(), soar, asset)
    assert result[0].document_count == "2"
    assert result[0].store_size == "3kb"
    assert soar.set_summary.call_args.args[0].total_indices == 1


def test_ingestion(asset, monkeypatch):
    asset.ingest_index = "logs"
    asset.ingest_query = "{}"
    monkeypatch.setattr(
        helper,
        "search",
        Mock(
            return_value={
                "hits": {
                    "hits": [
                        {"_id": str(i), "_index": "logs", "_source": {"value": i}}
                        for i in range(3)
                    ]
                }
            }
        ),
    )
    results = list(on_poll.__wrapped__(OnPollParams(container_count=1), Mock(), asset))
    assert len(results) == 1
    assert results[0].source_data_identifier == "0"
    assert results[0].artifacts[0]["cef"] == {"value": 0}
    assert results[0].artifacts[0]["run_automation"] is True
    assert len(list(on_poll.__wrapped__(OnPollParams(), Mock(), asset))) == 3


def test_ingestion_missing_config(asset):
    with pytest.raises(ActionFailure, match="configured index and query"):
        list(on_poll.__wrapped__(OnPollParams(), Mock(), asset))


def test_connectivity(asset, monkeypatch):
    call = Mock(return_value={})
    monkeypatch.setattr(helper, "request_json", call)
    connectivity.__wrapped__(asset)
    call.assert_called_once_with(asset, "/_cluster/health")


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://evil.example",
        "//evil.example",
        "http://evil.example",
        "\\evil",
        "/x#fragment",
    ],
)
def test_request_rejects_external_urls(asset, endpoint):
    with pytest.raises(ActionFailure, match="relative"):
        helper.request(asset, endpoint)


def test_make_request_transport(asset, monkeypatch):
    client = Mock()
    client.__enter__ = Mock(return_value=client)
    client.__exit__ = Mock(return_value=False)
    client.request.return_value = httpx.Response(404, text='{"error":"missing"}')
    factory = Mock(return_value=client)
    monkeypatch.setattr(httpx, "Client", factory)
    params = MakeRequestParams(
        http_method="POST",
        endpoint="/_search",
        body='{"size":1}',
        headers='{"X-Test":"yes"}',
        query_parameters="?a=1&a=2",
        timeout=12,
        verify_ssl=False,
    )
    output = make_request.__wrapped__(params, asset)
    assert output.status_code == 404
    assert json.loads(output.response_body) == {"error": "missing"}
    assert factory.call_args.kwargs["verify"] is False
    assert factory.call_args.kwargs["timeout"] == 12
    args, kwargs = client.request.call_args
    assert args == ("POST", "https://elastic.example:9200/_search")
    assert kwargs["content"] == '{"size":1}'
    assert kwargs["params"] == [("a", "1"), ("a", "2")]
    assert kwargs["headers"]["X-Test"] == "yes"
    request = httpx.Request("GET", "https://elastic.example")
    assert (
        next(factory.call_args.kwargs["auth"].auth_flow(request))
        .headers["Authorization"]
        .startswith("Basic ")
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"headers": "{"},
        {"headers": "[]"},
        {"headers": '{"X-Test": 1}'},
        {"headers": '{"X-Test": null}'},
        {"query_parameters": "[]"},
        {"timeout": -1},
    ],
)
def test_make_request_invalid_inputs(asset, kwargs):
    with pytest.raises(ActionFailure, match=r".+"):
        make_request.__wrapped__(
            MakeRequestParams(http_method="GET", endpoint="/", **kwargs), asset
        )


def test_legacy_parser_rejected():
    with pytest.raises(ValueError, match="Custom ingestion parsers"):
        Asset(url="https://elastic.example", ingest_parser="legacy.py")


def test_config_table_columns():
    from src.app import app
    from src.actions.get_config import GetConfigOutput

    action = next(
        a
        for a in app.actions_manager.get_actions_meta_list()
        if a.action == "get config"
    )
    assert action.render_as == "table"
    assert action.view_handler is None
    columns = [
        field for field in GetConfigOutput._to_json_schema() if field.get("column_name")
    ]
    assert [field["column_name"] for field in columns] == [
        "Index",
        "Health",
        "Status",
        "Document Count",
        "Store Size",
    ]
    assert [field["column_order"] for field in columns] == sorted(
        field["column_order"] for field in columns
    )


def test_manifest_metadata_preserved():
    from src.app import app

    actions = {
        action.action: action for action in app.actions_manager.get_actions_meta_list()
    }
    assert set(actions) == {
        "get config",
        "run query",
        "test connectivity",
        "on poll",
        "make request",
    }
    assert actions["run query"].read_only is True
    assert actions["run query"].type == "investigate"
    output = {
        item["data_path"] for item in actions["run query"].output._to_json_schema()
    }
    assert "action_result.data.*._shards.total" in output
    assert "action_result.data.*.hits.hits.*._source" in output
    assert "total_hits" in actions["run query"].summary_type.model_fields
    assert Asset.to_json_schema()["password"]["data_type"] == "password"


@pytest.mark.parametrize("container_count", [None, 1])
def test_poll_accepts_explicit_blank_query(asset, monkeypatch, container_count):
    asset.ingest_index = "logs"
    asset.ingest_query = ""
    call = Mock(
        return_value={
            "hits": {
                "hits": [
                    {"_id": "1", "_index": "logs", "_source": {"message": "event"}}
                ]
            }
        }
    )
    monkeypatch.setattr(helper, "request_json", call)
    records = list(
        on_poll.__wrapped__(
            OnPollParams(container_count=container_count), Mock(), asset
        )
    )
    assert len(records) == 1
    assert records[0].artifacts[0]["cef"] == {"message": "event"}
    assert call.call_args.args[1] == "/logs/_search"
    assert call.call_args.kwargs["json_body"] is None


@pytest.fixture
def mock_http(monkeypatch):
    original_client = httpx.Client

    def install(handler):
        monkeypatch.setattr(
            httpx,
            "Client",
            lambda **kwargs: original_client(
                transport=httpx.MockTransport(handler), **kwargs
            ),
        )

    return install


@pytest.mark.parametrize("status_code,method", [(302, "GET"), (307, "POST")])
def test_legacy_requests_follow_redirects(asset, mock_http, status_code, method):
    seen = []

    def route(request):
        seen.append(request)
        if request.url.path == "/initial":
            return httpx.Response(status_code, headers={"Location": "/target"}, json={})
        return httpx.Response(200, json={"status": "green"})

    mock_http(route)
    assert helper.request_json(
        asset, "/initial", method=method, json_body={"size": 1}
    ) == {"status": "green"}
    assert [request.url.path for request in seen] == ["/initial", "/target"]
    assert seen[1].method == method
    assert seen[1].headers["Authorization"] == seen[0].headers["Authorization"]
    if method == "POST":
        assert seen[1].content == seen[0].content


def test_redirect_target_error_fails_connectivity(asset, mock_http):
    def route(request):
        if request.url.path == "/_cluster/health":
            return httpx.Response(302, headers={"Location": "/target"}, json={})
        return httpx.Response(401, json={"error": "unauthorized"})

    mock_http(route)
    with pytest.raises(ActionFailure, match="Status code: 401"):
        connectivity.__wrapped__(asset)


def test_unresolved_json_redirect_is_not_success(asset, monkeypatch):
    monkeypatch.setattr(
        helper, "request", Mock(return_value=httpx.Response(302, json={}))
    )
    with pytest.raises(ActionFailure, match="Status code: 302"):
        helper.request_json(asset, "/_cluster/health")


def test_cross_origin_redirect_does_not_forward_credentials(asset, mock_http):
    seen = []

    def route(request):
        seen.append(request)
        if request.url.host == "elastic.example":
            return httpx.Response(
                302, headers={"Location": "https://other.example/health"}
            )
        return httpx.Response(200, json={"status": "green"})

    mock_http(route)
    assert helper.request_json(asset, "/_cluster/health") == {"status": "green"}
    assert "Authorization" in seen[0].headers
    assert "Authorization" not in seen[1].headers


def test_make_request_still_returns_raw_redirect(asset, mock_http):
    mock_http(
        lambda request: httpx.Response(
            302, headers={"Location": "/target"}, text="redirect"
        )
    )
    result = make_request.__wrapped__(
        MakeRequestParams(http_method="GET", endpoint="/initial"), asset
    )
    assert result.status_code == 302
    assert result.response_body == "redirect"


@pytest.mark.parametrize("total", [{"value": 1, "relation": "eq"}, 1, None])
def test_query_preserves_nested_json_without_validation_warnings(
    asset, monkeypatch, total
):
    from copy import deepcopy
    from soar_sdk import action_results
    from src.actions.run_query import RunQueryOutput

    hits = {
        "hits": [
            {
                "_id": "1",
                "_source": {"nested": {"items": [1, None, "value"]}},
                "fields": {"a": [1, 2]},
            }
        ]
    }
    if total is not None:
        hits["total"] = total
    payload = {
        "_shards": {"total": 1},
        "hits": hits,
        "aggregations": {"count": 2},
        "took": 1,
        "timed_out": False,
    }
    expected = deepcopy(payload)
    warning = Mock(
        side_effect=AssertionError(
            "Valid Elasticsearch response produced a validation warning"
        )
    )
    monkeypatch.setattr(action_results, "warning", warning)
    from src.actions import run_query as module

    monkeypatch.setattr(module, "search", Mock(return_value=payload))
    result = run_query.__wrapped__(RunQueryParams(index="logs"), Mock(), asset)
    assert result.model_dump(by_alias=True) == expected
    assert payload == expected
    warning.assert_not_called()
    schema = {
        field["data_path"]: field["data_type"]
        for field in RunQueryOutput._to_json_schema()
    }
    assert schema["action_result.data.*.hits.hits.*._source"] == "string"
    assert schema["action_result.data.*.hits.hits.*.fields"] == "numeric"


@pytest.mark.parametrize(
    "invalid", [{"ingest_parser": "legacy.py"}, {"verify_server_cert": "invalid"}]
)
def test_asset_validation_does_not_expose_credentials(invalid):
    from pydantic import ValidationError

    password = "validation-secret-marker"  # pragma: allowlist secret
    with pytest.raises(ValidationError) as error:
        Asset(url="https://elastic.example", password=password, **invalid)
    assert password not in str(error.value)
    assert "input_value=" not in str(error.value)
    assert Asset.model_config["arbitrary_types_allowed"] is True


@pytest.mark.parametrize(
    "action_name",
    ["run_query", "get_config", "make_request", "test_connectivity", "on_poll"],
)
def test_expected_failures_use_sdk_failure_results(asset, monkeypatch, action_name):
    from src.app import app
    from src.actions import get_config as config_module

    params = None
    kwargs = {"soar": Mock()}
    if action_name == "run_query":
        action = run_query
        params = RunQueryParams(index="UPPER")
        kwargs["asset"] = asset
    elif action_name == "get_config":
        action = get_config
        params = Params()
        monkeypatch.setattr(
            config_module, "request_json", Mock(side_effect=ActionFailure("API failed"))
        )
        kwargs["asset"] = asset
    elif action_name == "make_request":
        action = make_request
        params = MakeRequestParams(http_method="GET", endpoint="https://other.example/")
        kwargs["asset"] = asset
    elif action_name == "test_connectivity":
        action = connectivity
        monkeypatch.setattr(app, "_asset", asset, raising=False)
        monkeypatch.setattr(
            helper, "request_json", Mock(side_effect=ActionFailure("Connection failed"))
        )
    else:
        action = on_poll
        params = OnPollParams()
        state = Mock(in_transaction=False)
        state.begin_transaction.side_effect = lambda: setattr(
            state, "in_transaction", True
        )
        asset._ingest_state = state
        monkeypatch.setattr(app, "_asset", asset, raising=False)
        kwargs["asset"] = asset

    add_result = Mock()
    add_exception = Mock()
    monkeypatch.setattr(app.actions_manager, "add_result", add_result)
    monkeypatch.setattr(app.actions_manager, "add_exception", add_exception)
    assert action(params, **kwargs) is False
    result = add_result.call_args.args[0]
    assert result.get_status() is False
    assert result.get_message().startswith(f"Action failure in {action.meta.action}:")
    assert "Traceback" not in result.get_message()
    add_exception.assert_not_called()
    if action_name == "on_poll":
        state.rollback.assert_called_once()


def test_unexpected_programming_errors_remain_distinguishable(asset, monkeypatch):
    from src.app import app
    from src.actions import run_query as module

    add_result = Mock()
    add_exception = Mock()
    monkeypatch.setattr(app.actions_manager, "add_result", add_result)
    monkeypatch.setattr(app.actions_manager, "add_exception", add_exception)
    monkeypatch.setattr(
        module, "search", Mock(side_effect=RuntimeError("unexpected bug"))
    )
    assert run_query(RunQueryParams(index="logs"), soar=Mock(), asset=asset) is False
    assert "Traceback" in add_result.call_args.args[0].get_message()
    add_exception.assert_called_once()


@pytest.mark.parametrize("error_type", [httpx.ConnectError, httpx.InvalidURL])
def test_transport_errors_are_action_failures(asset, monkeypatch, error_type):
    monkeypatch.setattr(
        httpx, "Client", Mock(side_effect=error_type("invalid connection"))
    )
    with pytest.raises(ActionFailure, match="Connection failed"):
        helper.request(asset, "/")


def test_malformed_endpoint_is_action_failure(asset):
    with pytest.raises(ActionFailure, match="relative"):
        helper.request(asset, "https://[")
