
from config import FR35_DUMPS_DIR

from hearty.files.fit import FitFile

ff = FitFile()

record_count = ff.read_from_file(fit_file_path=f"{FR35_DUMPS_DIR}/2025-05-24_23-14/DEVICE.FIT")
print(f"Read {record_count} record(s)")
