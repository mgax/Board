import unittest

from board import model

class NoteDictTest(unittest.TestCase):
    def test_set(self):
        note = model.Note()
        self.assertEqual(dict(note), {})
        note['a'] = 'b'
        self.assertEqual(dict(note), {'a': 'b'})
        self.assertRaises(ValueError, note.__setitem__, 'c', 13)

    def test_update(self):
        note = model.Note()
        note.update({'a': 'b', 'c': 'd'})
        self.assertEqual(dict(note), {'a': 'b', 'c': 'd'})
        self.assertRaises(ValueError, note.update, {'c': 13})

    def test_get(self):
        note = model.Note()
        note.update({'a': 'b', 'c': 'd'})
        self.assertEqual(note['a'], 'b')
        self.assertEqual(note.get('a'), 'b')
        self.assertEqual(note['x'], None)
        self.assertEqual(note.get('x'), None)
        self.assertEqual(note.get('x', 'y'), 'y')
        self.assertEqual(note.get('a', 'y'), 'b')

    def test_remove_values(self):
        note = model.Note()
        note['a'] = 'b'
        note['c'] = 'd'
        self.assertEqual(dict(note), {'a': 'b', 'c': 'd'})
        del note['a']
        self.assertEqual(dict(note), {'c': 'd'})
        note['c'] = None
        self.assertEqual(dict(note), {})

    def test_length(self):
        note = model.Note()
        self.assertEqual(len(note), 0)
        note['a'] = 'b'
        self.assertEqual(len(note), 1)
        note['c'] = 'd'
        note.update({'e': 'f', 'g': 'h'})
        self.assertEqual(len(note), 4)
