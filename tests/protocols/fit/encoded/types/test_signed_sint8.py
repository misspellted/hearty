
from hearty.protocols.fit.encoded.types.signed import SInt8

import unittest

# Basically, there's not much really to test (it's an enumerated type kind of thing).
# But we can use tests to see if the enumerated values change (and that would indcate there was an unexpected update).
class TestSInt8(unittest.TestCase):
  def test_init(self):
    tested = SInt8()

    self.assertEqual(0x01, tested.number)
    self.assertFalse(tested.has_endianness)
    self.assertEqual("sint8", tested.name)
    self.assertEqual(0x7F, tested.invalid_value)
