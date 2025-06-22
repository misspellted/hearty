
class BaseType:
  MASK_HAS_ENDIANNESS = 0b1000_0000
  MASK_RESERVED = 0b0110_0000
  MASK_NUMBER = 0b0001_1111
  MIN_NUMBER = 0
  MAX_NUMBER = 16

  def __init__(self):
    self.has_endianness = None
    self.number = None

  def decode(self, encoded:int) -> bool:
    self.has_endianness = (encoded & BaseType.MASK_HAS_ENDIANNESS) == BaseType.MASK_HAS_ENDIANNESS
    reserved = (encoded & BaseType.MASK_RESERVED) >> 5
    self.number = encoded & BaseType.MASK_NUMBER
    
    return reserved == 0 and BaseType.MIN_NUMBER <= self.number <= BaseType.MAX_NUMBER

  @property
  def name(self) -> str:
    raise NotImplementedError()

  @property
  def invalid_value(self) -> str:
    raise NotImplementedError()

  def __repr__(self):
    return f"[{self.number:02d}] {self.name}!{self.invalid_value}"

  def evaluate(bytes:list[int], endianness:str) -> tuple[bool, object]:
    raise NotImplementedError()

def evaluate_integer(signed:bool, octets:int, bytes:list[int], endianness:str, invalid_value:int=None) -> tuple[bool, int]:
  valid = octets == len(bytes)
  value = None
  
  if valid and isinstance(invalid_value, int):
    invalid_bytes = invalid_value.to_bytes(octets, byteorder=endianness, signed=signed)
    comparisons = [True if invalid_bytes[_] == bytes[_] else False for _ in range(octets)]
    
    valid = False if False not in comparisons else True

    if valid:
      value = int.from_bytes(bytes, byteorder=endianness, signed=signed)

  return (valid, value)
