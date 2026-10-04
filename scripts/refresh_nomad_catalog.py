import concurrent.futures
import datetime
import json
from pathlib import Path
import re
import subprocess
import urllib.request
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'main'
catalog = json.loads((ROOT / 'nomad-site/actors.json').read_text())
examples = {a['slug']: a.get('inputExample') for a in catalog['actors']}

def read(path):
    request = urllib.request.Request('https://api.apify.com/v2/' + path, headers={'User-Agent': 'NomadAgentWebsiteCatalog/1.0'})
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.load(response)['data']

def inspect(actor):
    meta = read('acts/nomad-agent~' + actor['slug'])
    if meta.get('username') != 'nomad-agent':
        raise ValueError('Actor moved out of the authorized publisher: '+actor['slug'])
    if not meta.get('isPublic') or meta.get('isDeprecated'):
        return None, {'slug': actor['slug'], 'reason': 'No longer public and active'}
    latest = meta.get('taggedBuilds', {}).get('latest', {}).get('buildId')
    if not latest:
        raise ValueError('Missing latest selector: '+actor['slug'])
    build = read('actor-builds/' + latest)
    if build.get('actId') != meta['id'] or build.get('status') != 'SUCCEEDED':
        raise ValueError('Invalid latest immutable build: '+actor['slug'])
    schema = build.get('inputSchema')
    schema = json.loads(schema) if isinstance(schema, str) else schema
    example = examples.get(actor['slug'])
    if example is not None and schema:
        try:
            jsonschema.validate(example, schema)
        except jsonschema.ValidationError:
            example = None
    else:
        example = None
    if example is None and schema and 'maxItems' in schema.get('properties', {}):
        candidate = {'maxItems': 5}
        properties = schema['properties']
        if 'schemaVersion' in properties and 'default' in properties['schemaVersion']:
            candidate['schemaVersion'] = properties['schemaVersion']['default']
        if 'maxItemsPerSource' in properties:
            candidate['maxItemsPerSource'] = 5
        if 'dedupe' in properties:
            candidate['dedupe'] = {'enabled': True, 'key': ''}
        try:
            jsonschema.validate(candidate, schema)
            example = candidate
        except jsonschema.ValidationError:
            pass
    return {
        'slug': meta['name'], 'actorId': meta['id'], 'title': meta['title'],
        'description': actor['description'], 'url': 'https://apify.com/nomad-agent/' + meta['name'],
        'isPublic': True, 'isDeprecated': False, 'family': actor['family'],
        'schemaSelector': 'latest', 'buildId': build['id'], 'buildNumber': build['buildNumber'],
        'inputExample': example, 'inputSchema': schema,
    }, None

actors = catalog['actors']
if any(a['family'] != 'Simple and source-specific jobs' or not re.fullmatch(r'[a-z0-9][a-z0-9-]*', a['slug']) for a in actors):
    raise ValueError('Review the explicit simple-job site cohort before refresh')
results = []
excluded = []
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    for actor, result in zip(actors, pool.map(inspect, actors)):
        row, reason = result
        if row:
            results.append(row)
        else:
            excluded.append(reason)
snapshot = {
    'schemaVersion': 'nomad-simple-site-catalog-v1',
    'observedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
    'evidenceBoundary': 'Public identity, visibility, deprecation status and latest-resolved immutable-build input schemas checked through read-only Apify API requests. No Actors were run. Starter inputs are validated against the observed schemas; coverage, availability, costs and destination delivery are not execution-tested.',
    'actors': sorted(results, key=lambda x: x['slug']), 'excluded': excluded,
}
destination = ROOT / 'nomad-site' / 'actors.json'
destination.parent.mkdir(exist_ok=True)
destination.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({'actors': len(results), 'validatedStarterInputs': sum(a['inputExample'] is not None for a in results), 'excluded': excluded, 'snapshot': str(destination)}))
