
from hearty.files.fit import FitFile
from hearty.files.xml import GarminDeviceXml
from hearty.protocols.fit.messages import global_messages, FileIdMessage
from hearty.repositories.base import UniqueFilesRepository
from hearty.repositories.hashers import sha3_512

import os

class FitDeviceFiles(UniqueFilesRepository):
  """
  A collection of files that are unique from multiple "dump" directories associated with a Garmin FIT protocol device.

  SHA3-512 is the hashing algorithm utilized for enough-uniqueness calculations.
  """
  def __init__(self, root_directory_path:str):
    UniqueFilesRepository.__init__(self, root_directory_path, sha3_512)

  def scan(self, dump_directory:str) -> bool:
    """
    Scans a directory containing subdirectories and files "dumped" from a FIT device to determine if it can be read into the repository.

    The expectation is that the directory provided contains both DEVICE.FIT and GarminDevice.xml files, in addition to the subdirectories containing additional files dumped from the device.
    """
    result = UniqueFilesRepository.scan(self, dump_directory)

    if result:
      ddfp = os.path.join(dump_directory, "DEVICE.FIT")
      device_fit_exists = os.path.exists(ddfp)

      # For now, assume Garmin is the manufacturer.
      ddxp = os.path.join(dump_directory, GarminDeviceXml.FILE_NAME)
      device_xml_exists = os.path.exists(ddxp)

      result = device_fit_exists and device_xml_exists

    return result

  def on_file(self, file_path:str) -> bool:
    resume = True

    # Note: Previous/ongoing work in the PyFR project (local for now) resulted in what was termed "time-streams",
    # or a timestamped reconstruction of a FIT file; these files were given the .FITS extension. This occurred
    # near the beginning of understanding the FIT protocol; however, it is now expected to run this collector to
    # provide a consolidated unique set of files to parse later. So, if they are encountered (such as testing
    # this work with, say a backup set of dumps, such FITS files might still be encountered). As they can be
    # regenerated, it is safe to just delete them from the dump directory, since they are not part of the actual
    # file dump process.
    if file_path.endswith(".FITS"):
      self.drop(file_path, "PyFR 'FITS' file not original data dump file; this file could be recrated later on, depending on reworked PyFR work or PyFR incorporation into this project.")
      resume = False

    elif file_path.endswith("DEVICE.FIT"):
      device_manufacturer = None
      device_product = None
      device_serial_number = None

      ddff = FitFile()
      record_count = ddff.read_from_file(file_path)

      print(f"\n\n<<< FitFile.read_from_file({file_path}) >>>")

      print(f"\tRecord Count: {record_count}")
      print(f"\tMessage Count: {len(ddff.messages)}")

      # To have messages, records are required.
      if 0 < record_count:
        fim:FileIdMessage = None

        for message in ddff.messages:
          if message.global_message_number in global_messages.keys():
            gm = global_messages[message.global_message_number]()
            gm.from_file_message_record(message)

            if isinstance(gm, FileIdMessage):
              fim = gm

        if fim != None:
          print("\tfile_id message:")
          print(f"\t\tType: {fim.type}")
          print(f"\t\tManufacturer: {fim.manufacturer.value}")
          print(f"\t\tProduct: {fim.product}")
          print(f"\t\tSerial Number: {fim.serial_number}")
          print(f"\t\tTime Created: {fim.time_created}") # Activity (type 4) files have valid time_created values, but type 1 (assuming 'device') files have invalid values 4294967295 (uint32) .. (thinking_face) ..
          print(f"\t\tUnknown Fields? {0 < len(fim.unknown.keys())}")
          for ufdn, ubtn_val in fim.unknown.items():
            print(f"\t\t\t{ufdn}: {ubtn_val}")

          device_manufacturer = fim.manufacturer.value
          device_product = fim.product.value
          device_serial_number = fim.serial_number.value

      print(f">>> FitFile.read_from_file({file_path}) <<<\n\n")

    elif file_path.endswith("GarminDevice.xml"):
      ddxf = GarminDeviceXml()
      ddxf.read_from_file(file_path)

      print(f"\n\n<<< GarminDeviceXml.read_from_file({file_path}) >>>")

      print(f"\tSchema: {ddxf.schema}")
      print(f"\tDevice: {ddxf.device}")

      print(f"\n\n>>> GarminDeviceXml.read_from_file({file_path}) <<<")

    return resume
