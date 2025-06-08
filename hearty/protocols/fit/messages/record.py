
class RecordMessage:
  GLOBAL_MESSAGE_NUMBER = 20 # As shown on https://developer.garmin.com/fit/protocol/#globalmessagenumber.

  # TODO: Everything else? ^_^

  # TODO: Fill in the attributes from the fields of a file record.
  def from_file_message_record(self, file_message_record):
    return NotImplementedError()

def new_record_message():
  return RecordMessage()
