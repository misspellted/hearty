
from .base import BaseType

class Enum(BaseType):
  NUMBER = 0x00

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(Enum.NUMBER)

  @property
  def name(self):
    return "enum"

  @property
  def invalid_value(self):
    return 0xFF

  def evaluate(self, bites:list[int], endianness:str) -> tuple[bool, str]:
    valid = 1 == len(bytes) and bytes[0] != self.invalid_value

    return (valid, None if not valid else bytes[0])
