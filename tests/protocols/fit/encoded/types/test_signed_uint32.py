
from hearty.protocols.fit.encoded.types.unsigned import UInt32

import unittest

# Basically, there's not much really to test (it's an enumerated type kind of thing).
# But we can use tests to see if the enumerated values change (and that would indcate there was an unexpected update).
class TestUInt32(unittest.TestCase):
  def test_init(self):
    tested = UInt32()

    self.assertEqual(0x06, tested.number) # The MSb indicates endianness, so we need to exclude it from the number.
    self.assertTrue(tested.has_endianness)
    self.assertEqual("uint32", tested.name)
    self.assertEqual(0xFFFF_FFFF, tested.invalid_value)
