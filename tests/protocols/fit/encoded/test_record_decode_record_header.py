from hearty.protocols.fit.encoded.record import decode_record_header, NormalRecordHeader, CompressedTimestampRecordHeader

import unittest

class TestDecode_Record_Header(unittest.TestCase):
  def test_decode_record_header_for_normal_record_header_with_valid_definition_message_with_developer_field_definitions(self):
    valid, record_header = decode_record_header(encoded_record_header=0b0110_0000)

    self.assertTrue(valid)
    self.assertIsInstance(record_header, NormalRecordHeader)
    self.assertTrue(record_header.message_type)
    self.assertTrue(record_header.message_type_specific)
    self.assertEqual(0, record_header.local_message_type)

  def test_decode_record_header_for_normal_record_header_with_valid_data_message(self):
    valid, record_header = decode_record_header(encoded_record_header=0b0000_1111)

    self.assertTrue(valid)
    self.assertIsInstance(record_header, NormalRecordHeader)
    self.assertFalse(record_header.message_type)
    self.assertFalse(record_header.message_type_specific)
    self.assertEqual(15, record_header.local_message_type)

  def test_decode_record_header_for_compressed_timestamp_record_header_with_valid_time_offset(self):
    valid, record_header = decode_record_header(encoded_record_header=0b1001_0101)

    self.assertTrue(valid) # Any compressed timestamp record header is valid from the decode_record_header function.
    self.assertIsInstance(record_header, CompressedTimestampRecordHeader)
    self.assertEqual(0, record_header.local_message_type)
    self.assertEqual(21, record_header.time_offset)

  def test_decode_record_header_for_normal_record_header_with_invalid_data_message_with_reserved_set(self):
    valid, record_header = decode_record_header(encoded_record_header=0b0001_0000)

    self.assertFalse(valid)
    self.assertIsInstance(record_header, NormalRecordHeader)
    self.assertFalse(record_header.message_type)
    self.assertFalse(record_header.message_type_specific)
    self.assertEqual(0, record_header.local_message_type)
