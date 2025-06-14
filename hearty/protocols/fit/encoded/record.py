
import logging
logger = logging.getLogger(__name__)

MASK_RECORD_HEADER_TYPE = 0b1000_0000
"""
A bitmask to identify which record header type is encoded.
"""

class NormalRecordHeader:
  MASK_MESSAGE_TYPE = 0b0100_0000
  MASK_MESSAGE_TYPE_SPECIFIC = 0b0010_0000
  MASK_RESERVED = 0b0001_0000
  MASK_LOCAL_MESSAGE_TYPE = 0b0000_1111

  def __init__(self):
    self.message_type:bool = None
    self.message_type_specific:bool = None
    self.local_message_type:int = None

  def decode(self, encoded:int) -> bool:
    valid = (encoded & MASK_RECORD_HEADER_TYPE) != MASK_RECORD_HEADER_TYPE

    if valid:
      self.message_type = (encoded & NormalRecordHeader.MASK_MESSAGE_TYPE) == NormalRecordHeader.MASK_MESSAGE_TYPE
      self.message_type_specific = (encoded & NormalRecordHeader.MASK_MESSAGE_TYPE_SPECIFIC) == NormalRecordHeader.MASK_MESSAGE_TYPE_SPECIFIC
      reserved = encoded & NormalRecordHeader.MASK_RESERVED
      self.local_message_type = encoded & NormalRecordHeader.MASK_LOCAL_MESSAGE_TYPE

      # Only a definition message can define developer field defintions; otherwise, reserved must be 0.
      valid = False if self.message_type_specific and not self.message_type else False if reserved else True

    return valid

  def __repr__(self):
    return f"Message Type: {1 if self.message_type else 0}; Message Type Specific: {1 if self.message_type_specific else 0}; Local Message Type: {self.local_message_type}"

  def encode(self) -> tuple[bool, int]:
    valid = False if None in [self.message_type, self.message_type_specific, self.local_message_type] else False if self.message_type_specific and not self.message_type else True
    encoded = 0

    if valid:
      encoded |= NormalRecordHeader.MASK_MESSAGE_TYPE if self.message_type else 0
      encoded |= NormalRecordHeader.MASK_MESSAGE_TYPE_SPECIFIC if self.message_type and self.message_type_specific else 0
      encoded |= NormalRecordHeader.MASK_LOCAL_MESSAGE_TYPE & self.local_message_type

    return (valid, encoded)

class CompressedTimestampRecordHeader:
  MASK_LOCAL_MESSAGE_TYPE = 0b0110_0000
  MASK_TIME_OFFSET = 0b0001_1111

  def __init__(self):
    self.local_message_type:int = None
    self.time_offset:int = None

  def decode(self, encoded:int) -> bool:
    valid = (encoded & MASK_RECORD_HEADER_TYPE) == MASK_RECORD_HEADER_TYPE

    if valid:
      self.local_message_type = (encoded & CompressedTimestampRecordHeader.MASK_LOCAL_MESSAGE_TYPE) >> 5 # Decode the value into the 0-3 values for human consumption.
      self.time_offset = encoded & CompressedTimestampRecordHeader.MASK_TIME_OFFSET

    return valid

  def __repr__(self) -> str:
    return f"Local Message Type: {self.local_message_type}; Time Offset (seconds): {self.time_offset}"

  def encode(self) -> tuple[bool, int]:
    valid = False if None in [self.local_message_type, self.time_offset] else True
    encoded = 0

    if valid:
      encoded |= MASK_RECORD_HEADER_TYPE
      encoded |= CompressedTimestampRecordHeader.MASK_LOCAL_MESSAGE_TYPE & (self.local_message_type << 5) # Encode the value into the binary file form.
      encoded |= CompressedTimestampRecordHeader.MASK_TIME_OFFSET & self.time_offset

    return (valid, encoded)

def decode_record_header(encoded_record_header:int) -> tuple[bool, NormalRecordHeader | CompressedTimestampRecordHeader]:
  encoded = encoded_record_header & 0b1111_1111 # Only look at the lowest byte-sworth of bits.
  logger.debug(f"Decoding record header: {encoded:03d} | 0x{encoded:02X} | 0b{encoded:08b}")

  record_header = CompressedTimestampRecordHeader() if encoded_record_header & MASK_RECORD_HEADER_TYPE == MASK_RECORD_HEADER_TYPE else NormalRecordHeader()
  valid = record_header.decode(encoded=encoded)

  # Log the decoding, even if it is invalid.
  logger.debug(f"Decoded record header (valid? {valid}): {record_header}")

  return (valid, record_header)
