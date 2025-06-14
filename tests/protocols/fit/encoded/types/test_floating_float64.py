
from hearty.protocols.fit.encoded.types.floating import Float64

import unittest

# Basically, there's not much really to test (it's an enumerated type kind of thing).
# But we can use tests to see if the enumerated values change (and that would indcate there was an unexpected update).
class TestFloat64(unittest.TestCase):
  def test_init(self):
    tested = Float64()

    self.assertEqual(0x09, tested.number) # The MSb indicates endianness, so we need to exclude it from the number.
    self.assertTrue(tested.has_endianness)
    self.assertEqual("float64", tested.name)
    self.assertEqual(0xFFFF_FFFF_FFFF_FFFF, tested.invalid_value)
