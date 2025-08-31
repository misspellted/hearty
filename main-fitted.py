
import config

from hearty.repositories.fit import FitDeviceFiles

from fitted.util import delete_empty_directory

import os

DRY_RUN = True

def on_drop(file_path:str, reason:str) -> bool:
  print(f"DRY-RUN={DRY_RUN} {"Not " if DRY_RUN else ""}Deleting {file_path} - {reason}")
  return not DRY_RUN

ffr = FitDeviceFiles(config.DIR_FR35_HASHED)
ffr.on_drop = on_drop
ffr.on_read = lambda file_path, hash, hash_file_path: print(f"Read {file_path} with hash {hash}; moving to {hash_file_path}...")

load_count = ffr.load()

print(f"Loaded {load_count} existing hash(es).")

# Previously, [fitted]HashedFitFiles::scan(dir) expected a directory of dump directories.
# This is no longer the expectation; instead, [hearty]FitDeviceFiles::scan(dir) expects an individual dump directory.
# Therefore, the config.DIR_FR35_DUMPS value will need hanlded here.
# TODO: Determine viability of maybe adding a ::overscan() or similar to recreate the old behavior/expectation.

# In addition, [hearty]FitDeviceFiles::scan(dir) no longer reports a list of candidate dump directories, but instead
# indicates whether or not the provided directory is ready for import (has both DEVICE.FT and GarminDevice.xml
# files at the root of the provided directory):
#
# <provided_directory>/
# + DEVICE.FIT
# + GarminDevice.xml
# + <other directories, such as ACTIVITY, MONITOR, etc>/
#
# NOTE: The work in parsing the GarminDevice.xml may in fact alter the above directory structure, as the file utilizes
# a common 'GARMIN' base/root directory in the location.path references in the XML elements. However, the current "fr35"
# "project" files do not adhere to that potential new expectation, so this alteration may or may not be made. Stay tuned!

readable:list[str] = []

for dump_directory in os.listdir(config.DIR_FR35_DUMPS):
  ddp = os.path.join(config.DIR_FR35_DUMPS, dump_directory)
  scan_result = ffr.scan(ddp)

  if scan_result:
    readable.append(ddp)
    print(f"~~ {ddp} looks to be readable into the repository.")
  else:
    print(f"!! {ddp} does not contain the required device files for readability into the repository.")

read:dict[str, tuple[str, str]] = {}

for dump_directory in readable:
  read.update(ffr.read(dump_directory))

[print(f"++ Hash {hash}: {paths[0]} -> {paths[1]}") for hash, paths in read.items()]

# Effectively, the old HashedFitFiles::wipe(dumps_directory):
for dump_directory in os.listdir(config.DIR_FR35_DUMPS):
  ddp = os.path.join(config.DIR_FR35_DUMPS, dump_directory)

  if not DRY_RUN and delete_empty_directory(ddp):
    print(f"-- {ddp} deleted.")
  else:
    print(f"!! {ddp} needs manual deletion. [DRY_RUN={DRY_RUN}]")
