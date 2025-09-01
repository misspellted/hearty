
import config

from hearty.files import delete_empty_directory
from hearty.repositories.fit import FitDeviceFiles

import os

DRY_RUN = True

def on_drop(file_path:str, reason:str) -> bool:
  print(f"DRY-RUN={DRY_RUN} {"Not " if DRY_RUN else ""}Deleting {file_path} - {reason}")
  return not DRY_RUN

fdf = FitDeviceFiles(config.DIR_FR35_HASHED)
fdf.on_drop = on_drop
fdf.on_read = lambda file_path, hash, hash_file_path: print(f"Read {file_path} with hash {hash}; moving to {hash_file_path}...")

load_count = fdf.load()

print(f"Loaded {load_count} existing hash(es).")

readable:list[str] = []

for dump_directory in os.listdir(config.DIR_FR35_DUMPS):
  ddp = os.path.join(config.DIR_FR35_DUMPS, dump_directory)
  scan_result = fdf.scan(ddp)

  if scan_result:
    readable.append(ddp)
    print(f"~~ {ddp} looks to be readable into the repository.")
  else:
    print(f"!! {ddp} does not contain the required device files for readability into the repository.")

read:dict[str, tuple[str, str]] = {}

for dump_directory in readable:
  read.update(fdf.read(dump_directory))

[print(f"++ Hash {hash}: {paths[0]} -> {paths[1]}") for hash, paths in read.items()]

for dump_directory in os.listdir(config.DIR_FR35_DUMPS):
  ddp = os.path.join(config.DIR_FR35_DUMPS, dump_directory)

  if not DRY_RUN and delete_empty_directory(ddp):
    print(f"-- {ddp} deleted.")
  else:
    print(f"!! {ddp} needs manual deletion. [DRY_RUN={DRY_RUN}]")
