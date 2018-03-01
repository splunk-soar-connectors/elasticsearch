# --
# File: elasticsearch_parser.py
#
# Copyright (c) Phantom Cyber Corporation, 2017
#
# This unpublished material is proprietary to Phantom Cyber.
# All rights reserved. The methods and
# techniques described herein are considered trade secrets
# and/or confidential. Reproduction or distribution, in whole
# or in part, is forbidden except by express written permission
# of Phantom Cyber.
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
        print "Found hit {}. Building container".format(hit['_id'])

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
