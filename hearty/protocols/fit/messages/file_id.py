
from collections import OrderedDict

class FileIdMessage:
  GLOBAL_MESSAGE_NUMBER = 0x00 # As shown on https://developer.garmin.com/fit/protocol/#record1definitionmessage:file_idmesg_num0x00.

  FIELDS = {
    0: "type",          # Field Definition Number: 0; Size: 1 byte; Base Type: 0 (enum)
    1: "manufacturer",  # Field Definition Number: 1; Size: 2 bytes; Base Type: 132 (uint16)
    2: "product",       # Field Definition Number: 2; Size: 2 bytes; Base Type: 132 (uint16)
    3: "serial_number", # Field Definition Number: 3; Size: 4 byte2; Base Type: 140 (uint32z)
    4: "time_created",  # Field Definition Number: 4; Size: 4 byte2; Base Type: 134 (uint32)
  }

  TYPES = {
    4: "activity", # According to https://developer.garmin.com/fit/protocol/#record2datamessage:file_idlocalmsgtype0
  }

  MANUFACTURERS = {
    15: "Dynastream" # Also according to https://developer.garmin.com/fit/protocol/#record2datamessage:file_idlocalmsgtype0
  }

  PRODUCTS = {
    15: {
      22: "<not yet identified>" # As seen on https://developer.garmin.com/fit/protocol/#record2datamessage:file_idlocalmsgtype0
    },
  }

  # As visible on https://developer.garmin.com/fit/protocol/#record2datamessage:file_idlocalmsgtype0, time_created having a value of 621463080 corresponds to 14 Aug 2009. # TODO: Is the time_created field in Unix epoch seconds?

  def __init__(self):
    self.unknown = OrderedDict()

  def from_file_message_record(self, file_message_record):
    for fdn, btn_val in file_message_record.fields.items():
      if fdn in FileIdMessage.FIELDS:
        setattr(self, FileIdMessage.FIELDS[fdn], btn_val[1]) # TODO: Evaluate the value through the base type. # TODO: Ensure the base type from the file record is expected (as noted above).
      else:
        self.unknown[fdn] = btn_val

    for dfdn, dbtn_val in file_message_record.developer_fields:
      pass
      # TODO: Can the FileId message have developer fields?
      # Well, maybe, since in the exampe at https://developer.garmin.com/fit/protocol/#record7definitionmessage:recordmesg_num0x14 shows the global message 20 (Record) as having being redefined to include developer fields. (thinking_face)

def new_file_id_message():
  return FileIdMessage()
