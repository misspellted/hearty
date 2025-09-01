
import os, xml

from hearty.files.fit import FitFile
from hearty.files.xml import GarminDeviceXml
from hearty.protocols.fit.messages import global_messages, FileIdMessage

def on_device_fit_file(file_path:str) -> tuple[int, int, int]:
  manufacturer:int = None
  product:int = None
  serial_number:int = None

  exists = os.path.exists(file_path)

  if exists:
    ddff = FitFile()
    record_count = ddff.read_from_file(file_path)

    print(f"\n\n<<< FitFile.read_from_file({file_path}) >>>")

    print(f"\tRecord Count: {record_count}")
    print(f"\tMessage Count: {len(ddff.messages)}")

    # To have messages, records are required.
    if 0 < record_count:
      fim:FileIdMessage = None

      for message in ddff.messages:
        if message.global_message_number in global_messages.keys():
          gm = global_messages[message.global_message_number]()
          gm.from_file_message_record(message)

          if isinstance(gm, FileIdMessage):
            fim = gm
      
      if fim != None:
        print("\tfile_id message:")
        print(f"\t\tType: {fim.type}")
        print(f"\t\tManufacturer: {fim.manufacturer}")
        print(f"\t\tProduct: {fim.product}")
        print(f"\t\tSerial Number: {fim.serial_number}")
        print(f"\t\tTime Created: {fim.time_created}") # Activity (type 4) files have valid time_created values, but type 1 (assuming 'device') files have invalid values 4294967295 (uint32) .. (thinking_face) ..
        print(f"\t\tUnknown Fields? {0 < len(fim.unknown.keys())}")
        for ufdn, ubtn_val in fim.unknown.items():
          print(f"\t\t\t{ufdn}: {ubtn_val}")

        manufacturer = FileIdMessage.MANUFACTURERS[fim.manufacturer.value]
        product = FileIdMessage.PRODUCTS[fim.product.value]
        serial_number = fim.serial_number.value

    print(f">>> FitFile.read_from_file({file_path}) <<<\n\n")

  return (manufacturer, product, serial_number) if exists else None

def on_device_xml_file(file_path:str) -> tuple:
  xml_device:object = None

  exists = os.path.exists(file_path)

  if exists:
    xml_file = GarminDeviceXml()
    xml_file.read_from_file(file_path)

    print(f"\n\n<<< GarminDeviceXml.read_from_file({file_path}) >>>")
    
    print(f"\tSchema: {xml_file.schema}")

    print(f"\n\n>>> GarminDeviceXml.read_from_file({file_path}) <<<")

  return xml_device

def scan_for_fit_files_dump(directory:str) -> bool:
  """
  Scans a directory to determine if it contains sufficient evidence of being a FIT files dump (data files pulled from a FIT protocol-adherent device).

  The current determining factor is if the directory contains both `DEVICE.FIT` and `GarminDevice.xml` files, although the latter might be manufacturer-dependent.
  """
  result = os.path.isdir(directory)

  ddfp:str = os.path.join(directory, "DEVICE.FIT") if result else None
  device_mps = on_device_fit_file(ddfp) if ddfp != None else None
  result = device_mps != None

  # The contents indicate this file might be the one we want to find first, as there's a 'FITBinary' node that describes the DEVICE.FIT file, which means it might not always be `DEVICE.FIT`.
  # But for now, we'll leave it as the secondary item to be found in order to indicate it's probably a FIT device data dump directory.
  ddxp:str = os.path.join(directory, "GarminDevice.xml") if result else None

  if result:
    print(f"FIT device manufacturer: {device_mps[0]}")
    print(f"FIT device product: {device_mps[1]}")
    print(f"FIT device serial number: {device_mps[2]}")



  return result
