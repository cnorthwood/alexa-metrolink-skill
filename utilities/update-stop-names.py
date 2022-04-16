#!virtualenv/bin/python3

from collections import defaultdict
import csv
import json
import os
import re
import requests

ALTERNATIVES = defaultdict(list, **{
    'AIR': ['Airport'],
    'GMX': ['Deansgate', 'G-Mex'],
    'MTM': ['Newton Heath'],
    'RIN': ['Rochdale town centre'],
    'SHA': ['Shaw'],
    'WYT': ['Wythenshawe'],
})

OVERRIDES = {
    'RIN': 'rochdale-town-centre'
}

def get_stop_names():
    with requests.Session() as request:
        response = request.get('http://odata.tfgm.com/opendata/downloads/TfGMMetroRailStops.csv')

        for row in csv.reader(response.content.decode('ascii').splitlines(), delimiter=','):
            if row[0].startswith('9400ZZMA'):
                yield row[0][8:], row[6]


def slugify_stop_name(stop_code, stop_name):
    if stop_code in OVERRIDES:
        return OVERRIDES[stop_code]
    stop_name = stop_name.lower()
    stop_name = stop_name.replace('&', 'and')
    stop_name = stop_name.replace("'s", 's')
    stop_name = stop_name.replace("'", ' ')
    stop_name = stop_name.replace(' ', '-')
    stop_name = re.sub('-+', '-', stop_name)
    return stop_name


if __name__ == '__main__':
    stops = {code: name for code, name in get_stop_names()}
    with open(os.path.join(os.path.dirname(__file__), '..', 'interaction-model', 'stop-names.txt'), 'w') as stop_names_file:
        for name in stops.values():
            stop_names_file.write('{}\n'.format(name))
        for alteratives in ALTERNATIVES.values():
            for alternative in alteratives:
                stop_names_file.write('{}\n'.format(alternative))

    with open(os.path.join(os.path.dirname(__file__), '..', 'stop-names.json'), 'w') as stop_names_file:
        json.dump(
            {
                slugify_stop_name(code, name): {
                    'name': name,
                    'alternatives': [alternative.lower() for alternative in [name] + ALTERNATIVES[code]]
                }
                for code, name in stops.items()
            },
            stop_names_file, indent=2
        )
