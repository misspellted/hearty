
from hearty.protocols.fit.encoded.types.unsigned import UInt16

import unittest

# Basically, there's not much really to test (it's an enumerated type kind of thing).
# But we can use tests to see if the enumerated values change (and that would indcate there was an unexpected update).
class TestUInt16(unittest.TestCase):
  def test_init(self):
    tested = UInt16()

    self.assertEqual(0x04, tested.number) # The MSb indicates endianness, so we need to exclude it from the number.
    self.assertTrue(tested.has_endianness)
    self.assertEqual("uint16", tested.name)
    self.assertEqual(0xFFFF, tested.invalid_value)
