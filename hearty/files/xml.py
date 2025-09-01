
from xml.etree import ElementTree

import logging
logger = logging.getLogger(__name__)

def split_namespace_from_name(text:str) -> tuple[str, str]:
  xmlns:str = None
  name:str = None

  if text != None:
    parts = text.split("}")

    if len(parts) == 1:
      name = parts[0]
    else:
      xmlns = parts[0].split("{")[1]
      name = parts[1]

  return (xmlns, name)

class XmlFile:
  def __init__(self):
    self.tree:ElementTree = None
    self.root:ElementTree.Element = None

  def read_from_file(self, xml_file_path:str):
    logger.info(f"XML file: {xml_file_path}")

    self.tree = ElementTree.parse(xml_file_path)
    self.root = self.tree.getroot()

class GarminDeviceXml(XmlFile):
  FILE_NAME = "GarminDevice.xml"

  def __init__(self):
    XmlFile.__init__(self)
    self.schema:tuple[str, str] = None
    self.device:dict = {}

  def read_from_file(self, xml_file_path:str):
    XmlFile.read_from_file(self, xml_file_path)

    # The root element should be the Device element, which also has the schema details as an attribute.
    root_tag = split_namespace_from_name(self.root.tag)

    if root_tag[1] == "Device":
      for attrib, value in self.root.attrib.items():
        attrib_name = split_namespace_from_name(attrib)

        if attrib_name[1] == "schemaLocation":
          self.schema = tuple(value.split(" "))

    # Verify the schema is used with the root element tag.
    if root_tag[0] == self.schema[0]:
      for child in self.root:
        child_tag = split_namespace_from_name(child.tag)

        if child_tag[0] == self.schema[0]:
          if child_tag[1] == "Model":
            self.device["Model"] = {}
            for detail in child:
              detail_tag = split_namespace_from_name(detail.tag)
              self.device["Model"][detail_tag[1]] = detail.text
          elif child_tag[1] == "Id":
            self.device["Id"] = child.text
            pass
          elif child_tag[1] == "MassStorageMode":
            # For a Forerunner 35 on SoftwareVersion 360, the device's XML file contains child nodes out of these: DataType and UpdateFile.
            self.device["MassStorageMode"] = {}
            self.device["MassStorageMode"]["DataType"] = []
            # self.device["MassStorageMode"]["UpdateFile"] = [] # TODO: Maybe extract part numbers? Otherwise, not sure what else is useful...

            for node in child:
              node_tag = split_namespace_from_name(node.tag)

              if node_tag[1] == "DataType":
                dataTypeName:str = None
                dataTypeFiles = []

                for data_type_child in node:
                  data_type_child_tag = split_namespace_from_name(data_type_child.tag)
                  
                  if data_type_child_tag[1] == "Name":
                    dataTypeName = data_type_child.text
                  elif data_type_child_tag[1] == "File":
                    specification_identifier:str = None
                    location_path:str = None
                    location_base_name:str = None # May not be specified, basically if not, consider it an asterisks for the base name.
                    location_file_extension:str = None
                    transfer_direction:str = None

                    for data_type_file in data_type_child:
                      data_type_file_tag = split_namespace_from_name(data_type_file.tag)

                      if data_type_file_tag[1] == "Specification":
                        for data_type_file_detail in data_type_file:
                          data_type_file_detail_tag = split_namespace_from_name(data_type_file_detail.tag)

                          if data_type_file_detail_tag[1] == "Identifier":
                            specification_identifier = data_type_file_detail.text

                      elif data_type_file_tag[1] == "Location":
                        for data_type_file_detail in data_type_file:
                          data_type_file_detail_tag = split_namespace_from_name(data_type_file_detail.tag)

                          if data_type_file_detail_tag[1] == "Path":
                            location_path = data_type_file_detail.text
                          elif data_type_file_detail_tag[1] == "BaseName":
                            location_base_name = data_type_file_detail.text
                          elif data_type_file_detail_tag[1] == "FileExtension":
                            location_file_extension = data_type_file_detail.text

                      elif data_type_file_tag[1] == "TransferDirection":
                        transfer_direction = data_type_file.text

                    # Since we're only interested in data _from_ the device, we'll want to watch for file data types that indicate output.
                    # "InputToUnit": not interested
                    # "OutputFromUnit": interested
                    # "InputOutput": interested

                    if transfer_direction in ["OutputFromUnit", "InputOutput"]:
                      dataTypeFiles.append((specification_identifier, location_path, location_base_name, location_file_extension))

                if 0 < len(dataTypeFiles):
                  dataType = {}
                  dataType["Name"] = dataTypeName
                  dataType["File"] = dataTypeFiles
                  self.device["MassStorageMode"]["DataType"].append(dataType)
              elif node_tag[1] == "UpdateFile":
                pass # Not sure what benefit is provided by parsing the data just yet...
