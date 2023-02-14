[comment]: # "Auto-generated SOAR connector documentation"
# Elasticsearch

Publisher: Splunk  
Connector Version: 3\.0\.0  
Product Vendor: Elastic  
Product Name: Elasticsearch  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 5\.4\.0  

This app integrates with an Elasticsearch installation to implement ingestion and investigative actions

[comment]: # " File: README.md"
[comment]: # "  Copyright (c) 2016-2023 Splunk Inc."
[comment]: # ""
[comment]: # "Licensed under the Apache License, Version 2.0 (the 'License');"
[comment]: # "you may not use this file except in compliance with the License."
[comment]: # "You may obtain a copy of the License at"
[comment]: # ""
[comment]: # "    http://www.apache.org/licenses/LICENSE-2.0"
[comment]: # ""
[comment]: # "Unless required by applicable law or agreed to in writing, software distributed under"
[comment]: # "the License is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,"
[comment]: # "either express or implied. See the License for the specific language governing permissions"
[comment]: # "and limitations under the License."
[comment]: # ""
Elasticsearch installations can be configured to allow REST API access without any type of
authentication. The app therefore marks **username** and **password** as optional parameters. If
specified, the app will use these for generating the basic authentication header for various
Elasticsearch REST endpoints.  
The connection can be configured over HTTP or HTTPS, so if **test connectivity** fails please check
the protocol.

**Playbook Backward Compatibility**  
An action parameter has been changed as detailed below. Hence, it is recommended that the end-user
update their existing playbooks parameters accordingly to ensure that playbooks created using
earlier versions of the app are functioning correctly.

-   **Changes from version 2.0.5 to version 3.0.0:**

      

    -   run query - **type** parameter has been removed.  
        Reference: [Removal of mapping types from search
        API](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/removal-of-types.html#_search_apis)


### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a Elasticsearch asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**url** |  required  | string | Device URL including the port, e\.g\. https\://myelastic\.enterprise\.com\:9200
**verify\_server\_cert** |  optional  | boolean | Verify server certificate
**username** |  optional  | string | Username
**password** |  optional  | password | Password
**ingest\_index** |  optional  | string | Ingestion index
**ingest\_routing** |  optional  | string | Ingestion routing
**ingest\_query** |  optional  | string | Ingestion query
**ingest\_parser** |  optional  | file | Custom Elasticsearch parser

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity\. This action logs into the device to check the connection and credentials  
[get config](#action-get-config) - Returns the list of indices and their information currently configured on the ElasticSearch instance  
[run query](#action-run-query) - Run a search query on the Elasticsearch installation\. Please escape any quotes that are part of the query string  
[on poll](#action-on-poll) - Run a query in elasticsearch and ingest the results  

## action: 'test connectivity'
Validate the asset configuration for connectivity\. This action logs into the device to check the connection and credentials

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'get config'
Returns the list of indices and their information currently configured on the ElasticSearch instance

Type: **investigate**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action\_result\.status | string |  |   success  failed 
action\_result\.data\.\*\.document\_count | string |  |   1 
action\_result\.data\.\*\.health | string |  |   green  red  yellow 
action\_result\.data\.\*\.index | string |  `elasticsearch index`  |   test\_index 
action\_result\.data\.\*\.status | string |  |   open 
action\_result\.data\.\*\.store\_size | string |  |   12mb  12b 
action\_result\.summary\.total\_indices | numeric |  |   20 
action\_result\.message | string |  |   Total indices\: 20 
summary\.total\_objects | numeric |  |   1 
summary\.total\_objects\_successful | numeric |  |   1   

## action: 'run query'
Run a search query on the Elasticsearch installation\. Please escape any quotes that are part of the query string

Type: **investigate**  
Read only: **True**

The action executes the query on an Elasticsearch installation by doing a POST on the REST endpoint '<b>base\_url</b>/<b>index</b>/\_search' with the input <b>query</b> as the data, if specified\. Please see the Elasticseach website for query format and documentation\.<br>The <b>routing</b> parameter is appended as a parameter in the REST call if specified\.<br>As an e\.g\. the following query returns only the <i>id</i> and <i>name</i> of all the items from the given <b>index</b><br>\{ "query"\: \{ "match\_all"\: \{\} \}, "\_source"\: \["id", "name"\]\}\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**index** |  required  | Comma\-separated list of indexes to query on | string |  `elasticsearch index` 
**routing** |  optional  | Shards to query on \(routing value\) | string | 
**query** |  optional  | Query to run \(in ElasticSearch language\) | string |  `elasticsearch query` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action\_result\.status | string |  |   success  failed 
action\_result\.parameter\.index | string |  `elasticsearch index`  |   test\_index 
action\_result\.parameter\.query | string |  `elasticsearch query`  |   \{ "query"\: \{"match\_all"\: \{\}\}\} 
action\_result\.parameter\.routing | string |  |   route1 
action\_result\.data\.\*\.\_shards\.failed | numeric |  |   0 
action\_result\.data\.\*\.\_shards\.skipped | numeric |  |   0 
action\_result\.data\.\*\.\_shards\.successful | numeric |  |   0 
action\_result\.data\.\*\.\_shards\.total | numeric |  |   1 
action\_result\.data\.\*\.hits\.hits\.\*\.\_id | string |  |   LOdkiYNBlA\_PxVqybtLP 
action\_result\.data\.\*\.hits\.hits\.\*\.\_index | string |  |   test\_index 
action\_result\.data\.\*\.hits\.hits\.\*\.\_score | numeric |  |   1 
action\_result\.data\.\*\.hits\.hits\.\*\.\_source | string |  |  
action\_result\.data\.\*\.hits\.hits\.\*\.fields | numeric |  |  
action\_result\.data\.\*\.hits\.max\_score | numeric |  |   1 
action\_result\.data\.\*\.hits\.total\.relation | string |  |   eq 
action\_result\.data\.\*\.hits\.total\.value | numeric |  |   2 
action\_result\.data\.\*\.took | numeric |  |   1 
action\_result\.summary\.timed\_out | boolean |  |   True  False 
action\_result\.summary\.total\_hits | numeric |  |   40 
action\_result\.message | string |  |   Total hits\: 40, Timed out\: False 
summary\.total\_objects | numeric |  |   1 
summary\.total\_objects\_successful | numeric |  |   1   

## action: 'on poll'
Run a query in elasticsearch and ingest the results

Type: **ingest**  
Read only: **True**

This will run a query in elasticsearch using the <b>index</b>, <b>routing</b>, and <b>query</b> configured in the app settings and ingest the results\. The <b>query</b> is not modified by Splunk SOAR in any way before being requested in elasticsearch\. This means that the <b>query</b> must account for relative time between ingestion runs, query limits, and page sizes\.<br><br>The <a href="https\://www\.elastic\.co/guide/en/elasticsearch/reference/current/search\-request\-body\.html">raw JSON response</a> from elasticsearch is passed to a parser script which returns a list of containers and artifacts\. If a custom parsing script is not provided, the <a href="/app\_resource/elasticsearch\_fde8b9da\-d38c\-45c2\-832a\-1e1c543ed287/elasticsearch\_parser\.py">default parsing script</a> is used\:<br><pre class="shell"><code>def ingest\_parser\(data\)\:
    results = \[\]
    if not isinstance\(data, dict\)\:
        return results

    hits = data\.get\('hits', \{\}\)\.get\('hits', \[\]\)
    for hit in hits\:
        container = \{\}
        artifacts = \[\]

        \# anything printed to stdout will be added to the Splunk SOAR debug logs
        print\('Found hit \{\}\. Building container'\.format\(hit\['\_id'\]\)\)

        container\['run\_automation'\] = False
        container\['source\_data\_identifier'\] = hit\['\_id'\]
        container\['name'\] = 'Elasticsearch\: \{\} \{\} \{\}'\.format\(hit\['\_index'\],
                                                             ,
                                                             hit\['\_id'\]\)

        artifacts\.append\(\{
            \# always True since there is only one
            'run\_automation'\: True,
            'label'\: 'event',
            'name'\: 'elasticsearch event',
            'cef'\: hit\.get\('\_source'\),
            'source\_data\_identifier'\: hit\['\_id'\]
        \}\)

        results\.append\(\{
            'container'\: container,
            'artifacts'\: artifacts
        \}\)

    return results
</code></pre>\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**container\_id** |  optional  | Limit ingestion to these container IDs | string | 
**start\_time** |  optional  | Start of time range in epoch time \(default\: 10 days ago\) | numeric | 
**end\_time** |  optional  | End of time range in epoch time \(default\: now\) | numeric | 
**container\_count** |  optional  | Maximum number of containers to create | numeric | 
**artifact\_count** |  optional  | Maximum number of artifacts to create per container | numeric | 

#### Action Output
No Output