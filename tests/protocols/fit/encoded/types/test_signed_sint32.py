
from hearty.protocols.fit.encoded.types.signed import SInt32

import unittest

class TestSInt32(unittest.TestCase):
  def test_init(self):
    tested = SInt32()

    self.assertEqual(0x05, tested.number) # The MSb indicates endianness, so we need to exclude it from the number.
    self.assertTrue(tested.has_endianness)
    self.assertEqual("sint32", tested.name)
    self.assertEqual(0x7FFF_FFFF, tested.invalid_value)

  def test_evaluate_incorrect_bytes_length(self):
    tested = SInt32()

    valid, value = tested.evaluate(bites=[], endianness="little")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_invalid_value_big_endianness(self):
    tested = SInt32()

    valid, value = tested.evaluate(bites=[0x7F, 0xFF, 0xFF, 0xFF], endianness="big")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_invalid_value_little_endianness(self):
    tested = SInt32()

    valid, value = tested.evaluate(bites=[0xFF, 0xFF, 0xFF, 0x7F], endianness="little")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_minimum_value_big_endianness(self):
    tested = SInt32()

    valid, value = tested.evaluate(bites=[0x80, 0x00, 0x00, 0x00], endianness="big")
    self.assertTrue(valid)
    self.assertEqual(-2147483648, value)

  def test_evaluate_minimum_value_little_endianness(self):
    tested = SInt32()

    valid, value = tested.evaluate(bites=[0x00, 0x00, 0x00, 0x80], endianness="little")
    self.assertTrue(valid)
    self.assertEqual(-2147483648, value)

  def test_evaluate_zero_value_big_endianness(self):
    tested = SInt32()

    valid, value = tested.evaluate(bites=[0x00, 0x00, 0x00, 0x00], endianness="big")
    self.assertTrue(valid)
    self.assertEqual(0, value)

  def test_evaluate_zero_value_little_endianness(self):
    tested = SInt32()

    valid, value = tested.evaluate(bites=[0x00, 0x00, 0x00, 0x00], endianness="little")
    self.assertTrue(valid)
    self.assertEqual(0, value)

  def test_evaluate_maximum_value_big_endianness(self):
    tested = SInt32()

    valid, value = tested.evaluate(bites=[0x7F, 0xFF, 0xFF, 0xFE], endianness="big")
    self.assertTrue(valid)
    self.assertEqual(2147483646, value)

  def test_evaluate_maximum_value_little_endianness(self):
    tested = SInt32()

    valid, value = tested.evaluate(bites=[0xFE, 0xFF, 0xFF, 0x7F], endianness="little")
    self.assertTrue(valid)
    self.assertEqual(2147483646, value)
