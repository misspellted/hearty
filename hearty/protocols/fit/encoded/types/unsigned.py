
from .base import BaseType

class UInt8(BaseType):
  NUMBER = 0x02

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(UInt8.NUMBER)

  @property
  def name(self):
    return "uint8"

  @property
  def invalid_value(self):
    return 0xFF

class UInt16(BaseType):
  NUMBER = 0x84

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(UInt16.NUMBER)

  @property
  def name(self):
    return "uint16"

  @property
  def invalid_value(self):
    return 0xFFFF

class UInt32(BaseType):
  NUMBER = 0x86

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(UInt32.NUMBER)

  @property
  def name(self):
    return "uint32"

  @property
  def invalid_value(self):
    return 0xFFFF_FFFF

class UInt64(BaseType):
  NUMBER = 0x8F

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(UInt64.NUMBER)

  @property
  def name(self):
    return "uint64"

  @property
  def invalid_value(self):
    return 0xFFFF_FFFF_FFFF_FFFF

class UInt8Z(BaseType):
  NUMBER = 0x0A

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(UInt8Z.NUMBER)

  @property
  def name(self):
    return "uint8z"

  @property
  def invalid_value(self):
    return 0x00

class UInt16Z(BaseType):
  NUMBER = 0x8B

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(UInt16Z.NUMBER)

  @property
  def name(self):
    return "uint16z"

  @property
  def invalid_value(self):
    return 0x0000

class UInt32Z(BaseType):
  NUMBER = 0x8C

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(UInt32Z.NUMBER)

  @property
  def name(self):
    return "uint32z"

  @property
  def invalid_value(self):
    return 0x0000_0000

class UInt64Z(BaseType):
  NUMBER = 0x90

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(UInt64Z.NUMBER)

  @property
  def name(self):
    return "uint64z"

  @property
  def invalid_value(self):
    return 0x0000_0000_0000_0000
