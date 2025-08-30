
from hearty.protocols.fit.encoded.types.floating import Float32

import unittest

# Basically, there's not much really to test (it's an enumerated type kind of thing).
# But we can use tests to see if the enumerated values change (and that would indcate there was an unexpected update).
class TestFloat32(unittest.TestCase):
  def test_init(self):
    tested = Float32()

    self.assertEqual(0x08, tested.number) # The MSb indicates endianness, so we need to exclude it from the number.
    self.assertTrue(tested.has_endianness)
    self.assertEqual("float32", tested.name)
    self.assertEqual(0xFFFF_FFFF, tested.invalid_value)

  def test_evaluate_incorrect_bytes_length(self):
    tested = Float32()

    valid, value = tested.evaluate(bites=[], endianness="little")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_invalid_value_big_endianness(self):
    tested = Float32()

    valid, value = tested.evaluate(bites=[0xFF, 0xFF, 0xFF, 0xFF], endianness="big")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_invalid_value_little_endianness(self):
    tested = Float32()

    valid, value = tested.evaluate(bites=[0xFF, 0xFF, 0xFF, 0xFF], endianness="little")
    self.assertFalse(valid)
    self.assertIsNone(value)

# TODO: Write test cases for some values.
# Here's a nice source: https://en.wikipedia.org/wiki/Single-precision_floating-point_format#Notable_single-precision_cases
