
from hearty.protocols.fit.encoded.types.array import Byte

import unittest

# Basically, there's not much really to test (it's an enumerated type kind of thing).
# But we can use tests to see if the enumerated values change (and that would indcate there was an unexpected update).
class TestString(unittest.TestCase):
  def test_init(self):
    tested = Byte()

    self.assertEqual(0x0D, tested.number)
    self.assertFalse(tested.has_endianness)
    self.assertEqual("byte", tested.name)
    self.assertEqual(0xFF, tested.invalid_value)
