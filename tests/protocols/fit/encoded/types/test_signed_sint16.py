
from hearty.protocols.fit.encoded.types.signed import SInt16

import unittest

class TestSInt16(unittest.TestCase):
  def test_init(self):
    tested = SInt16()

    self.assertEqual(0x03, tested.number) # The MSb indicates endianness, so we need to exclude it from the number.
    self.assertTrue(tested.has_endianness)
    self.assertEqual("sint16", tested.name)
    self.assertEqual(0x7FFF, tested.invalid_value)

  def test_evaluate_incorrect_bytes_length(self):
    tested = SInt16()

    valid, value = tested.evaluate(bytes=[], endianness="little")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_invalid_value_big_endianness(self):
    tested = SInt16()

    valid, value = tested.evaluate(bytes=[0x7F, 0xFF], endianness="big")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_invalid_value_little_endianness(self):
    tested = SInt16()

    valid, value = tested.evaluate(bytes=[0xFF, 0x7F], endianness="little")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_minimum_value_big_endianness(self):
    tested = SInt16()

    valid, value = tested.evaluate(bytes=[0x80, 0x00], endianness="big")
    self.assertTrue(valid)
    self.assertEqual(-32768, value)

  def test_evaluate_minimum_value_little_endianness(self):
    tested = SInt16()

    valid, value = tested.evaluate(bytes=[0x00, 0x80], endianness="little")
    self.assertTrue(valid)
    self.assertEqual(-32768, value)

  def test_evaluate_zero_value_big_endianness(self):
    tested = SInt16()

    valid, value = tested.evaluate(bytes=[0x00, 0x00], endianness="big")
    self.assertTrue(valid)
    self.assertEqual(0, value)

  def test_evaluate_zero_value_little_endianness(self):
    tested = SInt16()

    valid, value = tested.evaluate(bytes=[0x00, 0x00], endianness="little")
    self.assertTrue(valid)
    self.assertEqual(0, value)

  def test_evaluate_maximum_value_big_endianness(self):
    tested = SInt16()

    valid, value = tested.evaluate(bytes=[0x7F, 0xFE], endianness="big")
    self.assertTrue(valid)
    self.assertEqual(32766, value)

  def test_evaluate_maximum_value_little_endianness(self):
    tested = SInt16()

    valid, value = tested.evaluate(bytes=[0xFE, 0x7F], endianness="little")
    self.assertTrue(valid)
    self.assertEqual(32766, value)
