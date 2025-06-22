
from .base import BaseType

# There isn't a nice "first-class" method pair on float like there is on int (.from_bytes/.to_bytes).
# Thusly, the mechanism is to read the bytes through the struct module and unpacking them.
import struct

def evaluate_floating(octets:int, bytes:list[int], endianness:str, invalid_value:int=None) -> tuple[bool, float]:
  valid = octets == len(bytes)
  value = None

  if valid:
    invalid_bytes = invalid_value.to_bytes(octets) # Endianness technically won't matter for invalid_value, because all bytes are 0xFF.
    comparisons = [True if invalid_bytes[_] == bytes[_] else False for _ in range(octets)]
    
    valid = False if False not in comparisons else True

    if valid:
      value = struct.unpack(f"{'<' if endianness == "little" else '>'}{'d' if octets == 8 else 'f'}", bytes)

  return (valid, value)

class Float32(BaseType):
  NUMBER = 0x88
  BYTES = 4

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(Float32.NUMBER)

  @property
  def name(self):
    return "float32"

  @property
  def invalid_value(self):
    return 0xFFFF_FFFF

  def evaluate(self, bytes:list[int], endianness:str) -> tuple[bool, float]:
    return evaluate_floating(octets=Float32.BYTES, bytes=bytes, endianness=endianness, invalid_value=self.invalid_value)

class Float64(BaseType):
  NUMBER = 0x89
  BYTES = 8

  def __init__(self):
    BaseType.__init__(self=self)
    self.decode(Float64.NUMBER)

  @property
  def name(self):
    return "float64"

  @property
  def invalid_value(self):
    return 0xFFFF_FFFF_FFFF_FFFF

  def evaluate(self, bytes:list[int], endianness:str) -> tuple[bool, float]:
    return evaluate_floating(octets=Float32.BYTES, bytes=bytes, endianness=endianness, invalid_value=self.invalid_value)
