
from .base import BaseType

def null_terminate(text:str) -> str:
  if text == None:
    raise ValueError("Expected a value.")

  if not isinstance(text, str):
    raise TypeError("Expected a str type.")

  return f"\0" if 0 == len(text) else f"{text}\0" if text[-1] != '\0' else text

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

  # Endianness is ignored, since an array of bytes has none.
  def evaluate(self, bites:list[int], endianness:str) -> tuple[bool, str]:
    # Basically, ensure no byte in the array is invalid except the last one, the null-terminated byte).
    valid = 0 < len(bites)

    if valid:
      comparisons = [self.invalid_value == bites[_] for _ in range(len(bites) - 1)]
      valid = False if all(comparisons) else self.invalid_value == bites[-1]

    # But we can convert to the text form of the data.
    return (valid, None if not valid else str(bytes(bites), encoding='utf-8'))

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

  # Endianness is ignored, since an array of bytes has none.
  def evaluate(self, bites:list[int], endianness:str) -> tuple[bool, list[int]]:
    # Basically, ensure no byte in the array is invalid.
    valid = 0 < len(bites)

    if valid:
      comparisons = [self.invalid_value == _ for _ in bites]
      valid = False if all(comparisons) else True

    return (valid, None if not valid else bites)
