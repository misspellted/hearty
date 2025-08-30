
from hearty.protocols.fit.encoded.record import NormalRecordHeader

import unittest

class TestNormalRecordHeader(unittest.TestCase):
  def test_init(self):
    tested = NormalRecordHeader()

    self.assertIsNone(tested.message_type)
    self.assertIsNone(tested.message_type_specific)
    self.assertIsNone(tested.local_message_type)

    self.assertEqual(f"Message Type: 0; Message Type Specific: 0; Local Message Type: None", f"{tested}")

    valid, encoded = tested.encode()
    self.assertFalse(valid)
    self.assertEqual(0, encoded)

  def test_decode_compressed_timestamp_record_header_type(self):
    tested = NormalRecordHeader()

    valid = tested.decode(0b1000_0000) # Other fields won't (shouldn't?) matter.
    self.assertFalse(valid)

    # And demonstrate they are not even decoded to a default value.
    self.assertIsNone(tested.message_type)
    self.assertIsNone(tested.message_type_specific)
    self.assertIsNone(tested.local_message_type)

  def test_decode_definition_message_zero(self):
    tested = NormalRecordHeader()

    valid = tested.decode(0b0100_0000)
    self.assertTrue(valid)

    self.assertTrue(tested.message_type)
    self.assertFalse(tested.message_type_specific)
    self.assertEqual(0, tested.local_message_type)

    self.assertEqual(f"Message Type: 1; Message Type Specific: 0; Local Message Type: 0", f"{tested}")

  def test_decode_data_message_zero(self):
    tested = NormalRecordHeader()

    valid = tested.decode(0b0000_0000)
    self.assertTrue(valid)

    self.assertFalse(tested.message_type)
    self.assertFalse(tested.message_type_specific)
    self.assertEqual(0, tested.local_message_type)

    self.assertEqual(f"Message Type: 0; Message Type Specific: 0; Local Message Type: 0", f"{tested}")

  def test_decode_definition_message_with_developer_field_definitions_zero(self):
    tested = NormalRecordHeader()

    valid = tested.decode(0b0110_0000)
    self.assertTrue(valid)

    self.assertTrue(tested.message_type)
    self.assertTrue(tested.message_type_specific)
    self.assertEqual(0, tested.local_message_type)

    self.assertEqual(f"Message Type: 1; Message Type Specific: 1; Local Message Type: 0", f"{tested}")

  def test_decode_data_message_with_developer_field_definitions_zero(self):
    tested = NormalRecordHeader()

    valid = tested.decode(0b0010_0000)
    self.assertFalse(valid) # Cannot have a data message with developer field definitions.

    self.assertFalse(tested.message_type)
    self.assertTrue(tested.message_type_specific)
    self.assertEqual(0, tested.local_message_type)

    self.assertEqual(f"Message Type: 0; Message Type Specific: 1; Local Message Type: 0", f"{tested}")

  def test_decode_data_message_fifteen(self):
    tested = NormalRecordHeader()

    valid = tested.decode(0b0000_1111)
    self.assertTrue(valid)

    self.assertFalse(tested.message_type)
    self.assertFalse(tested.message_type_specific)
    self.assertEqual(15, tested.local_message_type)

    self.assertEqual(f"Message Type: 0; Message Type Specific: 0; Local Message Type: 15", f"{tested}")

  def test_decode_definition_message_zero_with_reserved_set(self):
    tested = NormalRecordHeader()

    valid = tested.decode(0b0101_0000)
    self.assertFalse(valid)

    self.assertTrue(tested.message_type)
    self.assertFalse(tested.message_type_specific)
    self.assertEqual(0, tested.local_message_type)

    self.assertEqual(f"Message Type: 1; Message Type Specific: 0; Local Message Type: 0", f"{tested}")

  def test_decode_data_message_zero_with_reserved_set(self):
    tested = NormalRecordHeader()

    valid = tested.decode(0b0001_0000)
    self.assertFalse(valid)

    self.assertFalse(tested.message_type)
    self.assertFalse(tested.message_type_specific)
    self.assertEqual(0, tested.local_message_type)

    self.assertEqual(f"Message Type: 0; Message Type Specific: 0; Local Message Type: 0", f"{tested}")

  def test_encode_with_at_least_one_unset_attribute(self):
    tested = NormalRecordHeader()

    tested.message_type = True
    tested.message_type_specific = False

    valid, encoded = tested.encode()
    self.assertFalse(valid)
    self.assertEqual(0b0000_0000, encoded)

  def test_encode_definition_message_zero(self):
    tested = NormalRecordHeader()

    tested.message_type = True
    tested.message_type_specific = False
    tested.local_message_type = 0

    valid, encoded = tested.encode()
    self.assertTrue(valid)
    self.assertEqual(0b0100_0000, encoded)

  def test_encode_data_message_zero(self):
    tested = NormalRecordHeader()

    tested.message_type = False
    tested.message_type_specific = False
    tested.local_message_type = 0

    valid, encoded = tested.encode()
    self.assertTrue(valid)
    self.assertEqual(0b0000_0000, encoded)

  def test_encode_definition_message_with_developer_field_definitions_zero(self):
    tested = NormalRecordHeader()

    tested.message_type = True
    tested.message_type_specific = True
    tested.local_message_type = 0

    valid, encoded = tested.encode()
    self.assertTrue(valid)
    self.assertEqual(0b0110_0000, encoded)

  def test_encode_data_message_with_developer_field_definitions_zero(self):
    tested = NormalRecordHeader()

    tested.message_type = False
    tested.message_type_specific = True
    tested.local_message_type = 0

    valid, encoded = tested.encode()
    self.assertFalse(valid) # Cannot have a data message with developer field definitions.
    self.assertEqual(0b0000_0000, encoded)

  def test_encode_data_message_fifteen(self):
    tested = NormalRecordHeader()

    tested.message_type = False
    tested.message_type_specific = False
    tested.local_message_type = 15

    valid, encoded = tested.encode()
    self.assertTrue(valid)
    self.assertEqual(0b0000_1111, encoded)
