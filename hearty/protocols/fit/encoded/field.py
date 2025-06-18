
from .types import base_types

FIELD_DEFINITION_BYTES = 3

class FieldDefinition:
  NUMBER = 0
  SIZE = 1
  BASE_TYPE = 2

  def __init__(self):
    self.number = None
    self.size = None
    self.base_type = None

  def decode(self, bytes:list[int]) -> bool:
    valid = len(bytes) == FIELD_DEFINITION_BYTES

    if valid:
      self.number = bytes[FieldDefinition.NUMBER]
      self.size = bytes[FieldDefinition.SIZE]

      valid = bytes[FieldDefinition.BASE_TYPE] in base_types.keys()

      if valid:
        self.base_type = base_types[bytes[FieldDefinition.BASE_TYPE]]

    return valid

class Field:
  def __init__(self, definition:FieldDefinition):
    self.definition = definition
    self.value = None

  def evaluate(self, bytes:list[int], endianness:str) -> bool:
    # endianness = {"little" | "big"}
    self.value = int.from_bytes(bytes, byteorder=endianness)
    # TODO: Don't assume an integer value? We have base_type in definition, so maybe we can evaluate from that.
    return True # TODO: Actually indicate a successful or failing evaluation.

  def __repr__(self):
    return f"{self.value if self.value != None else '<none>'}"
