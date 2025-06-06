
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

  def __str__(self):
    return f"Message Type: {1 if self.definition_message else 0}; Message Type Specific: {1 if self.extended_developer_definitions else 0}; Local Message Type: {self.local_message_type}"

class CompressedTimestampFitFileRecordHeader:
  MASK_LOCAL_MESSAGE_TYPE = 0b0110_0000
  MASK_TIME_OFFSET = 0b0001_1111

  def __init__(self, local_message_type:int=0, time_offset:int=0):
    self.local_message_type = local_message_type & CompressedTimestampFitFileRecordHeader.MASK_LOCAL_MESSAGE_TYPE
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
      self.local_message_type = serialized & CompressedTimestampFitFileRecordHeader.MASK_LOCAL_MESSAGE_TYPE
      self.time_offset = serialized & CompressedTimestampFitFileRecordHeader.MASK_TIME_OFFSET

    return valid

  def __str__(self):
    return f"Local Message Type: {self.local_message_type >> 5}; Time Offset (seconds): {self.time_offset}"

def deserialize_fit_file_record_header(serialized:int) -> tuple[bool, NormalFitFileRecordHeader | CompressedTimestampFitFileRecordHeader]:
  logger.debug(f"Serialized Record Header: {serialized:02X}")
  fit_file_record_header = CompressedTimestampFitFileRecordHeader() if serialized & MASK_RECORD_HEADER_TYPE == MASK_RECORD_HEADER_TYPE else NormalFitFileRecordHeader()

  valid = fit_file_record_header.deserialize(serialized=serialized)

  return (valid, fit_file_record_header)

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
      self.endianness = "little" if self.architecture == 0 else "big"
      self.global_message_number = int.from_bytes(fit_file.read(2), byteorder=self.endianness)
      self.field_definition_count = int.from_bytes(fit_file.read(1), byteorder=self.endianness)

      record_size += 5
      # print(f"::DMR::read_from_file::size={record_size}")

      # Each field defintion is 3 bytes: Field Defintion Number, Size (in bytes), Base Type
      for _ in range(self.field_definition_count):
        field_definition_number = int.from_bytes(fit_file.read(1), byteorder=self.endianness)
        size = int.from_bytes(fit_file.read(1), byteorder=self.endianness)
        base_type = int.from_bytes(fit_file.read(1), byteorder=self.endianness)

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
          base_type = int.from_bytes(fit_file.read(1), byteorder=self.endianness)

          self.developer_field_definitions.append((field_definition_number, size, base_type))

          record_size += 3
          # print(f"::DMR::read_from_file::size={record_size}")
  
    return (valid, record_size)

  def __str__(self):
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

  def __str__(self):
    return f"[Data Message Record] {[f"{key}: {field}" for key, field in self.fields.items()]}"

class FitFile:
  MAX_LOCAL_MESSAGE_TYPES = 16

  def __init__(self):
    self.header = None
    self.snapshots = list() # Maps a local message type [0,15] to definition message record. TODO: Since a new definition message record could redefine a local message type, each record will have an associated snapshot.

    next_snapshot = dict()
    for local_message_type in range(FitFile.MAX_LOCAL_MESSAGE_TYPES):
      next_snapshot[local_message_type] = None

    self.snapshots.append(next_snapshot) # Ensure at least one snapshot is ready to go.

    self.records = list()
    self.crc = None

  def read_from_file(self, fit_file_path:str) -> int:
    record_count = 0
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
              offset += size
              data_size_remaining -= size

              logger.debug(f"[Record {record_count + 1} Content ({size} bytes)]")
              logger.debug(definition_record)

              # Associate the local message type in the record header to the definition message record.
              self.snapshots[record_count][record_header.local_message_type] = definition_record
              logger.debug(f"Mapped LMT:{record_header.local_message_type} to GMN:{definition_record.global_message_number}")
            else:
              logger.debug(f"File offset: {offset:08X}")
              logger.debug(f"LMT:GMN Mappings: {self.snapshots[record_count]}")
              # Grab a data message record. Note that the data message record's local_message_type must be previously defined in order to grab the contents correctly.
              data_record = DataMessageRecord()
              successful, size = data_record.read_from_file(fit_file_path=fit_file_path, offset=offset, definition_message_record=self.snapshots[record_count][record_header.local_message_type])
              offset += size
              data_size_remaining -= size

              logger.debug(f"[Record {record_count + 1} Content ({size} bytes)]")
              logger.debug(data_record)

            if successful:
              # Generate a new message mapping snapshot.
              last_snapshot = self.snapshots[-1]
              next_snapshot = dict()

              next_snapshot.update(last_snapshot)
              self.snapshots.append(next_snapshot)

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
