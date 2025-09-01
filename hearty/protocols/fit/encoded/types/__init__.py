
from .enum import Enum
from .signed import SInt8, SInt16, SInt32, SInt64
from .unsigned import UInt8, UInt16, UInt32, UInt64, UInt8Z, UInt16Z, UInt32Z, UInt64Z
from .array import String, Byte
from .floating import Float32, Float64

base_types = {
  Enum.NUMBER: Enum(),
  SInt8.NUMBER: SInt8(),
  UInt8.NUMBER: UInt8(),
  SInt16.NUMBER: SInt16(),
  UInt16.NUMBER: UInt16(),
  SInt32.NUMBER: SInt32(),
  UInt32.NUMBER: UInt32(),
  String.NUMBER: String(),
  Float32.NUMBER: Float32(),
  Float64.NUMBER: Float64(),
  UInt8Z.NUMBER: UInt8Z(),
  UInt16Z.NUMBER: UInt16Z(),
  UInt32Z.NUMBER: UInt32Z(),
  Byte.NUMBER: Byte(),
  SInt64.NUMBER: SInt64(),
  UInt64.NUMBER: UInt64(),
  UInt64Z.NUMBER: UInt64Z(),
}
