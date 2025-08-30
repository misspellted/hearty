
# TODO: Continue importing message implementions into the map of global_message_number: <new_instance_function>.

from .file_id import FileIdMessage, new_file_id_message
from .record import RecordMessage, new_record_message

global_messages = {
  FileIdMessage.GLOBAL_MESSAGE_NUMBER: new_file_id_message,
  RecordMessage.GLOBAL_MESSAGE_NUMBER: new_record_message,
}
