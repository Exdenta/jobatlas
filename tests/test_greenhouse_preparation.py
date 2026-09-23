"""Prepared Greenhouse client contracts do not imply hosted migration."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft7Validator, Draft202012Validator
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / 'integrations/shared'


def load(name):
    return json.loads((SHARED / name).read_text())


class GreenhousePreparationTests(unittest.TestCase):
    def test_bounded_example_has_independent_default_off_options(self):
        schema=load('greenhouse-inventory-input-v1.schema.json')
        Draft7Validator.check_schema(schema)
        sample=load('input-greenhouse-inventory.json')
        Draft7Validator(schema).validate(sample)
        self.assertEqual(sample['maxItems'],5)
        self.assertFalse(sample['aiEnrichment']['enabled'])
        self.assertFalse(sample['translateToEnglish'])
        self.assertFalse(sample['dedupe']['enabled'])
        for ai in (False,True):
            for english in (False,True):
                value=deepcopy(sample);value['aiEnrichment']['enabled']=ai;value['translateToEnglish']=english
                Draft7Validator(schema).validate(value)

    def test_selection_and_raw_retention_fail_closed(self):
        validator=Draft7Validator(load('greenhouse-inventory-input-v1.schema.json'))
        sample=load('input-greenhouse-inventory.json')
        for change in ({'boards':[]},{'boards':['unknown']},{'boards':['Stripe']},{'boards':['stripe','stripe']},
                       {'includeRaw':False},{'openRouterApiKey':'buyer'},{'maxItems':201},{'postedWithin':'0d'}):
            with self.subTest(change=change),self.assertRaises(ValidationError):validator.validate({**sample,**change})
        sample.pop('boards')
        with self.assertRaises(ValidationError):validator.validate(sample)
        sample.update(schemaVersion='nomad-agent-job-search-input-v1',greenhouse={
            'schemaVersion':'nomad-greenhouse-search-v1','boards':['figma']})
        validator.validate(sample)
        with self.assertRaises(ValidationError):validator.validate({**sample,'boards':['figma']})

    def test_source_extension_is_closed_and_has_no_inferred_fields(self):
        schema=load('greenhouse-v1.schema.json');Draft202012Validator.check_schema(schema)
        value={name:None for name in schema['required']};value.update(board='stripe',nativeId='123',internalJobId=1)
        Draft202012Validator(schema).validate(value)
        with self.assertRaises(ValidationError):Draft202012Validator(schema).validate({**value,'aiSummary':'invented'})
        self.assertTrue(schema['$id'].startswith('https://raw.githubusercontent.com/Exdenta/jobatlas/'))

    def test_board_summary_is_separate_from_generic_summary(self):
        schema=load('inventory-board-run-summary-v1.schema.json');Draft202012Validator.check_schema(schema)
        self.assertEqual(schema['properties']['schemaVersion']['const'],'nomad-inventory-board-public-run-v1')
        self.assertIn('selection',schema['required']);self.assertIn('selectionDigest',schema['required'])
        generic=load('inventory-run-summary-v1.schema.json')
        self.assertTrue(all(branch['properties']['schemaVersion']['const']=='nomad-inventory-public-run-v1' for branch in generic['oneOf']))

    def test_guide_keeps_preparation_and_release_boundaries(self):
        guide=(ROOT/'docs/normalized-greenhouse.md').read_text()
        self.assertIn('prepared locally',guide);self.assertIn('deployment and board activation are pending',guide)
        self.assertIn('`latest`',guide);self.assertIn('immutable build ID',guide)
        self.assertNotIn('api.oinkjobsearch.com',guide)
        self.assertNotIn('APIFY_SOURCE_TOKEN',guide)


if __name__=='__main__':unittest.main()
