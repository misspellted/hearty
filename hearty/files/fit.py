
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

def deserialize_fit_file_record_header(serialized:int) -> tuple[bool, NormalFitFileRecordHeader | CompressedTimestampFitFileRecordHeader]:
  fit_file_record_header = CompressedTimestampFitFileRecordHeader() if serialized & MASK_RECORD_HEADER_TYPE == MASK_RECORD_HEADER_TYPE else NormalFitFileRecordHeader()

  valid = fit_file_record_header.deserialize(serialized=serialized)

  return (valid, fit_file_record_header)

# Mapp the local_message_type records to global_message_number message definitions.
class FitFileMessageMapping:
  def __init__(self):
    self.snapshots = list() # Since they can be redefined in the file, the tracking can't simply have just a list, a dictionary, or a dictionary of lists. It needs to be a list of dictionaries.

class FitFile:
  MAX_LOCAL_MESSAGE_TYPES = 16

  def __init__(self):
    self.header = None
    self.snapshots = list() # Maps a local message type [0,15] to global message number [0,65535]. TODO: Since a new definition message record could redefine a local message type, each record will have an associated snapshot.

    next_snapshot = dict()
    for local_message_type in range(FitFileMessageMapping.MAX_LOCAL_MESSAGE_TYPES): # TODO: Is there a default lmt->gmn mapping?
      next_snapshot[local_message_type] = -1 # 0 - 65535 for the global message number range.

    self.snapshots.append(next_snapshot) # Ensure at least one snapshot is ready to go.

    self.records = list()
    self.crc = None

  def read_from_file(self, fit_file_path:str) -> int:
    record_count = 0
    self.header = FitFileHeader()

    if self.header.read_from_file(fit_file_path=fit_file_path):
      with open(file=fit_file_path, mode="rb") as fit_file:
        # Skip to the start of records.
        fit_file.seek(offset=self.header.size)

        # Trust that the file is properly structured.
        successful = True
        while successful:
          # Read the record header.
          successful, record_header = deserialize_fit_file_record_header(fit_file.read(1)[0])

          # DEBUG
          print(record_header)
          successful = False

          # But verify, of course.
          if successful:
            if isinstance(self.header, NormalFitFileRecordHeader) and self.header.definition_message:
              # TODO: Grab a definition message record.
              # successful, definition_message_record = deserialize_fit_file_definition_message_record()

              if successful:
                # Generate a new message mapping snapshot.
                last_snapshot = self.snapshots[-1]
                next_snapshot = dict()

                next_snapshot.update(last_snapshot)
                self.snapshots.append(next_snapshot)

                # TODO: Update the snapshots with the new local message type to global message number mapping.
            else:
              # TODO: Grab a data message record. Note that the data message record's local_message_type must be previously defined in order to grab the contents correctly.
              # successful, data_message_record = deserialize_fit_file_data_message_record()
              pass

            if successful:
              record_count += 1

      # TODO: Read the CRC.
      pass

    return record_count
