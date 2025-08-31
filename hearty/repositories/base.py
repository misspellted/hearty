
import os, shutil
from collections.abc import Callable

from .hashers import sha3_512

class UniqueFilesRepository:
  """
  A collection of files that are unique from multiple "dump" directories.

  A hashing algorithm (default: SHA3-512) is used to calculate a "unique-enough" identifier per file in the respository.
  """
  def __init__(self, root_directory:str, hasher:Callable[[str, int], str]=sha3_512):
    if not os.path.isdir(root_directory):
      raise ValueError(f"'{root_directory}' is not a path to a directory.")

    self.root_directory:str = root_directory
    self.hasher:Callable[[str, int], str] = hasher
    self.existing_hashes:list[str] = []

  def load(self) -> int:
    """
    Loads the existing unique file hashes from the repository.

    Returns the count of hashes loaded.
    """
    load_count = 0

    loaded:list[str] = sorted(os.listdir(self.root_directory))

    for _ in range(len(loaded)):
      entry = loaded.pop(0)

      if entry not in self.existing_hashes:
        self.existing_hashes.append(entry)
        load_count += 1

    return load_count

  def scan(self, dump_directory:str) -> bool:
    """
    Scans a "dump" directory determine if the contents conform to the expectations of the repository.

    For example, a Garmin FIT protocol files repository requires that the "dump" directory contain both the DEVICE.FIT and GarminDevice.xml files.

    By default, returns False indicating the provided "dump" directory fails to conform to the repository expectations.
    """
    return False

  def on_file(self, file_path:str) -> bool:
    """
    Handles the notification that a file was discovered in a "dump" directory.

    The result should be the indication whether or not the file should be processed further.

    By default, returns False to indicate the file should not be processed further.
    """
    return False

  def on_drop(self, file_path:str, reason:str) -> bool:
    """
    Handles the notification of a file to be deleted.
    
    This notification allows interception of the file deletion, such that the deletion may be avoided if desired.

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
          
          if self.on_file(file_path):
            file_contents_hash = self.hasher(file_path)

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

  # TODO: Reimplement this (as it previously occurred at the end of [fitted]HashedFitFiles::read()).
  def wipe(self, dump_directory:str) -> bool:
    """
    Recursively earses a "dump" directory.

    By default, returns False to indicate no erasure was completed.
    """
    return False
