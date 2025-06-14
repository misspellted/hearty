
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
