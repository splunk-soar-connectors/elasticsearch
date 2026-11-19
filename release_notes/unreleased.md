**Unreleased**

* Migrated the Elasticsearch connector to the Splunk SOAR SDK.
* The minimum supported Splunk SOAR version is now 7.0.0.
* Added the make request action for authenticated requests to Elasticsearch endpoints.
* For run query and get config, JSON API errors are now reported in the action message instead of including structured error data and input parameters in failed action results.
