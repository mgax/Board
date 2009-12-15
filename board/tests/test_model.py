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

    def test_remove_note(self):
        note = model.Note()
        note2 = model.Note()
        note.append_child(note2)
        self.assertEqual(list(note.children()), [note2])
        self.assertTrue(note2.parent is note)

        note.remove_child(note2)
        self.assertEqual(list(note.children()), [])
        self.assertTrue(note2.parent is None)

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

class DocumentTest(unittest.TestCase):
    def test_new_document(self):
        doc = model.Document()
        self.assertEqual(len(doc), 1)
        root = doc.root
        self.assertTrue(root._parent is None)
        self.assertTrue(root._document is doc)
        self.assertEqual(root._id, 0)

    def test_create_note(self):
        doc = model.Document()
        note = model.Note()
        doc.root.append_child(note)
        self.assertEqual(len(doc), 2)
        self.assertTrue(note._parent is doc.root)
        self.assertTrue(note._document is doc)
        self.assertEqual(note._id, 1)

        # adding a note with children should not be allowed
        note2 = model.Note(children=[model.Note()])
        self.assertRaises(AssertionError, doc.root.append_child, note2)

        # adding a note from another document should not be allowed
        note3 = model.Note()
        note3._document = 13
        self.assertRaises(AssertionError, doc.root.append_child, note3)

    def test_remove_note(self):
        doc = model.Document()
        note = model.Note()
        doc.root.append_child(note)
        self.assertEqual(note._id, 1)
        self.assertTrue(note._document is doc)
        self.assertEqual(len(doc), 2)

        doc.root.remove_child(note)
        self.assertTrue(note._id is None)
        self.assertTrue(note._document is None)
        self.assertEqual(len(doc), 1)
        self.assertEqual(doc._index, {0: doc.root})

        note2 = model.Note()
        doc.root.append_child(note2)
        note3 = model.Note()
        note2.append_child(note3)
        self.assertEqual(len(doc), 3)

        doc.root.remove_child(note2)
        self.assertTrue(note3._id is None)
        self.assertTrue(note3._document is None)
        self.assertEqual(len(doc), 1)
