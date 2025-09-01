
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
    1: "Garmin", # Based on DEVICE.FIT files coming from a Garmin Forerunner 35
    15: "Dynastream", # Also according to https://developer.garmin.com/fit/protocol/#record2datamessage:file_idlocalmsgtype0
  }

  PRODUCTS = {
    1: {
      2503: "Forerunner 35" # Based on DEVICE.FIT files coming from a Garmin Forerunner 35
    },
    15: {
      22: "<not yet identified>" # As seen on https://developer.garmin.com/fit/protocol/#record2datamessage:file_idlocalmsgtype0
    },
  }

  def __init__(self):
    self.unknown = OrderedDict()

  def from_file_message_record(self, file_message_record):
    for fdn, btn_val in file_message_record.fields.items():
      if fdn in FileIdMessage.FIELDS:
        setattr(self, FileIdMessage.FIELDS[fdn], btn_val)
      else:
        self.unknown[fdn] = btn_val

    for dfdn, dbtn_val in file_message_record.developer_fields:
      pass

def new_file_id_message():
  return FileIdMessage()
