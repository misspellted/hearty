
from hearty.protocols.fit.encoded.types.unsigned import UInt8Z

import unittest

# Basically, there's not much really to test (it's an enumerated type kind of thing).
# But we can use tests to see if the enumerated values change (and that would indcate there was an unexpected update).
class TestUInt8Z(unittest.TestCase):
  def test_init(self):
    tested = UInt8Z()

    self.assertEqual(0x0A, tested.number)
    self.assertFalse(tested.has_endianness)
    self.assertEqual("uint8z", tested.name)
    self.assertEqual(0x00, tested.invalid_value)

  def test_evaluate_incorrect_bytes_length(self):
    tested = UInt8Z()

    valid, value = tested.evaluate(bites=[], endianness="little")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_invalid_value_big_endianness(self):
    tested = UInt8Z()

    valid, value = tested.evaluate(bites=[0x00], endianness="big")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_invalid_value_little_endianness(self):
    tested = UInt8Z()

    valid, value = tested.evaluate(bites=[0x00], endianness="little")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_minimum_value_big_endianness(self):
    tested = UInt8Z()

    valid, value = tested.evaluate(bites=[0x01], endianness="big")
    self.assertTrue(valid)
    self.assertEqual(1, value)

  def test_evaluate_minimum_value_little_endianness(self):
    tested = UInt8Z()

    valid, value = tested.evaluate(bites=[0x01], endianness="little")
    self.assertTrue(valid)
    self.assertEqual(1, value)

  def test_evaluate_maximum_value_big_endianness(self):
    tested = UInt8Z()

    valid, value = tested.evaluate(bites=[0xFF], endianness="big")
    self.assertTrue(valid)
    self.assertEqual(255, value)

  def test_evaluate_maximum_value_little_endianness(self):
    tested = UInt8Z()

    valid, value = tested.evaluate(bites=[0xFF], endianness="little")
    self.assertTrue(valid)
    self.assertEqual(255, value)
