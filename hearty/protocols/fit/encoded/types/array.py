
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
