
import hashlib

def sha3_512(file_path:str, buffer_size:int=1024*64) -> str:
  """
  Calculates a SHA3-512 hash from the contents of a file.

  A chunk size parameter is provided to avoid having to load the entire file into memory to complete the hasing calculation.

  Based on https://stackoverflow.com/a/22058673
  """
  hasher = hashlib.sha3_512()

  with open(file_path, "rb") as file:
    while True:
      chunk = file.read(buffer_size)

      if not chunk:
        break

      hasher.update(chunk)

  return hasher.hexdigest()
