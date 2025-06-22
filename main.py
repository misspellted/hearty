
# from config import FR35_DUMPS_DIR
# from hearty.files.fit import FitFile
# import logging
# logger = logging.getLogger(__name__)

# def main():
#   logging.basicConfig(filename="hearty.log", level=logging.DEBUG, filemode="w")
#   # fit_file_path = f"{FR35_DUMPS_DIR}/2025-05-24_23-14/DEVICE.FIT" # No errors reading. ^_^
#   fit_file_path = f"{FR35_DUMPS_DIR}/2025-05-24_23-14/ACTIVITY/F3C94745.FIT" # No errors reading. ^_^
#   # fit_file_path = f"{FR35_DUMPS_DIR}/2025-05-24_23-14/MONITOR/F5A00000.FIT" # No errors reading. ^_^
#   # fit_file_path = f"{FR35_DUMPS_DIR}/2025-05-24_23-14/RECORDS/RECORDS.FIT" # No errors reading. ^_^
#   # fit_file_path = f"{FR35_DUMPS_DIR}/2025-05-24_23-14/SETTINGS/SETTINGS.FIT" # No errors reading. ^_^
#   # fit_file_path = f"{FR35_DUMPS_DIR}/2025-05-24_23-14/SPORTS/0RRUN.FIT" # No errors reading. ^_^

#   logger.info(f"Reading {fit_file_path}")
#   ff = FitFile()
#   record_count = ff.read_from_file(fit_file_path=fit_file_path)
#   logger.info(f"Read {record_count} record(s)")
#   print(f"Read {record_count} record(s)")

#   message_count = len(ff.messages)
#   logger.info(f"Read {message_count} message(s)")
#   print(f"Read {message_count} message(s)")

#   for message in ff.messages:
#     logger.info(message)
#     print(message)

# if __name__ == "__main__":
#   main()

# ================================

# from hearty.protocols.fit.messages import global_messages

# print(global_messages[0x00]()) # Yes, I _know_ it's just 0... but.. it's what was on the documentation page, so... ^_^
# print(global_messages[20]())

# ================================

# now, to combine them! WE HAVE THE POWA... _coughs_ ... I'm getting too old for references, haha!

from config import FR35_DUMPS_DIR
from hearty.files.fit import FitFile
from hearty.protocols.fit.messages import global_messages, FileIdMessage # I has the burger that a chunk of what's in the files.fit 'package' will shift to this one...

import logging
logger = logging.getLogger(__name__)

def main():
  logging.basicConfig(filename="hearty.log", level=logging.DEBUG, filemode="w")
  # Apparently the Garmin Forerunner 35 (m:1/p:2503) emits unknown-to-me FDNs:

  # fit_file_path = f"{FR35_DUMPS_DIR}/2025-05-24_23-14/DEVICE.FIT" # file_id.type => 1 (unknown FDNs - '5': 0 <uint16>) | Also: invalid time_created value (4294967295)
  # fit_file_path = f"{FR35_DUMPS_DIR}/2025-05-24_23-14/ACTIVITY/F3C94745.FIT" # file_id.type => 4 (unknown FDNs - '5': 65535 <uint16, invalid value>)
  # fit_file_path = f"{FR35_DUMPS_DIR}/2025-05-24_23-14/MONITOR/F5A00000.FIT" # file_id.type => 32 (unknown FDNs - '5': 214 <uint16>, '6': 65535 <uint16, invalid value>)
  # fit_file_path = f"{FR35_DUMPS_DIR}/2025-05-24_23-14/RECORDS/RECORDS.FIT" # file_id.type => 29 (unknown FDNs - '5': 0 <uint16>) | Also: invalid time_created value (4294967295)
  # fit_file_path = f"{FR35_DUMPS_DIR}/2025-05-24_23-14/SETTINGS/SETTINGS.FIT" # file_id.type => 2 (unknown FDNs - '5': 0 <uint16>) | Also: invalid time_created value (4294967295)
  fit_file_path = f"{FR35_DUMPS_DIR}/2025-05-24_23-14/SPORTS/0RRUN.FIT" # file_id.type => 3 (unknown FDNs - '5': 0 <uint16>) | Also: invalid time_created value (4294967295)

  logger.info(f"Reading {fit_file_path}")
  print(f"Reading {fit_file_path}")
  ff = FitFile()
  record_count = ff.read_from_file(fit_file_path=fit_file_path)
  logger.info(f"Read {record_count} record(s)")
  print(f"Read {record_count} record(s)")

  message_count = len(ff.messages)
  logger.info(f"Read {message_count} message(s)")
  print(f"Read {message_count} message(s)")

  fim = None

  for message in ff.messages:
    logger.info(message)
    # print(message)

    if message.global_message_number in global_messages.keys():
      gm = global_messages[message.global_message_number]()
      gm.from_file_message_record(message)

      if isinstance(gm, FileIdMessage):
        fim = gm
  
  if fim != None:
    print("file_id message:")
    print(f"\tType: {fim.type}")
    print(f"\tManufacturer: {fim.manufacturer}")
    print(f"\tProduct: {fim.product}")
    print(f"\tSerial Number: {fim.serial_number}")
    print(f"\tTime Created: {fim.time_created}") # Activity (type 4) files have valid time_created values, but type 1 (assuming 'device') files have invalid values 4294967295 (uint32) .. (thinking_face) ..
    print(f"\tUnknown Fields? {0 < len(fim.unknown.keys())}")
    for ufdn, ubtn_val in fim.unknown.items():
      print(f"\t\t{ufdn}: {ubtn_val}")

if __name__ == "__main__":
  main()
