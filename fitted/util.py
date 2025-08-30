
import hashlib
import os

def chunked_sha3_512_hex(file_path:str, buffer_size:int=1024*64) -> str:
  # Based on https://stackoverflow.com/a/22058673
  hasher = hashlib.sha3_512()

  with open(file_path, "rb") as file:
    while True:
      chunk = file.read(buffer_size)

      if not chunk:
        break

      hasher.update(chunk)

  return hasher.hexdigest()

def delete_empty_directory(directory:str) -> bool:
  contents = os.listdir(directory)

  empty = len(contents) == 0

  if not empty:
    for _ in contents:
      _path = os.path.join(directory, _)

      empty = os.path.isdir(_path) and delete_empty_directory(_path)

      if not empty:
        break
  
  if empty:
    os.rmdir(directory)

  return empty
