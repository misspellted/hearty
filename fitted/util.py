
import os

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
