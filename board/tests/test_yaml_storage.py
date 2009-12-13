import unittest
import json

from board import model
from board import yaml_storage

class YamlStorageTest(unittest.TestCase):
    def test_dump(self):
        root = model.Note({'here': 'root'},
                          [model.Note({'here': 'kid1'}),
                           model.Note({'here': 'kid2'},
                                      [model.Note({'here': 'kid2.1'})])])
        yaml_out = yaml_storage.dump(root)
        out_data = json.loads(yaml_out)
        reference = {
            'properties': {'here': 'root'}, 'children': [
                {'properties': {'here': 'kid1'}, 'children': []},
                {'properties': {'here': 'kid2'}, 'children': [
                     {'properties': {'here': 'kid2.1'}, 'children': []},
                 ]},
            ]}
        self.assertEqual(out_data, reference)
