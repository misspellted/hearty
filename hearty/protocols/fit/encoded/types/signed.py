
from .base import BaseType

# Signed base types are in 2's complement format.

class SInt8(BaseType):
  NUMBER = 0x01

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(SInt8.NUMBER)

  @property
  def name(self):
    return "sint8"

  @property
  def invalid_value(self):
    return 0x7F

class SInt16(BaseType):
  NUMBER = 0x83

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(SInt16.NUMBER)

  @property
  def name(self):
    return "sint16"

  @property
  def invalid_value(self):
    return 0x7FFF

class SInt32(BaseType):
  NUMBER = 0x85

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(SInt32.NUMBER)

  @property
  def name(self):
    return "sint32"

  @property
  def invalid_value(self):
    return 0x7FFF_FFFF

class SInt64(BaseType):
  NUMBER = 0x8E

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(SInt64.NUMBER)

  @property
  def name(self):
    return "sint64"

  @property
  def invalid_value(self):
    return 0x7FFF_FFFF_FFFF_FFFF
