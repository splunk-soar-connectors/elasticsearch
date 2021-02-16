# File: elasticsearch_parser.py
# Copyright (c) 2016-2021 Splunk Inc.
#
# SPLUNK CONFIDENTIAL - Use or disclosure of this material in whole or in part
# without a valid written license from Splunk Inc. is PROHIBITED.
#
# --


def ingest_parser(data):
    results = []
    if not isinstance(data, dict):
        return results

    hits = data.get('hits', {}).get('hits', [])
    for hit in hits:
        container = {}
        artifacts = []

        # anything printed to stdout will be added to the phantom debug logs
        print("Found hit {}. Building container".format(hit['_id']))

        container['run_automation'] = False
        container['source_data_identifier'] = hit['_id']
        container['name'] = 'Elasticsearch: {} {} {}'.format(hit['_index'],
                                                             hit['_type'],
                                                             hit['_id'])

        artifacts.append({
            # always True since there is only one
            'run_automation': True,
            'label': 'event',
            'name': 'elasticsearch event',
            'cef': hit.get('_source'),
            'source_data_identifier': hit['_id']
        })

        results.append({
            'container': container,
            'artifacts': artifacts
        })

    return results
