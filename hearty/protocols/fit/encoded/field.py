
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

  def decode(self, bites:list[int]) -> bool:
    valid = len(bites) == FIELD_DEFINITION_BYTES

    if valid:
      self.number = bites[FieldDefinition.NUMBER]
      self.size = bites[FieldDefinition.SIZE]

      valid = bites[FieldDefinition.BASE_TYPE] in base_types.keys()

      if valid:
        self.base_type = base_types[bites[FieldDefinition.BASE_TYPE]]

    return valid

  def __repr__(self):
    return f"{self.size} byte(s): {self.base_type.name}"

class Field:
  def __init__(self, definition:FieldDefinition):
    self.definition = definition
    self.value = None

  def evaluate(self, bites:list[int], endianness:str) -> bool:
    valid = self.definition != None

    if valid:
      valid, self.value = self.definition.base_type.evaluate(bites=bites, endianness=endianness)

    return valid

  def __repr__(self):
    return f"{self.value if self.value != None else '<none>'}"
