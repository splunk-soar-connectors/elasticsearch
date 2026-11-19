**Requirements**\
This connector uses the Splunk SOAR SDK and requires Splunk SOAR 7.0.0 or later.

Elasticsearch installations can be configured to allow REST API access without any type of
authentication. The app therefore marks **username** and **password** as optional parameters. If
specified, the app will use these for generating the basic authentication header for various
Elasticsearch REST endpoints.\
The connection can be configured over HTTP or HTTPS, so if **test connectivity** fails please check
the protocol.

- **Changes from version 2.0.5 to version 3.0.0:**

  - run query - **type** parameter has been removed.\
    Reference: [Removal of mapping types from search
    API](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/removal-of-types.html#_search_apis)
