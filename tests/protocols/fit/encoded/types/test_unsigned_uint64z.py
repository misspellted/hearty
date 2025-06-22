
from hearty.protocols.fit.encoded.types.unsigned import UInt64Z

import unittest

# Basically, there's not much really to test (it's an enumerated type kind of thing).
# But we can use tests to see if the enumerated values change (and that would indcate there was an unexpected update).
class TestUInt64Z(unittest.TestCase):
  def test_init(self):
    tested = UInt64Z()

    self.assertEqual(0x10, tested.number) # The MSb indicates endianness, so we need to exclude it from the number.
    self.assertTrue(tested.has_endianness)
    self.assertEqual("uint64z", tested.name)
    self.assertEqual(0x0000_0000_0000_0000, tested.invalid_value)
