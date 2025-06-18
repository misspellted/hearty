
from .base import BaseType

# Null-terminated string encoded in UTF-8.
class String(BaseType):
  NUMBER = 0x07

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(String.NUMBER)

  @property
  def name(self):
    return "string"

  @property
  def invalid_value(self):
    return 0x00

  def evaluate(self, bytes:list[int], endianness:str) -> tuple[bool, str]:
    # Basically, ensure no byte in the array is invalid.
    valid = 0 < len(bytes)

    for _ in range(len(bytes)):
      valid = True if _ < len(bytes) - 1 and bytes[_] != self.invalid_value else True if _ == len(bytes) - 1 and bytes[_] == self.invalid_value else False

      if not valid:
        break

    # But we can convert to the text form of the data.
    return (valid, None if not valid else str(bytes, encoding='utf-8'))

# Array of bytes. Field is invalid if all bytes are invalid.
class Byte(BaseType):
  NUMBER = 0x0D

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(Byte.NUMBER)

  @property
  def name(self):
    return "byte"

  @property
  def invalid_value(self):
    return 0xFF

  def evaluate(self, bytes:list[int], endianness:str) -> tuple[bool, list[int]]:
    # Basically, ensure no byte in the array is invalid.
    valid = 0 < len(bytes)

    for byte in bytes:
      valid = byte != self.invalid_value

      if not valid:
        break

    return (valid, None if not valid else bytes)
