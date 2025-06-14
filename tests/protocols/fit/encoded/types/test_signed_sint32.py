
from hearty.protocols.fit.encoded.types.signed import SInt32

import unittest

# Basically, there's not much really to test (it's an enumerated type kind of thing).
# But we can use tests to see if the enumerated values change (and that would indcate there was an unexpected update).
class TestSInt32(unittest.TestCase):
  def test_init(self):
    tested = SInt32()

    self.assertEqual(0x05, tested.number) # The MSb indicates endianness, so we need to exclude it from the number.
    self.assertTrue(tested.has_endianness)
    self.assertEqual("sint32", tested.name)
    self.assertEqual(0x7FFF_FFFF, tested.invalid_value)
