
import logging
logger = logging.getLogger(__name__)

from .field import FieldDefinition, FIELD_DEFINITION_BYTES, Field

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

class MessageDefinitionRecord:
  def __init__(self):
    self.header = None
    self.reserved = None
    self.architecture = None
    self.global_message_number = None
    self.field_definition_count = 0
    self.field_definitions = list()
    self.developer_field_definition_count = 0
    self.developer_field_definitions = list()

    # Make it easier to work with endianness instead of checking architecture being 0 or 1 (which may change in the future, since architecture is 8 bits; endianness is only 1).
    self.endianness = None

  def read_from_file(self, fit_file_path:str, offset:int, record_header:NormalRecordHeader) -> tuple[bool, int]:
    # Trust the contents of the definition message is valid, but verify when possible.
    valid = True
    record_size = 0

    # Ensure the record header is the normal type (needs to be to determine if there are developer field definitions).
    if isinstance(record_header, NormalRecordHeader):
      self.header = record_header

      with open(file=fit_file_path, mode="rb") as fit_file:
        fit_file.seek(offset)

        self.reserved = int.from_bytes(fit_file.read(1), byteorder="little")
        self.architecture = int.from_bytes(fit_file.read(1), byteorder="little")
        self.endianness = "little" if self.architecture == 0 else "big"
        self.global_message_number = int.from_bytes(fit_file.read(2), byteorder=self.endianness)
        self.field_definition_count = int.from_bytes(fit_file.read(1), byteorder=self.endianness)

        record_size += 5

        for _ in range(self.field_definition_count):
          fd = FieldDefinition()
          valid = fd.decode([int.from_bytes(fit_file.read(1), byteorder=self.endianness) for _ in range(FIELD_DEFINITION_BYTES)])

          if not valid:
            break

          self.field_definitions.append(fd)
          record_size += FIELD_DEFINITION_BYTES

        if self.header.message_type_specific:
          self.developer_field_definition_count = int.from_bytes(fit_file.read(1), byteorder=self.endianness)

          record_size += 1

          for _ in range(self.developer_field_definition_count):
            dfd = FieldDefinition()
            dfd.decode([int.from_bytes(fit_file.read(1), byteorder=self.endianness) for _ in range(FIELD_DEFINITION_BYTES)])

            if not valid:
              break

            self.developer_field_definitions.append(dfd)
            record_size += FIELD_DEFINITION_BYTES

    return (valid, record_size)

  def __repr__(self):
    fds = [f"{definition.number}: {definition}" for definition in self.field_definitions]

    if self.header.message_type_specific:
      dfds = [f"{definition.number}: {definition}" for definition in self.developer_field_definitions]
      return f"Endianness: {self.endianness}; GMN: {self.global_message_number}; FDC: {self.field_definition_count} ({fds}); DFDC: {self.developer_field_definition_count} ({dfds})"
    else:
      return f"Endianness: {self.endianness}; GMN: {self.global_message_number}; FDC: {self.field_definition_count} ({fds}); DFDC: {self.developer_field_definition_count}"

class MessageDataRecord:
  def __init__(self):
    self.header = None
    self.fields = dict()
    self.developer_fields = dict()

  def read_from_file(self, fit_file_path:str, offset:int, record_header:tuple[NormalRecordHeader, CompressedTimestampRecordHeader], message_defintion_record:MessageDefinitionRecord) -> tuple[bool, int]:
    # Trust the contents of the definition message is valid, but verify when possible.
    valid = True
    record_size = 0

    self.header = record_header

    # Read each field defined in the definition message record.
    with open(file=fit_file_path, mode="rb") as fit_file:
      fit_file.seek(offset)

      for fd in message_defintion_record.field_definitions:
        f = Field(fd)
        # Allow reading invalid field values, but note an error in the log.
        if not f.evaluate(bites=fit_file.read(fd.size), endianness=message_defintion_record.endianness):
          logger.error(f"Failed to evaluate field {fd.number}!")

        self.fields[fd.number] = f
        record_size += fd.size

      for dfd in message_defintion_record.developer_field_definitions:
        df = Field(dfd)
        # Allow reading invalid field values, but note an error in the log.
        if not df.evaluate(bites=fit_file.read(dfd.size), endianness=message_defintion_record.endianness):
          logger.error(f"Failed to evaluate developer field {fd.number}!")

        self.developer_fields[dfd.number] = df
        record_size += dfd.size

    return (valid, record_size)

  def __repr__(self):
    fs = [f"{number}: {field}" for number, field in self.fields.items()]

    if 0 < len(self.developer_fields.keys()):
      dfs = [f"{number}: {developer_field}" for number, developer_field in self.developer_fields.items()]
      return f"Fields: {fs}; Developer Fields: {dfs}"
    else:
      return f"Fields: {fs}"
