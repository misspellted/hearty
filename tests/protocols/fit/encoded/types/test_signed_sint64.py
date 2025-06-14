
from hearty.protocols.fit.encoded.types.signed import SInt64

import unittest

# Basically, there's not much really to test (it's an enumerated type kind of thing).
# But we can use tests to see if the enumerated values change (and that would indcate there was an unexpected update).
class TestSInt64(unittest.TestCase):
  def test_init(self):
    tested = SInt64()

    self.assertEqual(0x0E, tested.number) # The MSb indicates endianness, so we need to exclude it from the number.
    self.assertTrue(tested.has_endianness)
    self.assertEqual("sint64", tested.name)
    self.assertEqual(0x7FFF_FFFF_FFFF_FFFF, tested.invalid_value)
