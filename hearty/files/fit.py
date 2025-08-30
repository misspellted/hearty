
from collections import OrderedDict # Let the container maintain the sorted keys instead of sorting each time.

from ..protocols.fit.encoded.field import FieldDefinition, FIELD_DEFINITION_BYTES, Field
from ..protocols.fit.encoded.record import decode_record_header, NormalRecordHeader, MessageDefinitionRecord, MessageDataRecord
from ..protocols.fit.decoded.message import FitMessage

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

class FitFile:
  MAX_LOCAL_MESSAGE_TYPES = 16

  def __init__(self):
    self.header = None
    self.records = list()
    self.messages = list()
    self.crc = None

  def read_from_file(self, fit_file_path:str) -> int:
    logger.info(f"FIT file: {fit_file_path}")

    record_count = 0
    snapshots = list() # Maps a local message type [0,15] to definition message record.

    next_snapshot = dict()
    for local_message_type in range(FitFile.MAX_LOCAL_MESSAGE_TYPES):
      next_snapshot[local_message_type] = None

    snapshots.append(next_snapshot) # Ensure at least one snapshot is ready to go.

    self.header = FitFileHeader()

    if self.header.read_from_file(fit_file_path=fit_file_path):
      logger.info(f"Protocol version: {self.header.protocol_version}")
      logger.info(f"Profile version: {self.header.profile_version}")
      logger.info(f"FIT data size (bytes): {self.header.data_size}")

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
              definition_record = MessageDefinitionRecord()
              successful, size = definition_record.read_from_file(fit_file_path=fit_file_path, offset=offset, record_header=record_header)

              if successful:
                offset += size
                data_size_remaining -= size
                self.records.append(definition_record)

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
              data_record = MessageDataRecord()
              definition_record = snapshots[record_count][record_header.local_message_type]
              successful, size = data_record.read_from_file(fit_file_path=fit_file_path, offset=offset, record_header=record_header, message_defintion_record=definition_record)

              if successful:
                offset += size
                data_size_remaining -= size
                self.records.append(data_record)

                logger.debug(f"[Record {record_count + 1} Content ({size} bytes)]")
                logger.debug(data_record)

                self.messages.append(FitMessage(definition=definition_record, data=data_record))
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
