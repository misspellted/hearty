
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
