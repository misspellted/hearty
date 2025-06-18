
from .base import BaseType

# Signed base types are in 2's complement format.

class SInt8(BaseType):
  NUMBER = 0x01
  BYTES = 1

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(SInt8.NUMBER)

  @property
  def name(self):
    return "sint8"

  @property
  def invalid_value(self):
    return 0x7F

  def evaluate(self, bytes:list[int], endianness:str) -> tuple[bool, int]:
    valid = SInt8.BYTES == len(bytes) and bytes[0] != self.invalid_value

    return (valid, None if not valid else int.from_bytes(bytes, signed=True))

class SInt16(BaseType):
  NUMBER = 0x83
  BYTES = 2

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(SInt16.NUMBER)

  @property
  def name(self):
    return "sint16"

  @property
  def invalid_value(self):
    return 0x7FFF

  def evaluate(self, bytes:list[int], endianness:str) -> tuple[bool, int]:
    valid = SInt16.BYTES == len(bytes)

    if valid:
      # Compare each byte to the invalid value as bytes in the endianness order.
      invalid_bytes = self.invalid_value.to_bytes(SInt16.BYTES, byteorder=endianness, signed=True)
      comps = [True if invalid_bytes[_] == bytes[_] else False for _ in range(SInt16.BYTES)]

      valid = False if False not in comps else True

    return (valid, None if not valid else int.from_bytes(bytes, byteorder=endianness, signed=True))

class SInt32(BaseType):
  NUMBER = 0x85
  BYTES = 4

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(SInt32.NUMBER)

  @property
  def name(self):
    return "sint32"

  @property
  def invalid_value(self):
    return 0x7FFF_FFFF

  def evaluate(self, bytes:list[int], endianness:str) -> tuple[bool, int]:
    valid = SInt32.BYTES == len(bytes)

    if valid:
      # Compare each byte to the invalid value as bytes in the endianness order.
      invalid_bytes = self.invalid_value.to_bytes(SInt32.BYTES, byteorder=endianness, signed=True)
      comps = [True if invalid_bytes[_] == bytes[_] else False for _ in range(SInt32.BYTES)]

      valid = False if False not in comps else True

    return (valid, None if not valid else int.from_bytes(bytes, byteorder=endianness, signed=True))

class SInt64(BaseType):
  NUMBER = 0x8E
  BYTES = 8

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(SInt64.NUMBER)

  @property
  def name(self):
    return "sint64"

  @property
  def invalid_value(self):
    return 0x7FFF_FFFF_FFFF_FFFF

  def evaluate(self, bytes:list[int], endianness:str) -> tuple[bool, int]:
    valid = SInt64.BYTES == len(bytes)

    if valid:
      # Compare each byte to the invalid value as bytes in the endianness order.
      invalid_bytes = self.invalid_value.to_bytes(SInt64.BYTES, byteorder=endianness, signed=True)
      comps = [True if invalid_bytes[_] == bytes[_] else False for _ in range(SInt64.BYTES)]

      valid = False if False not in comps else True

    return (valid, None if not valid else int.from_bytes(bytes, byteorder=endianness, signed=True))
