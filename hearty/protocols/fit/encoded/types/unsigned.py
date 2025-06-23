
from .base import BaseType, evaluate_integer

# The following unsigned types are for values which are greater than or equal to zero.

class UInt8(BaseType):
  NUMBER = 0x02
  BYTES = 1

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(UInt8.NUMBER)

  @property
  def name(self):
    return "uint8"

  @property
  def invalid_value(self):
    return 0xFF

  def evaluate(self, bytes:list[int], endianness:str) -> tuple[bool, int]:
    return evaluate_integer(signed=False, octets=UInt8.BYTES, bytes=bytes, endianness=endianness, invalid_value=self.invalid_value)

class UInt16(BaseType):
  NUMBER = 0x84
  BYTES = 2

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(UInt16.NUMBER)

  @property
  def name(self):
    return "uint16"

  @property
  def invalid_value(self):
    return 0xFFFF

  def evaluate(self, bytes:list[int], endianness:str) -> tuple[bool, int]:
    return evaluate_integer(signed=False, octets=UInt16.BYTES, bytes=bytes, endianness=endianness, invalid_value=self.invalid_value)

class UInt32(BaseType):
  NUMBER = 0x86
  BYTES = 4

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(UInt32.NUMBER)

  @property
  def name(self):
    return "uint32"

  @property
  def invalid_value(self):
    return 0xFFFF_FFFF

  def evaluate(self, bytes:list[int], endianness:str) -> tuple[bool, int]:
    return evaluate_integer(signed=False, octets=UInt32.BYTES, bytes=bytes, endianness=endianness, invalid_value=self.invalid_value)

class UInt64(BaseType):
  NUMBER = 0x8F
  BYTES = 8

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(UInt64.NUMBER)

  @property
  def name(self):
    return "uint64"

  @property
  def invalid_value(self):
    return 0xFFFF_FFFF_FFFF_FFFF

  def evaluate(self, bytes:list[int], endianness:str) -> tuple[bool, int]:
    return evaluate_integer(signed=False, octets=UInt64.BYTES, bytes=bytes, endianness=endianness, invalid_value=self.invalid_value)


# The following unsigned types are for values which must be greater than zero.

class UInt8Z(BaseType):
  NUMBER = 0x0A
  BYTES = 1

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(UInt8Z.NUMBER)

  @property
  def name(self):
    return "uint8z"

  @property
  def invalid_value(self):
    return 0x00

  def evaluate(self, bytes:list[int], endianness:str) -> tuple[bool, int]:
    return evaluate_integer(signed=False, octets=UInt8Z.BYTES, bytes=bytes, endianness=endianness, invalid_value=self.invalid_value)

class UInt16Z(BaseType):
  NUMBER = 0x8B
  BYTES = 2

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(UInt16Z.NUMBER)

  @property
  def name(self):
    return "uint16z"

  @property
  def invalid_value(self):
    return 0x0000

  def evaluate(self, bytes:list[int], endianness:str) -> tuple[bool, int]:
    return evaluate_integer(signed=False, octets=UInt16Z.BYTES, bytes=bytes, endianness=endianness, invalid_value=self.invalid_value)

class UInt32Z(BaseType):
  NUMBER = 0x8C
  BYTES = 4

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(UInt32Z.NUMBER)

  @property
  def name(self):
    return "uint32z"

  @property
  def invalid_value(self):
    return 0x0000_0000

  def evaluate(self, bytes:list[int], endianness:str) -> tuple[bool, int]:
    return evaluate_integer(signed=False, octets=UInt32Z.BYTES, bytes=bytes, endianness=endianness, invalid_value=self.invalid_value)

class UInt64Z(BaseType):
  NUMBER = 0x90
  BYTES = 8

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(UInt64Z.NUMBER)

  @property
  def name(self):
    return "uint64z"

  @property
  def invalid_value(self):
    return 0x0000_0000_0000_0000

  def evaluate(self, bytes:list[int], endianness:str) -> tuple[bool, int]:
    return evaluate_integer(signed=False, octets=UInt64Z.BYTES, bytes=bytes, endianness=endianness, invalid_value=self.invalid_value)
