
from hearty.protocols.fit.encoded.types.base import BaseType

import unittest

class TestBaseType(unittest.TestCase):
  def test_init(self):
    tested = BaseType()

    self.assertIsNone(tested.has_endianness)
    self.assertIsNone(tested.number)

    with self.assertRaises(NotImplementedError) as bed:
      tested.name

    with self.assertRaises(NotImplementedError) as bed:
      tested.invalid_value

    with self.assertRaises(TypeError) as bed:
      f"{tested}"
  
  def test_decode_with_reserved_set(self):
    tested = BaseType()

    self.assertFalse(tested.decode(0b0100_0000))

  def test_decode_with_excessive_number(self):
    tested = BaseType()

    self.assertFalse(tested.decode(0b0001_0010))

  def test_decode_enum(self):
    tested = BaseType()

    self.assertTrue(tested.decode(0b0000_0000))
    self.assertFalse(tested.has_endianness)
    self.assertEqual(0, tested.number)

    # While a base type can be decoded, the class doesn't know the type name or invalid value.
    with self.assertRaises(NotImplementedError) as bed:
      tested.name

    with self.assertRaises(NotImplementedError) as bed:
      tested.invalid_value

    # But with the number decoded, the NotImplementedError shows up instead of TypeError (so it shows more 'success' after decoding).
    with self.assertRaises(NotImplementedError) as bed:
      f"{tested}"

# NOTE: The evaluate_integer function won't have unit tests here; instead, they are split among the various test_(un|)signed_$intType.py test cases.
# If there is a problem with this strategy, raise an issue &| contribute them here.
