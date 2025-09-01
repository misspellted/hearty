
from ..encoded.record import MessageDefinitionRecord, MessageDataRecord

from collections import OrderedDict # Let the container maintain the sorted keys instead of sorting each time.

class FitMessage:
  def __init__(self, definition:MessageDefinitionRecord, data:MessageDataRecord):
    self.global_message_number = definition.global_message_number

    self.fields = OrderedDict()

    for field in sorted([fd.number for fd in definition.field_definitions]):
      self.fields[field] = data.fields[field]

    self.developer_fields = OrderedDict()

    for developer_field in sorted([dfd.number for dfd in definition.developer_field_definitions]):
      self.developer_fields[developer_field] = data.developer_fields[developer_field]

  def __repr__(self):
    idfr = f"[{self.global_message_number}]"
    fds = f"{[f"{key}: {field}" for key, field in self.fields.items()]}"
    dfds = f"{[f"{developer_key}: {developer_field}" for developer_key, developer_field in self.developer_fields.items()]}"
    return f"{idfr} - {fds} + {dfds}" if 0 < len(self.developer_fields.keys()) else f"{idfr} - {fds}"
