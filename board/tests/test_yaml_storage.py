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

    def test_load(self):
        in_data = ("{properties: {a: 'b'}, children: ["
                   "    {properties: {c: 'd'}, children: []},"
                   "    {properties: {e: 'f'}, children: ["
                   "        {properties: {g: 'h'}, children: []},"
                   "        {properties: {i: 'j'}, children: []}]},"
                   "    {properties: {k: 'l'}, children: []}]}")
        root = yaml_storage.load(in_data)
        self.assertTrue(root.parent is None)
        self.assertEqual(dict(root), {'a': 'b'})

        root_children = list(root.children())
        self.assertEqual(len(root_children), 3)
        self.assertEqual(dict(root_children[0]), {'c': 'd'})
        self.assertEqual(dict(root_children[1]), {'e': 'f'})
        self.assertEqual(dict(root_children[2]), {'k': 'l'})
        self.assertTrue(root_children[0].parent is root)
        self.assertTrue(root_children[1].parent is root)
        self.assertTrue(root_children[2].parent is root)
        self.assertEqual(len(list(root_children[0].children())), 0)
        self.assertEqual(len(list(root_children[1].children())), 2)
        self.assertEqual(len(list(root_children[2].children())), 0)

        sub_children = list(root_children[1].children())
        self.assertEqual(len(sub_children), 2)
        self.assertEqual(dict(sub_children[0]), {'g': 'h'})
        self.assertEqual(dict(sub_children[1]), {'i': 'j'})
        self.assertTrue(sub_children[0].parent is root_children[1])
        self.assertTrue(sub_children[1].parent is root_children[1])
        self.assertEqual(len(list(sub_children[0].children())), 0)
        self.assertEqual(len(list(sub_children[1].children())), 0)
