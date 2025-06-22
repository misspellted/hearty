
from hearty.protocols.fit.encoded.types.unsigned import UInt8

import unittest

# Basically, there's not much really to test (it's an enumerated type kind of thing).
# But we can use tests to see if the enumerated values change (and that would indcate there was an unexpected update).
class TestUInt8(unittest.TestCase):
  def test_init(self):
    tested = UInt8()

    self.assertEqual(0x02, tested.number)
    self.assertFalse(tested.has_endianness)
    self.assertEqual("uint8", tested.name)
    self.assertEqual(0xFF, tested.invalid_value)
