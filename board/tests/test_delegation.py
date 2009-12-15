import unittest
from copy import copy

from board import model
from board import delegation

class DelegationTest(unittest.TestCase):
    def setUp(self):
        self._registry_bkp = delegation.registry
        delegation.registry = copy(delegation.registry)

    def tearDown(self):
        delegation.registry = self._registry_bkp

    def test_default_delegate(self):
        note = model.Note({'a': 'b'})
        d = note.get_delegate()
        self.assertTrue(isinstance(d, delegation.DefaultDelegate))
        self.assertTrue(d.note is note)

    def test_custom_delegate(self):
        delegation.register('test.deleg', TestDelegate)

        note = model.Note({'a': 'b'})
        d1 = note.get_delegate()
        self.assertTrue(isinstance(d1, delegation.DefaultDelegate))
        self.assertTrue(d1.note is note)

        note['-delegate-'] = 'test.deleg'
        d2 = note.get_delegate()
        self.assertTrue(isinstance(d2, TestDelegate))
        self.assertTrue(d1.note is note)

class TestDelegate(object):
    def __init__(self, note):
        self.note = note
