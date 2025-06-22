
from hearty.protocols.fit.encoded.types.signed import SInt8

import unittest

class TestSInt8(unittest.TestCase):
  def test_init(self):
    tested = SInt8()

    self.assertEqual(0x01, tested.number)
    self.assertFalse(tested.has_endianness)
    self.assertEqual("sint8", tested.name)
    self.assertEqual(0x7F, tested.invalid_value)

  def test_evaluate_incorrect_bytes_length(self):
    tested = SInt8()

    valid, value = tested.evaluate(bytes=[], endianness="little")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_invalid_value_big_endianness(self):
    tested = SInt8()

    valid, value = tested.evaluate(bytes=[0x7F], endianness="big")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_invalid_value_little_endianness(self):
    tested = SInt8()

    valid, value = tested.evaluate(bytes=[0x7F], endianness="little")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_minimum_value_big_endianness(self):
    tested = SInt8()

    valid, value = tested.evaluate(bytes=[0x80], endianness="big")
    self.assertTrue(valid)
    self.assertEqual(-128, value)

  def test_evaluate_minimum_value_little_endianness(self):
    tested = SInt8()

    valid, value = tested.evaluate(bytes=[0x80], endianness="little")
    self.assertTrue(valid)
    self.assertEqual(-128, value)

  def test_evaluate_zero_value_big_endianness(self):
    tested = SInt8()

    valid, value = tested.evaluate(bytes=[0x00], endianness="big")
    self.assertTrue(valid)
    self.assertEqual(0, value)

  def test_evaluate_zero_value_little_endianness(self):
    tested = SInt8()

    valid, value = tested.evaluate(bytes=[0x00], endianness="little")
    self.assertTrue(valid)
    self.assertEqual(0, value)

  def test_evaluate_maximum_value_big_endianness(self):
    tested = SInt8()

    valid, value = tested.evaluate(bytes=[0x7E], endianness="big")
    self.assertTrue(valid)
    self.assertEqual(126, value)

  def test_evaluate_maximum_value_little_endianness(self):
    tested = SInt8()

    valid, value = tested.evaluate(bytes=[0x7E], endianness="little")
    self.assertTrue(valid)
    self.assertEqual(126, value)
