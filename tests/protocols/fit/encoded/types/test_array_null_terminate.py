
from hearty.protocols.fit.encoded.types.array import null_terminate

import unittest

class TestNullTerimate(unittest.TestCase):
  def test_none(self):
    with self.assertRaises(ValueError) as bed:
      null_terminate(text=None)

  def test_non_str(self):
    with self.assertRaises(TypeError) as bed:
      null_terminate(text=13)

  def test_empty_str(self):
    self.assertEqual("\0", null_terminate(text=""))

  def test_not_null_terminated_str(self):
    self.assertEqual("hello\0", null_terminate(text="hello"))

  def test_null_terminated_str(self):
    self.assertEqual("world\0", null_terminate(text="world\0"))