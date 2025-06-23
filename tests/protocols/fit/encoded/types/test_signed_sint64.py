
from hearty.protocols.fit.encoded.types.signed import SInt64

import unittest

class TestSInt64(unittest.TestCase):
  def test_init(self):
    tested = SInt64()

    self.assertEqual(0x0E, tested.number) # The MSb indicates endianness, so we need to exclude it from the number.
    self.assertTrue(tested.has_endianness)
    self.assertEqual("sint64", tested.name)
    self.assertEqual(0x7FFF_FFFF_FFFF_FFFF, tested.invalid_value)

  def test_evaluate_incorrect_bytes_length(self):
    tested = SInt64()

    valid, value = tested.evaluate(bites=[], endianness="little")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_invalid_value_big_endianness(self):
    tested = SInt64()

    valid, value = tested.evaluate(bites=[0x7F, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], endianness="big")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_invalid_value_little_endianness(self):
    tested = SInt64()

    valid, value = tested.evaluate(bites=[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x7F], endianness="little")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_minimum_value_big_endianness(self):
    tested = SInt64()

    valid, value = tested.evaluate(bites=[0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], endianness="big")
    self.assertTrue(valid)
    self.assertEqual(-9223372036854775808, value)

  def test_evaluate_minimum_value_little_endianness(self):
    tested = SInt64()

    valid, value = tested.evaluate(bites=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80], endianness="little")
    self.assertTrue(valid)
    self.assertEqual(-9223372036854775808, value)

  def test_evaluate_zero_value_big_endianness(self):
    tested = SInt64()

    valid, value = tested.evaluate(bites=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], endianness="big")
    self.assertTrue(valid)
    self.assertEqual(0, value)

  def test_evaluate_zero_value_little_endianness(self):
    tested = SInt64()

    valid, value = tested.evaluate(bites=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], endianness="little")
    self.assertTrue(valid)
    self.assertEqual(0, value)

  def test_evaluate_maximum_value_big_endianness(self):
    tested = SInt64()

    valid, value = tested.evaluate(bites=[0x7F, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFE], endianness="big")
    self.assertTrue(valid)
    self.assertEqual(9223372036854775806, value)

  def test_evaluate_maximum_value_little_endianness(self):
    tested = SInt64()

    valid, value = tested.evaluate(bites=[0xFE, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x7F], endianness="little")
    self.assertTrue(valid)
    self.assertEqual(9223372036854775806, value)
