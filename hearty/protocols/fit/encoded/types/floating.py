
from .base import BaseType

class Float32(BaseType):
  NUMBER = 0x88

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(Float32.NUMBER)

  @property
  def name(self):
    return "float32"

  @property
  def invalid_value(self):
    return 0xFFFF_FFFF

class Float64(BaseType):
  NUMBER = 0x89

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(Float64.NUMBER)

  @property
  def name(self):
    return "float64"

  @property
  def invalid_value(self):
    return 0xFFFF_FFFF_FFFF_FFFF

# TODO: Use struct module to unpack floating point numbers (Float32 -> 'f', Float64 -> 'd').
