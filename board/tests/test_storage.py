import unittest

from board import model

class TSNote(model.Note):
    def _properties_factory(self):
        self._ts_properties = dict()
        return self._ts_properties

    def _children_factory(self):
        self._ts_children = list()
        return self._ts_children

class NoteStorageTest(unittest.TestCase):
    def test_properties_storage(self):
        note = TSNote()
        note['a'] = 'b'
        note['c'] = 'd'
        self.assertRaises(ValueError, note.__setitem__, 3, 'x')
        self.assertRaises(ValueError, note.__setitem__, 'x', 3)
        self.assertEqual(note._ts_properties, {'a': 'b', 'c': 'd'})

    def test_children_storage(self):
        note = TSNote()
        note2 = TSNote()
        note.append_child(note2)
        self.assertEqual(note._ts_children, [note2])

    def test_load(self):
        note2 = model.Note()
        note = model.Note(properties={'x': 'y'}, children=[note2])
        self.assertEqual(dict(note), {'x': 'y'})
        self.assertEqual(list(note.children()), [note2])
