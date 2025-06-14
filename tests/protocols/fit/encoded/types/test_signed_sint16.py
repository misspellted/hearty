
from hearty.protocols.fit.encoded.types.signed import SInt16

import unittest

# Basically, there's not much really to test (it's an enumerated type kind of thing).
# But we can use tests to see if the enumerated values change (and that would indcate there was an unexpected update).
class TestSInt16(unittest.TestCase):
  def test_init(self):
    tested = SInt16()

    self.assertEqual(0x03, tested.number) # The MSb indicates endianness, so we need to exclude it from the number.
    self.assertTrue(tested.has_endianness)
    self.assertEqual("sint16", tested.name)
    self.assertEqual(0x7FFF, tested.invalid_value)
