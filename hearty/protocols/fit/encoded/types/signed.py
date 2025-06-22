
from .base import BaseType, evaluate_integer

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
    return evaluate_integer(signed=True, octets=SInt8.BYTES, bytes=bytes, endianness=endianness, invalid_value=self.invalid_value)

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
    return evaluate_integer(signed=True, octets=SInt16.BYTES, bytes=bytes, endianness=endianness, invalid_value=self.invalid_value)

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
    return evaluate_integer(signed=True, octets=SInt32.BYTES, bytes=bytes, endianness=endianness, invalid_value=self.invalid_value)

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
    return evaluate_integer(signed=True, octets=SInt64.BYTES, bytes=bytes, endianness=endianness, invalid_value=self.invalid_value)
