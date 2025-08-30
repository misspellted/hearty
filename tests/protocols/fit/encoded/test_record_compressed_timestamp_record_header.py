
from hearty.protocols.fit.encoded.record import CompressedTimestampRecordHeader

import unittest

class TestCompressedTimestampRecordHeader(unittest.TestCase):
  def test_init(self):
    tested = CompressedTimestampRecordHeader()

    self.assertIsNone(tested.local_message_type)
    self.assertIsNone(tested.time_offset)

    self.assertEqual(f"Local Message Type: None; Time Offset (seconds): None", f"{tested}")

    valid, encoded = tested.encode()
    self.assertFalse(valid)
    self.assertEqual(0, encoded)

  def test_decode_normal_record_header_type(self):
    tested = CompressedTimestampRecordHeader()

    valid = tested.decode(0b0000_0000) # Other fields won't (shouldn't?) matter.
    self.assertFalse(valid)

    # And demonstrate they are not even decoded to a default value.
    self.assertIsNone(tested.local_message_type)
    self.assertIsNone(tested.time_offset)

  def test_decode_zero_and_zero_offset(self):
    tested = CompressedTimestampRecordHeader()

    valid = tested.decode(0b1000_0000)
    self.assertTrue(valid)

    self.assertEqual(0, tested.local_message_type)
    self.assertEqual(0, tested.time_offset)

    self.assertEqual(f"Local Message Type: 0; Time Offset (seconds): 0", f"{tested}")

  def test_decode_three_and_zero_offset(self):
    tested = CompressedTimestampRecordHeader()

    valid = tested.decode(0b1110_0000)
    self.assertTrue(valid)

    self.assertEqual(3, tested.local_message_type)
    self.assertEqual(0, tested.time_offset)

    self.assertEqual(f"Local Message Type: 3; Time Offset (seconds): 0", f"{tested}")

  def test_decode_zero_and_full_offset(self):
    tested = CompressedTimestampRecordHeader()

    valid = tested.decode(0b1001_1111)
    self.assertTrue(valid)

    self.assertEqual(0, tested.local_message_type)
    self.assertEqual(31, tested.time_offset)

    self.assertEqual(f"Local Message Type: 0; Time Offset (seconds): 31", f"{tested}")

  def test_decode_three_and_full_offset(self):
    tested = CompressedTimestampRecordHeader()

    valid = tested.decode(0b1111_1111)
    self.assertTrue(valid)

    self.assertEqual(3, tested.local_message_type)
    self.assertEqual(31, tested.time_offset)

    self.assertEqual(f"Local Message Type: 3; Time Offset (seconds): 31", f"{tested}")
