
from collections import OrderedDict # Let the container maintain the sorted keys instead of sorting each time.

import logging
logger = logging.getLogger(__name__)

class FitFileHeader:
  SIZE = 12
  SIZE_CRC = 14 # Adds the 2-byte CRC at the end.

  def __init__(self):
    self.size = None
    self.protocol_version = None
    self.profile_version = None
    self.data_size = None
    self.data_type = None
    self.crc = None

  def read_from_file(self, fit_file_path:str) -> bool:
    # Trust the header of the file is valid, but verify when possible.
    valid = True

    with open(file=fit_file_path, mode="rb") as fit_file:
      self.size = int.from_bytes(fit_file.read(1), byteorder="little")
      valid = self.size in [FitFileHeader.SIZE, FitFileHeader.SIZE_CRC]

      if valid:
        self.protocol_version = int.from_bytes(fit_file.read(1), byteorder="little")
        self.profile_version = int.from_bytes(fit_file.read(2), byteorder="little")
        self.data_size = int.from_bytes(fit_file.read(4), byteorder="little")
        self.data_type = str(fit_file.read(4), encoding="ascii")

        valid = self.data_type == ".FIT"

        if valid and FitFileHeader.SIZE_CRC <= self.size:
          self.crc = f"{int.from_bytes(fit_file.read(2), byteorder="little"):04X}"

          # TODO: Validate the CRC is correct.
  
    return valid

MASK_RECORD_HEADER_TYPE = 0b1000_0000

class NormalFitFileRecordHeader:
  MASK_MESSAGE_TYPE = 0b0100_0000
  MASK_MESSAGE_TYPE_SPECIFIC = 0b0010_0000
  MASK_RESERVED = 0b0001_0000
  MASK_LOCAL_MESSAGE_TYPE = 0b0000_1111

  def __init__(self, definition_message:bool=False, extended_developer_definitions:bool=False, local_message_type:int=0):
    self.definition_message = definition_message
    self.extended_developer_definitions = extended_developer_definitions
    self.local_message_type = local_message_type & NormalFitFileRecordHeader.MASK_LOCAL_MESSAGE_TYPE

  def serialize(self) -> int:
    # Start off with setting the normal header flag (0).
    serialized = 0b0000_0000

    # Then the message type field.
    serialized |= (NormalFitFileRecordHeader.MASK_MESSAGE_TYPE if self.definition_message else 0)

    # Followed by the message type specific field.
    serialized |= (NormalFitFileRecordHeader.MASK_MESSAGE_TYPE_SPECIFIC if self.definition_message and self.extended_developer_definitions else 0)

    # And finally the local message type bits.
    serialized |= (NormalFitFileRecordHeader.MASK_LOCAL_MESSAGE_TYPE & self.local_message_type)

    return serialized

  def deserialize(self, serialized:int) -> bool:
    valid = (serialized & MASK_RECORD_HEADER_TYPE) == 0b0000_0000

    if valid:
      self.definition_message = (serialized & NormalFitFileRecordHeader.MASK_MESSAGE_TYPE) == NormalFitFileRecordHeader.MASK_MESSAGE_TYPE

      if self.definition_message:
        self.extended_developer_definitions = (serialized & NormalFitFileRecordHeader.MASK_MESSAGE_TYPE_SPECIFIC) == NormalFitFileRecordHeader.MASK_MESSAGE_TYPE_SPECIFIC
  
      self.local_message_type = (serialized & NormalFitFileRecordHeader.MASK_LOCAL_MESSAGE_TYPE)

    return valid

  def __repr__(self):
    return f"Message Type: {1 if self.definition_message else 0}; Message Type Specific: {1 if self.extended_developer_definitions else 0}; Local Message Type: {self.local_message_type}"

class CompressedTimestampFitFileRecordHeader:
  MASK_LOCAL_MESSAGE_TYPE = 0b0110_0000
  MASK_TIME_OFFSET = 0b0001_1111

  def __init__(self, local_message_type:int=0, time_offset:int=0):
    self.local_message_type = ((local_message_type << 5) & CompressedTimestampFitFileRecordHeader.MASK_LOCAL_MESSAGE_TYPE) >> 5
    self.time_offset = time_offset & CompressedTimestampFitFileRecordHeader.MASK_TIME_OFFSET

  def serialize(self) -> int:
    # Start off with setting the normal header flag (0).
    serialized = MASK_RECORD_HEADER_TYPE

    # Then the local message type bits.
    serialized |= CompressedTimestampFitFileRecordHeader.MASK_LOCAL_MESSAGE_TYPE & self.local_message_type

    # And finally the time offset bits.
    serialized |= CompressedTimestampFitFileRecordHeader.MASK_TIME_OFFSET & self.time_offset

    return serialized

  def deserialize(self, serialized:int) -> bool:
    valid = (serialized & MASK_RECORD_HEADER_TYPE) == MASK_RECORD_HEADER_TYPE

    if valid:
      self.local_message_type = (serialized & CompressedTimestampFitFileRecordHeader.MASK_LOCAL_MESSAGE_TYPE) >> 5
      self.time_offset = serialized & CompressedTimestampFitFileRecordHeader.MASK_TIME_OFFSET

    return valid

  def __repr__(self):
    return f"Local Message Type: {self.local_message_type}; Time Offset (seconds): {self.time_offset}"

def deserialize_fit_file_record_header(serialized:int) -> tuple[bool, NormalFitFileRecordHeader | CompressedTimestampFitFileRecordHeader]:
  logger.debug(f"Serialized Record Header: {serialized:02X}")
  fit_file_record_header = CompressedTimestampFitFileRecordHeader() if serialized & MASK_RECORD_HEADER_TYPE == MASK_RECORD_HEADER_TYPE else NormalFitFileRecordHeader()

  valid = fit_file_record_header.deserialize(serialized=serialized)

  return (valid, fit_file_record_header)


class FieldBaseType:
  MASK_HAS_ENDIANNESS = 0b1000_0000
  MASK_RESERVED = 0b0110_0000
  MASK_BASE_TYPE_NUMBER = 0b0001_1111
  MIN_BASE_TYPE_NUMBER = 0
  MAX_BASE_TYPE_NUMBER = 16 # So far, anyways. By bits, this should be 31 ('for future use' is the assumption).

  # From Table 7: "FIT Base Types and Invalid Values" @ https://developer.garmin.com/fit/protocol/#basetype
  # (base_type_fied, type_name, invalid_value)
  BASE_TYPES = {
    0: (0x00, "enum", 0xFF),
    1: (0x01, "sint8", 0x7F), # 2's complement format
    2: (0x02, "uint8", 0xFF),
    3: (0x83, "sint16", 0x7FFF), # 2's complement format
    4: (0x84, "uint16", 0xFFFF),
    5: (0x85, "sint32", 0x7FFFFFFF), # 2's complement format
    6: (0x86, "uint32", 0xFFFFFFFF),
    7: (0x07, "string", 0x00), # Null-terminated string encoded in UTF-8
    8: (0x88, "float32", 0xFFFFFFFF),
    9: (0x89, "float64", 0xFFFFFFFFFFFFFFFF),
    10: (0x0A, "uint8z", 0x00),
    11: (0x8B, "uint16z", 0x0000),
    12: (0x8C, "uint32z", 0x00000000),
    13: (0x0D, "byte", 0xFF), # Array of bytes. Field is invalid if all bytes are invalid
    14: (0x8E, "sint64", 0x7FFFFFFFFFFFFFFF), # 2's complement format
    15: (0x8F, "uint64", 0xFFFFFFFFFFFFFFFF),
    16: (0x90, "uint64z", 0x0000000000000000),
  }

  def __init__(self, has_endianness:bool=True, base_type_number:int=0):
    self.has_endianness = has_endianness
    self.reserved = 0
    self.base_type_number = base_type_number

  def deserialize(self, serialized:int) -> bool:
    self.has_endianness = (serialized & FieldBaseType.MASK_HAS_ENDIANNESS) == FieldBaseType.MASK_HAS_ENDIANNESS
    self.reserved = (serialized & FieldBaseType.MASK_RESERVED) >> 5
    self.base_type_number = serialized & FieldBaseType.MASK_BASE_TYPE_NUMBER

    return self.reserved == 0 and FieldBaseType.MIN_BASE_TYPE_NUMBER <= self.base_type_number <= FieldBaseType.MAX_BASE_TYPE_NUMBER

  def serialize(self) -> int:
    serialized = FieldBaseType.MASK_HAS_ENDIANNESS if self.has_endianness else 0

    # Skipping the reserved for now.

    serialized |= FieldBaseType.MAX_BASE_TYPE_NUMBER if FieldBaseType.MAX_BASE_TYPE_NUMBER < self.base_type_number else self.base_type_number & FieldBaseType.MASK_BASE_TYPE_NUMBER

    return serialized

  def get_type_name(self):
    return FieldBaseType.BASE_TYPES[self.base_type_number][1]

  def get_invalid_value(self):
    return FieldBaseType.BASE_TYPES[self.base_type_number][2]

  def __repr__(self):
    return f"{self.get_type_name()}!{self.get_invalid_value()}"

class DefinitionMessageRecord:
  def __init__(self):
    self.reserved = None
    self.architecture = None
    self.endianness = None
    self.global_message_number = None
    self.field_definition_count = 0
    self.field_definitions = list()
    self.developer_field_definition_count = 0
    self.developer_field_definitions = list()

  def read_from_file(self, fit_file_path:str, offset:int, has_developer_fields:bool) -> tuple[bool, int]:
    # Trust the contents of the definition message is valid, but verify when possible.
    valid = True
    record_size = 0

    with open(file=fit_file_path, mode="rb") as fit_file:
      fit_file.seek(offset)
      
      self.reserved = int.from_bytes(fit_file.read(1), byteorder="little")
      self.architecture = int.from_bytes(fit_file.read(1), byteorder="little")
      self.endianness = "little" if self.architecture == 0 else "BIG"
      self.global_message_number = int.from_bytes(fit_file.read(2), byteorder=self.endianness)
      self.field_definition_count = int.from_bytes(fit_file.read(1), byteorder=self.endianness)

      record_size += 5
      # print(f"::DMR::read_from_file::size={record_size}")

      # Each field defintion is 3 bytes: Field Defintion Number, Size (in bytes), Base Type
      for _ in range(self.field_definition_count):
        field_definition_number = int.from_bytes(fit_file.read(1), byteorder=self.endianness)
        size = int.from_bytes(fit_file.read(1), byteorder=self.endianness)

        base_type = FieldBaseType()
        base_type.deserialize(int.from_bytes(fit_file.read(1), byteorder=self.endianness))

        self.field_definitions.append((field_definition_number, size, base_type))

        record_size += 3
        # print(f"::DMR::read_from_file::size={record_size}")

      # The record header indicates if there are developer field definitions.
      if has_developer_fields:
        self.developer_field_definition_count = int.from_bytes(fit_file.read(1), byteorder=self.endianness)

        record_size += 1
        # print(f"::DMR::read_from_file::size={record_size}")

        for _ in ran(self.developer_field_definition_count):
          field_definition_number = int.from_bytes(fit_file.read(1), byteorder=self.endianness)
          size = int.from_bytes(fit_file.read(1), byteorder=self.endianness)

          base_type = FieldBaseType()
          base_type.deserialize(int.from_bytes(fit_file.read(1), byteorder=self.endianness))

          self.developer_field_definitions.append((field_definition_number, size, base_type))

          record_size += 3
          # print(f"::DMR::read_from_file::size={record_size}")
  
    return (valid, record_size)

  def __repr__(self):
    return f"[Definition Message Record] Endianness: {self.endianness}; GMN: {self.global_message_number}; FDC: {self.field_definition_count}; DFDC: {self.developer_field_definition_count}"

class DataMessageRecord:
  def __init__(self):
    self.fields = dict()
    self.developer_fields = dict()

  def read_from_file(self, fit_file_path:str, offset:int, definition_message_record:DefinitionMessageRecord) -> tuple[bool, int]:
    # Trust the contents of the definition message is valid, but verify when possible.
    valid = True
    record_size = 0

    # Read each field defined in the definition message record.
    with open(file=fit_file_path, mode="rb") as fit_file:
      fit_file.seek(offset)

      for field_definition in definition_message_record.field_definitions:
        fdn, fds, fdbt = field_definition

        self.fields[fdn] = (fdbt, int.from_bytes(fit_file.read(fds), byteorder=definition_message_record.endianness))
        record_size += fds

      for developer_field_definition in definition_message_record.developer_field_definitions:
        dfdn, dfds, dfdbt = developer_field_definition

        self.developer_fields[dfdn] = (dfdbt, int.from_bytes(fit_file.read(dfds), byteorder=definition_message_record.endianness))
        record_size += dfds
  
    return (valid, record_size)

  def __repr__(self):
    return f"[Data Message Record] {[f"{key}: {field}" for key, field in self.fields.items()]}"

class FitMesssageRecord:
  """
  Combines defintion and data message records from a FIT file into one message record.
  """
  def __init__(self, definition:DefinitionMessageRecord, data:DataMessageRecord):
    self.global_message_number = definition.global_message_number
    self.fields = OrderedDict() # key: (base_data_type: value)

    for field in sorted([fdn for fdn, _, __ in definition.field_definitions]):
      self.fields[field] = data.fields[field]

    self.developer_fields = OrderedDict() # key: (base_data_type: value)

    for developer_field in sorted([dfdn for dfdn, _, __ in definition.developer_field_definitions]):
      self.developer_fields[developer_field] = data.developer_fields[developer_field]

  def __repr__(self):
    idfr = f"[{self.global_message_number}]"
    fds = f"{[f"{key}: {field}" for key, field in self.fields.items()]}"
    dfds = f"{[f"{developer_key}: {developer_field}" for developer_key, developer_field in self.developer_fields.items()]}"
    return f"{idfr} - {fds} + {dfds}" if 0 < len(self.developer_fields.keys()) else f"{idfr} - {fds}"

class FitFile:
  MAX_LOCAL_MESSAGE_TYPES = 16

  def __init__(self):
    self.header = None
    self.records = list()
    self.messages = list()
    self.crc = None

  def read_from_file(self, fit_file_path:str) -> int:
    record_count = 0
    snapshots = list() # Maps a local message type [0,15] to definition message record.

    next_snapshot = dict()
    for local_message_type in range(FitFile.MAX_LOCAL_MESSAGE_TYPES):
      next_snapshot[local_message_type] = None

    snapshots.append(next_snapshot) # Ensure at least one snapshot is ready to go.

    self.header = FitFileHeader()

    if self.header.read_from_file(fit_file_path=fit_file_path):
      offset = self.header.size
      with open(file=fit_file_path, mode="rb") as fit_file:
        # Skip to the start of records.
        fit_file.seek(offset)
        data_size_remaining = self.header.data_size

        # Trust that the file is properly structured.
        successful = True
        while successful and 0 < data_size_remaining:
          logger.debug(f"Data Size Remaining: {data_size_remaining}")
          logger.debug(f"File offset: {offset:08X}")

          # Read the record header.
          fit_file.seek(offset)
          logger.debug(f"Record header peek: {fit_file.peek(1)[0]}")
          successful, record_header = deserialize_fit_file_record_header(fit_file.read(1)[0])
          offset += 1
          data_size_remaining -= 1

          logger.debug(f"[Record {record_count + 1} Header]: {record_header}")

          # But verify, of course.
          if successful:
            if isinstance(record_header, NormalFitFileRecordHeader) and record_header.definition_message:
              logger.debug(f"File offset: {offset:08X}")
              # Grab a definition message record.
              definition_record = DefinitionMessageRecord()
              successful, size = definition_record.read_from_file(fit_file_path=fit_file_path, offset=offset, has_developer_fields=record_header.extended_developer_definitions)

              if successful:
                offset += size
                data_size_remaining -= size

                logger.debug(f"[Record {record_count + 1} Content ({size} bytes)]")
                logger.debug(definition_record)

                # Associate the local message type in the record header to the definition message record.
                snapshots[record_count][record_header.local_message_type] = definition_record
                logger.debug(f"Mapped LMT:{record_header.local_message_type} to GMN:{definition_record.global_message_number}")
              else:
                logger.error(f"Failed to read definition message record at offset {offset - 1}!") # Back track one byte to the start of the record with its header.
                break
            else:
              logger.debug(f"File offset: {offset:08X}")
              logger.debug(f"LMT:GMN Mappings: {snapshots[record_count]}")
              # Grab a data message record. Note that the data message record's local_message_type must be previously defined in order to grab the contents correctly.
              data_record = DataMessageRecord()
              definition_record = snapshots[record_count][record_header.local_message_type]
              successful, size = data_record.read_from_file(fit_file_path=fit_file_path, offset=offset, definition_message_record=definition_record)

              if successful:
                offset += size
                data_size_remaining -= size

                logger.debug(f"[Record {record_count + 1} Content ({size} bytes)]")
                logger.debug(data_record)

                self.messages.append(FitMesssageRecord(definition=definition_record, data=data_record))
              else:
                logger.error(f"Failed to read data message record at offset {offset - 1}!") # Back track one byte to the start of the record with its header.
                break

            if successful:
              # Generate a new message mapping snapshot.
              last_snapshot = snapshots[-1]
              next_snapshot = dict()

              next_snapshot.update(last_snapshot)
              snapshots.append(next_snapshot)

            if successful:
              record_count += 1

        # Read the CRC if the file header indicates one is used.
        if self.header.size == FitFileHeader.SIZE_CRC:
          logger.debug(f"File offset: {offset:08X}")
          fit_file.seek(offset)
          self.crc = int.from_bytes(fit_file.read(FitFileHeader.SIZE_CRC - FitFileHeader.SIZE), byteorder="little")

          # TODO: Verify the CRC.
          logger.debug(f"File CRC: {self.crc:04X}")

    return record_count
