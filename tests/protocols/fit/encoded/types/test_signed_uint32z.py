
from hearty.protocols.fit.encoded.types.unsigned import UInt32Z

import unittest

# Basically, there's not much really to test (it's an enumerated type kind of thing).
# But we can use tests to see if the enumerated values change (and that would indcate there was an unexpected update).
class TestUInt32Z(unittest.TestCase):
  def test_init(self):
    tested = UInt32Z()

    self.assertEqual(0x0C, tested.number) # The MSb indicates endianness, so we need to exclude it from the number.
    self.assertTrue(tested.has_endianness)
    self.assertEqual("uint32z", tested.name)
    self.assertEqual(0x0000_0000, tested.invalid_value)
