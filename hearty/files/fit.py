
from collections import OrderedDict # Let the container maintain the sorted keys instead of sorting each time.

from ..protocols.fit.encoded.field import FieldDefinition, FIELD_DEFINITION_BYTES, Field
from ..protocols.fit.encoded.record import NormalRecordHeader, CompressedTimestampRecordHeader, decode_record_header

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

      # Each field defintion is 3 bytes: Field Defintion Number, Size (in bytes), Base Type
      for _ in range(self.field_definition_count):
        fd = FieldDefinition()
        valid = fd.decode([int.from_bytes(fit_file.read(1), byteorder=self.endianness) for _ in range(FIELD_DEFINITION_BYTES)])

        if not valid:
          break

        self.field_definitions.append(fd)
        record_size += FIELD_DEFINITION_BYTES

      # The record header indicates if there are developer field definitions.
      if has_developer_fields:
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

      for fd in definition_message_record.field_definitions:
        f = Field(fd)
        if f.evaluate(bytes=fit_file.read(fd.size), endianness=definition_message_record.endianness):
          self.fields[fd.number] = f
        # self.fields[fd.number] = (fd.base_type, int.from_bytes(fit_file.read(fd.size), byteorder=definition_message_record.endianness))
        record_size += fd.size

      for dfd in definition_message_record.developer_field_definitions:
        df = Field(dfd)
        if df.evaluate(bytes=fit_file.read(dfd.size), endianness=definition_message_record.endianness):
          self.developer_fields[dfd.number] = df
        # self.developer_fields[dfd.number] = (dfd.base_type, int.from_bytes(fit_file.read(dfd.size), byteorder=definition_message_record.endianness))
        record_size += dfd.size
  
    return (valid, record_size)

  def __repr__(self):
    return f"[Data Message Record] {[f"{key}: {field}" for key, field in self.fields.items()]}"

class FitMesssageRecord:
  """
  Combines defintion and data message records from a FIT file into one message record.
  """
  def __init__(self, definition:DefinitionMessageRecord, data:DataMessageRecord):
    self.global_message_number = definition.global_message_number

    self.fields = OrderedDict()

    for field in sorted([fd.number for fd in definition.field_definitions]):
      self.fields[field] = data.fields[field]

    self.developer_fields = OrderedDict()

    for developer_field in sorted([dfd.number for dfd in definition.developer_field_definitions]):
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

      # Note (2025-06-14@0300 UTC): Happened to be watching WyoOS's Context-Free Grammars: LR(k) Grammars video
      # (https://www.youtube.com/watch?v=FtxJylkW7Oo&list=PLHh55M_Kq4OAmzC6zR7NXhZT9z21NkRCa&index=5)
      # And it made me realize maybe there's a grammar-based way to read the file?
      # Maybe. Maybe not. Just had the idea.

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
          successful, record_header = decode_record_header(fit_file.read(1)[0])
          offset += 1
          data_size_remaining -= 1

          logger.debug(f"[Record {record_count + 1} Header]: {record_header}")

          # But verify, of course.
          if successful:
            if isinstance(record_header, NormalRecordHeader) and record_header.message_type:
              logger.debug(f"File offset: {offset:08X}")
              # Grab a definition message record.
              definition_record = DefinitionMessageRecord()
              successful, size = definition_record.read_from_file(fit_file_path=fit_file_path, offset=offset, has_developer_fields=record_header.message_type_specific)

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
