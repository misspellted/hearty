
from hearty.protocols.fit.encoded.types.array import String

import unittest

# Basically, there's not much really to test (it's an enumerated type kind of thing).
# But we can use tests to see if the enumerated values change (and that would indcate there was an unexpected update).
class TestString(unittest.TestCase):
  def test_init(self):
    tested = String()

    self.assertEqual(0x07, tested.number)
    self.assertFalse(tested.has_endianness)
    self.assertEqual("string", tested.name)
    self.assertEqual(0x00, tested.invalid_value)
