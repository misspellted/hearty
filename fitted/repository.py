
from .util import chunked_sha3_512_hex

from hearty.files.fit import FitFile
from hearty.files.xml import GarminDeviceXml
from hearty.protocols.fit.messages import global_messages, FileIdMessage

import os, shutil

class FitFilesRepository:
  """
  A repository of FIT files.
  """
  def __init__(self, root_directory_path:str):
    self.root_directory_path = root_directory_path
    self.existing_hashes:list[str] = []

  def load(self) -> int:
    """
    Loads the existing hashes of the FIT files in the respository.
    """
    self.existing_hashes.extend(sorted(os.listdir(self.root_directory_path) if os.path.isdir(self.root_directory_path) else []))

    return len(self.existing_hashes)

  def scan(self, dump_directory:str) -> bool:
    """
    Scans a directory containing subdirectories and files "dumped" from a FIT device to determine if it can be read into the repository.

    The expectation is that the directory provided contains both DEVICE.FIT and GarminDevice.xml files, in addition to the subdirectories containing additional files dumped from the device.
    """
    result = False

    if os.path.isdir(dump_directory):
      ddfp = os.path.join(dump_directory, "DEVICE.FIT")
      device_fit_exists = os.path.exists(ddfp)
      # Although, if it's not a Garmin FIT device, such as a scale made by FitBit (they don't utilize the FIT protocol, but just as a thought experiement), would they have their own XML file?
      # TODO: So maybe scan DEVICE.FIT to determine what manufacturer is involved, and then scan for that device manufacturer's XML file.

      device_manufacturer = None
      device_product = None
      device_serial_number = None

      if device_fit_exists:
        ddff = FitFile()
        record_count = ddff.read_from_file(ddfp)

        print(f"\n\n<<< FitFile.read_from_file({ddfp}) >>>")

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

        print(f">>> FitFile.read_from_file({ddfp}) <<<\n\n")

      device_xml_exists = False
      ddxp:str = None

      # For now, assume Garmin is manufacturer 1.
      if device_manufacturer == 1:
        ddxp = os.path.join(dump_directory, GarminDeviceXml.FILE_NAME)

      if ddxp != None:
        device_xml_exists = os.path.exists(ddxp)

        if device_xml_exists:
          ddxf = GarminDeviceXml()
          ddxf.read_from_file(ddxp)

          print(f"\n\n<<< GarminDeviceXml.read_from_file({ddxp}) >>>")
          
          print(f"\tSchema: {ddxf.schema}")
          print(f"\tDevice: {ddxf.device}")

          print(f"\n\n>>> GarminDeviceXml.read_from_file({ddxp}) <<<")

      result = device_fit_exists and device_xml_exists

    return result

  def on_drop(self, file_path:str, reason:str) -> bool:
    """
    Handles the notification of a file to be deleted, allowing interception of the file deletion (return False).

    By default, returns True to indicate the file should be deleted.
    """
    return True

  def drop(self, file_path:str, reason:str):
    """
    Deletes a file.
    """
    if self.on_drop(file_path, reason):
      os.remove(file_path)

  def on_read(self, file_path:str, hash:str, hash_file_path:str):
    """
    Handles the notification that a file was read into the repository.

    By default, does nothing.
    """
    pass

  def read(self, dump_directory:str) -> dict[str, tuple[str, str]]:
    """
    Reads a directory containing subdirectories and files "dumped" from a FIT device into the repository.

    The expectation is that the provided directory has already been scanned and found to be readable into the repository, but this method will invoke scan() to simplify usage.
    """
    result:dict[str, tuple[str, str]] = {}

    scan_result = self.scan(dump_directory)

    if scan_result:
      for current_directory, subdirectories, files in os.walk(dump_directory):
        for file in files:
          file_path = os.path.join(current_directory, file)

          # Note: Previous/ongoing work in the PyFR project (local for now) resulted in what was termed "time-streams",
          # or a timestamped reconstruction of a FIT file; these files were given the .FITS extension. This occurred
          # near the beginning of understanding the FIT protocol; however, it is now expected to run this collector to
          # provide a consolidated unique set of files to parse later. So, if they are encountered (such as testing
          # this work with, say a backup set of dumps, such FITS files might still be encountered). As they can be
          # regenerated, it is safe to just delete them from the dump directory, since they are not part of the actual
          # file dump process.
          if file_path.endswith(".FITS"):
            self.drop(file_path, "PyFR 'FITS' file not original data dump file; this file could be recrated later on, depending on reworked PyFR work or PyFR incorporation into this project.")
          else:
            file_contents_hash = chunked_sha3_512_hex(file_path)

            # Note: Since the hash is based on the contents of the file, not the path/name, it should be safe to consider
            # each hash as unique (enough for the purpose this collection; a collision is not anticipated). As a result,
            # if a dump directory contains a file that hashes to one already in the existing collection, it is assumed
            # to be a duplicate (caught myself typing 'dumplic' there before getting it right, hahaha!), and as such,
            # it can be deleted.
            if file_contents_hash in self.existing_hashes:
              self.drop(file_path, f"Deleting {file_path} as {file_contents_hash} already exists; assuming it is a duplicate from previous dump.")
            else:
              # TODO: Absorb the ::move() method here.
              # self.move(current_directory, file_path, file_contents_hash)

              # Get the relative path in the dump directory for the file.
              rel_file_path = file_path.removeprefix(f"{current_directory}{os.path.sep}")
              rfp_parts = rel_file_path.split(os.path.sep)
              rel_directory, rel_file = ("_", rfp_parts[0]) if len(rfp_parts) < 2 else (rfp_parts[0], rfp_parts[1])

              # Create the directory ready for the file move.
              hash_directory = os.path.join(self.root_directory_path, file_contents_hash)
              hash_file_directory = os.path.join(hash_directory, rel_directory)

              # The hash directory shouldn't already exist, if the anticipated state of the existing collection is maintained.
              os.makedirs(hash_file_directory, exist_ok=False)

              # Then move the file into the collection.
              hash_directory_file = os.path.join(hash_file_directory, rel_file_path)
              shutil.move(file_path, hash_directory_file)

              # Verify the move was successful.
              if os.path.isfile(hash_directory_file):
                # If it exists, we can clean up the old file if it still exists (not sure how each platform moves (actual vs copied)...).
                if os.path.isfile(file_path):
                  self.drop(file_path, f"Deleting {file_path} as it was successfully copied to {hash_directory_file}.")

                self.on_read(file_path, file_contents_hash, hash_directory_file)
              
              # Else, exit immediately.
              else:
                exit(f"Error in moving/copying {file_path} to {hash_file_directory}; exiting...")

              # And track the move for later reporting (if the user wants such).
              result[file_contents_hash] = (file_path, hash_directory_file)

    return result
