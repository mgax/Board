import unittest

from board import model

class PathsTest(unittest.TestCase):
    def test_note_lookup(self):
        note = model.Note()
        self.assertEqual(note.lookup(''), note)

        kid1 = model.Note({'id': 'kid1', 'a': 'b'})
        note.append_child(kid1)
        self.assertTrue(note.lookup('asdf') is None)
        self.assertTrue(note.lookup('kid1') is kid1)

        kid2 = model.Note({'id': 'kid2', 'c': 'd'})
        kid1.append_child(kid2)
        self.assertTrue(note.lookup('qwer/blah') is None)
        self.assertTrue(note.lookup('kid1/blah') is None)
        self.assertTrue(note.lookup('kid1/kid2') is kid2)
        self.assertTrue(note.lookup('kid1/kid2/zxcv') is None)
