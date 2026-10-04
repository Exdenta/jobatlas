"""Explicitly starts one bounded, chargeable run. Never run for offline validation."""
import json
import os
from pathlib import Path
from apify_client import ApifyClient

def main():
    here=Path(__file__).resolve().parent
    client=ApifyClient(os.environ['APIFY_TOKEN'])
    params=json.loads((here/'input.json').read_text())
    run=client.actor('nomad-agent/ml-ai-dev-bundle').call(run_input=params,build='latest',max_total_charge_usd=1,timeout_secs=300)
    print(json.dumps({k:run.get(k) for k in ('id','buildId','status')}))
    if run['status']!='SUCCEEDED':raise RuntimeError('Run did not succeed; inspect its log')
    rows=list(client.dataset(run['defaultDatasetId']).list_items(limit=params['maxItems']).items)
    (here/'output.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
    summary=client.key_value_store(run['defaultKeyValueStoreId']).get_record('RUN-SUMMARY')
    (here/'run-summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    print('Rows:',len(rows),'Inspect output.json and run-summary.json before use.')

if __name__=='__main__':main()
