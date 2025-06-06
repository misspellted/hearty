
from config import FR35_DUMPS_DIR
from hearty.files.fit import FitFile
import logging
logger = logging.getLogger(__name__)

def main():
  logging.basicConfig(filename="hearty.log", level=logging.DEBUG)
  # fit_file_path = f"{FR35_DUMPS_DIR}/2025-05-24_23-14/DEVICE.FIT" # No errors reading. ^_^
  # fit_file_path = f"{FR35_DUMPS_DIR}/2025-05-24_23-14/ACTIVITY/F3C94745.FIT" # No errors reading. ^_^
  # fit_file_path = f"{FR35_DUMPS_DIR}/2025-05-24_23-14/MONITOR/F5A00000.FIT" # No errors reading. ^_^
  # fit_file_path = f"{FR35_DUMPS_DIR}/2025-05-24_23-14/RECORDS/RECORDS.FIT" # No errors reading. ^_^
  # fit_file_path = f"{FR35_DUMPS_DIR}/2025-05-24_23-14/SETTINGS/SETTINGS.FIT" # No errors reading. ^_^
  fit_file_path = f"{FR35_DUMPS_DIR}/2025-05-24_23-14/SPORTS/0RRUN.FIT" # No errors reading. ^_^

  logger.info(f"Reading {fit_file_path}")
  ff = FitFile()
  record_count = ff.read_from_file(fit_file_path=fit_file_path)
  logger.info(f"Read {record_count} record(s)")
  print(f"Read {record_count} record(s)")

if __name__ == "__main__":
  main()
