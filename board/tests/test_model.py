import unittest

from board import model

class NoteDictTest(unittest.TestCase):
    def test_set(self):
        note = model.Note()
        self.assertEqual(dict(note), {})
        note['a'] = 'b'
        self.assertEqual(dict(note), {'a': 'b'})
        self.assertRaises(ValueError, note.__setitem__, 'c', 13)
        self.assertRaises(ValueError, note.__setitem__, 13, 'c')

    def test_update(self):
        note = model.Note()
        note.update({'a': 'b', 'c': 'd'})
        self.assertEqual(dict(note), {'a': 'b', 'c': 'd'})
        self.assertRaises(ValueError, note.update, {'c': 13})
        self.assertRaises(ValueError, note.update, {13: 'c'})

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

class NoteChildrenTest(unittest.TestCase):
    def test_append_children(self):
        note = model.Note()
        self.assertEqual(list(note.children()), [])

        note2 = model.Note()
        note.append_child(note2)
        self.assertEqual(list(note.children()), [note2])

        note3 = model.Note()
        note.append_child(note3)
        self.assertEqual(list(note.children()), [note2, note3])

        note4 = model.Note()
        note.append_child(note4)
        self.assertEqual(list(note.children()), [note2, note3, note4])

    def test_insert_before(self):
        note = model.Note()
        note2 = model.Note()
        note.insert_child_before(note2, None)
        self.assertEqual(list(note.children()), [note2])

        note3 = model.Note()
        note.insert_child_before(note3, None)
        self.assertEqual(list(note.children()), [note2, note3])

        note4 = model.Note()
        note.insert_child_before(note4, note3)
        self.assertEqual(list(note.children()), [note2, note4, note3])

    def test_parent(self):
        note = model.Note()
        self.assertEqual(note.parent, None)

        note2 = model.Note()
        note.append_child(note2)
        self.assertEqual(note2.parent, note)

    def test_change_parent(self):
        note = model.Note()
        note2 = model.Note()
        note3 = model.Note()
        note4 = model.Note()
        note.append_child(note2)
        note.append_child(note3)
        note2.append_child(note4)
        self.assertEqual(list(note2.children()), [note4])
        self.assertEqual(list(note3.children()), [])
        self.assertEqual(note4.parent, note2)

        note3.append_child(note4)
        self.assertEqual(list(note2.children()), [])
        self.assertEqual(list(note3.children()), [note4])
        self.assertEqual(note4.parent, note3)

        self.assertRaises(AttributeError, setattr, note2, 'parent', note3)
