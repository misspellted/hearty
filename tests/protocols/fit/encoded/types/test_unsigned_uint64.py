
from hearty.protocols.fit.encoded.types.unsigned import UInt64

import unittest

# Basically, there's not much really to test (it's an enumerated type kind of thing).
# But we can use tests to see if the enumerated values change (and that would indcate there was an unexpected update).
class TestUInt64(unittest.TestCase):
  def test_init(self):
    tested = UInt64()

    self.assertEqual(0x0F, tested.number) # The MSb indicates endianness, so we need to exclude it from the number.
    self.assertTrue(tested.has_endianness)
    self.assertEqual("uint64", tested.name)
    self.assertEqual(0xFFFF_FFFF_FFFF_FFFF, tested.invalid_value)

  def test_evaluate_incorrect_bytes_length(self):
    tested = UInt64()

    valid, value = tested.evaluate(bites=[], endianness="little")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_invalid_value_big_endianness(self):
    tested = UInt64()

    valid, value = tested.evaluate(bites=[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], endianness="big")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_invalid_value_little_endianness(self):
    tested = UInt64()

    valid, value = tested.evaluate(bites=[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], endianness="little")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_minimum_value_big_endianness(self):
    tested = UInt64()

    valid, value = tested.evaluate(bites=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], endianness="big")
    self.assertTrue(valid)
    self.assertEqual(0, value)

  def test_evaluate_minimum_value_little_endianness(self):
    tested = UInt64()

    valid, value = tested.evaluate(bites=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], endianness="little")
    self.assertTrue(valid)
    self.assertEqual(0, value)

  def test_evaluate_maximum_value_big_endianness(self):
    tested = UInt64()

    valid, value = tested.evaluate(bites=[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFE], endianness="big")
    self.assertTrue(valid)
    self.assertEqual(18446744073709551614, value)

  def test_evaluate_maximum_value_little_endianness(self):
    tested = UInt64()

    valid, value = tested.evaluate(bites=[0xFE, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], endianness="little")
    self.assertTrue(valid)
    self.assertEqual(18446744073709551614, value)
