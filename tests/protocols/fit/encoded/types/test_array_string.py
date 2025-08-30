
from hearty.protocols.fit.encoded.types.array import String, null_terminate

import unittest

# Basically, there's not much really to test (it's an enumerated type kind of thing).
# But we can use tests to see if the enumerated values change (and that would indcate there was an unexpected update).
class TestString(unittest.TestCase):
  def test_init(self):
    tested = String()

    self.assertEqual(0x07, tested.number)
    self.assertFalse(tested.has_endianness)
    self.assertEqual("string", tested.name)
    self.assertEqual(0x00, tested.invalid_value)

  def test_evaluate_empty(self):
    tested = String()

    valid, value = tested.evaluate(bites=[], endianness="irrelevant")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_just_null_termination(self):
    tested = String()

    valid, value = tested.evaluate(bites=[0x00], endianness="irrelevant")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_text_sans_null_termination(self):
    tested = String()

    # "Hello, world!"
    valid, value = tested.evaluate(bites=[0x48, 0x65, 0x6C, 0x6C, 0x6F, 0x2C, 0x20, 0x77, 0x6F, 0x72, 0x6C, 0x64, 0x21], endianness="irrelevant")
    self.assertFalse(valid)
    self.assertIsNone(value)

  def test_evaluate_text_with_null_termination(self):
    tested = String()

    # "Hello, world!\0"
    valid, value = tested.evaluate(bites=[0x48, 0x65, 0x6C, 0x6C, 0x6F, 0x2C, 0x20, 0x77, 0x6F, 0x72, 0x6C, 0x64, 0x21, 0x00], endianness="irrelevant")
    self.assertTrue(valid)
    self.assertEqual("Hello, world!\0", value)
