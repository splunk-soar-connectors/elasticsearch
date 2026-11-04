# Elasticsearch

Publisher: Splunk <br>
Connector Version: 4.0.0 <br>
Product Vendor: Elastic <br>
Product Name: Elasticsearch <br>
Minimum Product Version: 7.0.0

This app integrates with an Elasticsearch installation to implement ingestion and investigative actions

Elasticsearch installations can be configured to allow REST API access without any type of
authentication. The app therefore marks **username** and **password** as optional parameters. If
specified, the app will use these for generating the basic authentication header for various
Elasticsearch REST endpoints.\
The connection can be configured over HTTP or HTTPS, so if **test connectivity** fails please check
the protocol.

**Playbook Backward Compatibility**\
An action parameter has been changed as detailed below. Hence, it is recommended that the end-user
update their existing playbooks parameters accordingly to ensure that playbooks created using
earlier versions of the app are functioning correctly.

- **Changes from version 2.0.5 to version 3.0.0:**

  - run query - **type** parameter has been removed.\
    Reference: [Removal of mapping types from search
    API](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/removal-of-types.html#_search_apis)

### Configuration variables

This table lists the configuration variables required to operate Elasticsearch. These variables are specified when configuring a Elasticsearch asset in Splunk SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**url** | required | string | Device URL including the port, e.g. https://myelastic.enterprise.com:9200 |
**verify_server_cert** | required | boolean | Verify server certificate |
**username** | optional | string | Username |
**password** | optional | password | Password |
**ingest_index** | optional | string | Ingestion index |
**ingest_routing** | optional | string | Ingestion routing |
**ingest_query** | optional | string | Ingestion query |

### Supported Actions

[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity. <br>
[on poll](#action-on-poll) - Run the configured query and ingest its hits using the bundled parser.

The query controls time ranges and pagination, as in the legacy connector. <br>
[get config](#action-get-config) - Returns the list of indices and their information currently configured on the ElasticSearch instance. <br>
[make request](#action-make-request) - Make an authenticated request relative to the configured Elasticsearch URL. <br>
[run query](#action-run-query) - Run a search query on the Elasticsearch installation. Please escape any quotes that are part of the query string.

## action: 'test connectivity'

Validate the asset configuration for connectivity.

Type: **test** <br>
Read only: **True**

Basic test for app.

#### Action Parameters

No parameters are required for this action

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'on poll'

Run the configured query and ingest its hits using the bundled parser.

The query controls time ranges and pagination, as in the legacy connector.

Type: **ingest** <br>
Read only: **True**

Callback action for the on_poll ingest functionality

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**start_time** | optional | Start of time range, in epoch time (milliseconds). | numeric | |
**end_time** | optional | End of time range, in epoch time (milliseconds). | numeric | |
**container_count** | optional | Maximum number of container records to query for. | numeric | |
**artifact_count** | optional | Maximum number of artifact records to query for. | numeric | |
**container_id** | optional | Comma-separated list of container IDs to limit the ingestion to. | string | |

#### Action Output

No Output

## action: 'get config'

Returns the list of indices and their information currently configured on the ElasticSearch instance.

Type: **investigate** <br>
Read only: **True**

#### Action Parameters

No parameters are required for this action

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.data.\*.index | string | `elasticsearch index` | |
action_result.data.\*.health | string | | |
action_result.data.\*.status | string | | |
action_result.data.\*.document_count | string | | |
action_result.data.\*.store_size | string | | |
action_result.summary.total_indices | numeric | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'make request'

Make an authenticated request relative to the configured Elasticsearch URL.

Type: **generic** <br>
Read only: **False**

'make request' action for the app. Used to handle arbitrary HTTP requests with the app's asset

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**http_method** | required | The HTTP method to use for the request. | string | |
**endpoint** | required | The endpoint to send the request to. | string | |
**headers** | optional | The headers to send with the request (JSON object). An example is {'Content-Type': 'application/json'} | string | |
**query_parameters** | optional | Parameters to append to the URL (JSON object or query string). An example is ?key=value&key2=value2 | string | |
**body** | optional | The body to send with the request (JSON object). An example is {'key': 'value', 'key2': 'value2'} | string | |
**timeout** | optional | The timeout for the request in seconds. | numeric | |
**verify_ssl** | optional | Whether to verify the SSL certificate. Default is True. | boolean | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.http_method | string | | |
action_result.parameter.endpoint | string | | |
action_result.parameter.headers | string | | |
action_result.parameter.query_parameters | string | | |
action_result.parameter.body | string | | |
action_result.parameter.timeout | numeric | | |
action_result.parameter.verify_ssl | boolean | | |
action_result.data.\*.status_code | numeric | | 200 404 500 |
action_result.data.\*.response_body | string | | {"key": "value"} |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'run query'

Run a search query on the Elasticsearch installation. Please escape any quotes that are part of the query string.

Type: **investigate** <br>
Read only: **True**

The action executes the query on an Elasticsearch installation by doing a POST on the REST endpoint '<b>base_url</b>/<b>index</b>/\_search' with the input <b>query</b> as the data, if specified. Please see the Elasticseach website for query format and documentation.<br>The <b>routing</b> parameter is appended as a parameter in the REST call if specified.<br>As an e.g. the following query returns only the <i>id</i> and <i>name</i> of all the items from the given <b>index</b><br>{ "query": { "match_all": {} }, "\_source": ["id", "name"]}.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**index** | required | Comma-separated list of indexes to query on | string | `elasticsearch index` |
**routing** | optional | Shards to query on (routing value) | string | |
**query** | optional | Query to run (in ElasticSearch language) | string | `elasticsearch query` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.index | string | `elasticsearch index` | |
action_result.parameter.routing | string | | |
action_result.parameter.query | string | `elasticsearch query` | |
action_result.data.\*.\_shards.failed | numeric | | |
action_result.data.\*.\_shards.skipped | numeric | | |
action_result.data.\*.\_shards.successful | numeric | | |
action_result.data.\*.\_shards.total | numeric | | |
action_result.data.\*.hits.hits.\*.\_id | string | | |
action_result.data.\*.hits.hits.\*.\_index | string | | |
action_result.data.\*.hits.hits.\*.\_score | numeric | | |
action_result.data.\*.hits.hits.\*.\_source | string | | |
action_result.data.\*.hits.hits.\*.fields | numeric | | |
action_result.data.\*.hits.max_score | numeric | | |
action_result.data.\*.hits.total.relation | string | | |
action_result.data.\*.hits.total.value | numeric | | |
action_result.data.\*.took | numeric | | |
action_result.summary.timed_out | boolean | | True False |
action_result.summary.total_hits | numeric | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

______________________________________________________________________

Auto-generated Splunk SOAR Connector documentation.

Copyright 2026 Splunk Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
