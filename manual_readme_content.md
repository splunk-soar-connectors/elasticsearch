[comment]: # " File: README.md"
[comment]: # "  Copyright (c) 2016-2024 Splunk Inc."
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
