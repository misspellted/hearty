
import unittest

from fitted.repository import *
import tempfile
import os
import shutil

class TestFitFilesRepository(unittest.TestCase):
  def setUp(self):
    # Utilize temporary directories for these tests.
    self.repo_directory:str = tempfile.mkdtemp()
    self.dump_directory:str = tempfile.mkdtemp()
    self.on_read_calls:list[tuple[str, str, str]] = []

  def tearDown(self):
    # Ensure the temporary directories are deleted.
    if os.path.exists(self.dump_directory):
      shutil.rmtree(self.dump_directory)

    if os.path.exists(self.repo_directory):
      shutil.rmtree(self.repo_directory)

  def write_fit_file_to(self, directory:str, name:str) -> str:
    fp = os.path.join(directory, name)
    with open(fp, "w") as f:
      f.write(name)
    return fp

  def get_device_fit_file_values(self) -> tuple[str, str, str, str, str]:
    dfn = "DEVICE.FIT"
    ddfp = os.path.join(self.dump_directory, dfn)
    sha3_512 = "de6bb309bf322783ba5e3adaa5668430dcb492ba71bcbb6cf70eda34fc2784973150b7506dabd2037c14fa2eea7111a1ff68eae7c0ee2031aa044d0d2ff013a9"
    rdfd = os.path.join(self.repo_directory, sha3_512, "_")
    rdfp = os.path.join(rdfd, dfn)
    return (dfn, ddfp, sha3_512, rdfd, rdfp)

  def get_device_xml_file_values(self) -> tuple[str, str, str, str, str]:
    dxn = "GarminDevice.xml"
    ddxp = os.path.join(self.dump_directory, dxn)
    sha3_512 = "ea81221ad48d3e82affa54fab251664a09bc2c3a6c0772a1368719a71b5d9629eb78f03f04309c94ca446d4079ced5e733259616bd926f89a93890dea5bfdd69"
    rdxd = os.path.join(self.repo_directory, sha3_512, "_")
    rdxp = os.path.join(rdxd, dxn)
    return (dxn, ddxp, sha3_512, rdxd, rdxp)

  def test_new_repository_has_no_existing_hashes(self):
    tested = FitFilesRepository(self.repo_directory)
    self.assertEqual(self.repo_directory, tested.root_directory_path)
    self.assertEqual(0, len(tested.existing_hashes))

  def test_empty_repository_has_no_existing_hashes(self):
    tested = FitFilesRepository(self.repo_directory)
    self.assertEqual(self.repo_directory, tested.root_directory_path)
    self.assertEqual(0, len(tested.existing_hashes))
    self.assertEqual(0, tested.load())

  def test_scan_fails_with_empty_dump_directory(self):
    tested = FitFilesRepository(self.repo_directory)
    self.assertEqual(self.repo_directory, tested.root_directory_path)
    self.assertEqual(0, len(tested.existing_hashes))
    self.assertEqual(0, tested.load())
    self.assertFalse(tested.scan(self.dump_directory))

  def test_scan_fails_without_required_device_fit_file(self):
    tested = FitFilesRepository(self.repo_directory)
    self.assertEqual(self.repo_directory, tested.root_directory_path)
    self.assertEqual(0, len(tested.existing_hashes))
    self.assertEqual(0, tested.load())

    with open(os.path.join(self.dump_directory, "DEVICE.FIT"), "w") as df:
      df.write("DEVICE.FIT")

    self.assertFalse(tested.scan(self.dump_directory))

  def test_scan_fails_without_required_device_xml_file(self):
    tested = FitFilesRepository(self.repo_directory)
    self.assertEqual(self.repo_directory, tested.root_directory_path)
    self.assertEqual(0, len(tested.existing_hashes))
    self.assertEqual(0, tested.load())

    with open(os.path.join(self.dump_directory, "GarminDevice.xml"), "w") as dx:
      dx.write("GarminDevice.xml")

    self.assertFalse(tested.scan(self.dump_directory))

  def test_scan_passes_with_required_device_files(self):
    tested = FitFilesRepository(self.repo_directory)
    self.assertEqual(self.repo_directory, tested.root_directory_path)
    self.assertEqual(0, len(tested.existing_hashes))
    self.assertEqual(0, tested.load())

    with open(os.path.join(self.dump_directory, "DEVICE.FIT"), "w") as df:
      df.write("DEVICE.FIT")

    with open(os.path.join(self.dump_directory, "GarminDevice.xml"), "w") as dx:
      dx.write("GarminDevice.xml")

    self.assertTrue(tested.scan(self.dump_directory))

  def on_drop_returns_false(self, file_path:str, reason:str) -> bool:
    return False

  def test_drop_leaves_file_to_be_deleted(self):
    tested = FitFilesRepository(self.repo_directory)
    self.assertEqual(self.repo_directory, tested.root_directory_path)
    self.assertEqual(0, len(tested.existing_hashes))
    self.assertEqual(0, tested.load())

    ddfp = os.path.join(self.dump_directory, "DEVICE.FIT")

    with open(ddfp, "w") as df:
      df.write("DEVICE.FIT")

    tested.on_drop = self.on_drop_returns_false

    self.assertTrue(os.path.exists(ddfp))
    tested.drop(ddfp, "TEST: Overridden on_drop returns False -> file should remain.")
    self.assertTrue(os.path.exists(ddfp))

  def test_drop_deletes_file_to_be_deleted(self):
    tested = FitFilesRepository(self.repo_directory)
    self.assertEqual(self.repo_directory, tested.root_directory_path)
    self.assertEqual(0, len(tested.existing_hashes))
    self.assertEqual(0, tested.load())

    ddfp = os.path.join(self.dump_directory, "DEVICE.FIT")

    with open(ddfp, "w") as df:
      df.write("DEVICE.FIT")

    self.assertTrue(os.path.exists(ddfp))
    tested.drop(ddfp, "TEST: Non-overridden on_drop returns True -> file should not remain.")
    self.assertFalse(os.path.exists(ddfp))

  def test_read_on_failed_scan_adds_zero_files(self):
    tested = FitFilesRepository(self.repo_directory)
    self.assertEqual(self.repo_directory, tested.root_directory_path)
    self.assertEqual(0, len(tested.existing_hashes))
    self.assertEqual(0, tested.load())

    self.assertEqual(0, len(tested.read(self.dump_directory).keys()))

  def test_read_on_successful_scan_adds_device_files_without_existing_device_files(self):
    tested = FitFilesRepository(self.repo_directory)
    self.assertEqual(self.repo_directory, tested.root_directory_path)
    self.assertEqual(0, len(tested.existing_hashes))
    self.assertEqual(0, tested.load())

    dfn, ddfp, dfh, rdfd, rdfp = self.get_device_fit_file_values()
    dxn, ddxp, dxh, rdxd, rdxp = self.get_device_xml_file_values()

    self.write_fit_file_to(self.dump_directory, dfn)
    self.write_fit_file_to(self.dump_directory, dxn)

    self.assertTrue(tested.scan(self.dump_directory))

    tested.on_read = lambda file_path, hash, hash_file_path: self.on_read_calls.append((file_path, hash, hash_file_path))

    self.assertFalse(os.path.exists(rdfp))
    self.assertFalse(os.path.exists(rdxp))
    self.assertTrue(os.path.exists(ddfp))
    self.assertTrue(os.path.exists(ddxp))

    read_result = tested.read(self.dump_directory)

    self.assertEqual(2, len(self.on_read_calls))

    on_read_device_fit:tuple[str, str, str] = None
    on_read_device_xml:tuple[str, str, str] = None

    for file_path, hash, hash_file_path in self.on_read_calls:
      if file_path.endswith(dfn):
        on_read_device_fit = (file_path, hash, hash_file_path)
      elif file_path.endswith(dxn):
        on_read_device_xml = (file_path, hash, hash_file_path)

    self.assertEqual(ddfp, on_read_device_fit[0])
    self.assertEqual(dfh, on_read_device_fit[1])
    self.assertEqual(rdfp, on_read_device_fit[2])

    self.assertEqual(ddxp, on_read_device_xml[0])
    self.assertEqual(dxh, on_read_device_xml[1])
    self.assertEqual(rdxp, on_read_device_xml[2])

    self.assertEqual(2, len(read_result.keys()))

    self.assertIn(dfh, read_result.keys())
    self.assertEqual(ddfp, read_result[dfh][0])
    self.assertEqual(rdfp, read_result[dfh][1])

    self.assertIn(dxh, read_result.keys())
    self.assertEqual(ddxp, read_result[dxh][0])
    self.assertEqual(rdxp, read_result[dxh][1])

    self.assertFalse(os.path.exists(ddfp))
    self.assertFalse(os.path.exists(ddxp))
    self.assertTrue(os.path.exists(rdfp))
    self.assertTrue(os.path.exists(rdxp))

  def test_read_on_successful_scan_adds_device_xml_file_with_existing_device_fit_file(self):
    tested = FitFilesRepository(self.repo_directory)
    self.assertEqual(self.repo_directory, tested.root_directory_path)
    self.assertEqual(0, len(tested.existing_hashes))

    dfn, ddfp, dfh, rdfd, rdfp = self.get_device_fit_file_values()
    dxn, ddxp, dxh, rdxd, rdxp = self.get_device_xml_file_values()

    self.write_fit_file_to(self.dump_directory, dfn)
    self.write_fit_file_to(self.dump_directory, dxn)

    os.makedirs(rdfd, exist_ok=False)
    self.write_fit_file_to(rdfd, dfn)

    self.assertEqual(1, tested.load()) # Forgot that we have to move this after creating the temporary file in the repo!

    self.assertTrue(tested.scan(self.dump_directory))

    tested.on_read = lambda file_path, hash, hash_file_path: self.on_read_calls.append((file_path, hash, hash_file_path))

    self.assertTrue(os.path.exists(rdfp))
    self.assertFalse(os.path.exists(rdxp))
    self.assertTrue(os.path.exists(ddfp))
    self.assertTrue(os.path.exists(ddxp))

    read_result = tested.read(self.dump_directory)

    self.assertEqual(1, len(self.on_read_calls))

    on_read_device_xml:tuple[str, str, str] = None

    for file_path, hash, hash_file_path in self.on_read_calls:
      if file_path.endswith(dxn):
        on_read_device_xml = (file_path, hash, hash_file_path)

    self.assertEqual(ddxp, on_read_device_xml[0])
    self.assertEqual(dxh, on_read_device_xml[1])
    self.assertEqual(rdxp, on_read_device_xml[2])

    self.assertEqual(1, len(read_result.keys()))

    self.assertIn(dxh, read_result.keys())
    self.assertEqual(ddxp, read_result[dxh][0])
    self.assertEqual(rdxp, read_result[dxh][1])

    self.assertFalse(os.path.exists(ddfp))
    self.assertFalse(os.path.exists(ddxp))
    self.assertTrue(os.path.exists(rdfp))
    self.assertTrue(os.path.exists(rdxp))

  def test_read_on_successful_scan_adds_device_fit_file_with_existing_device_xml_file(self):
    tested = FitFilesRepository(self.repo_directory)
    self.assertEqual(self.repo_directory, tested.root_directory_path)
    self.assertEqual(0, len(tested.existing_hashes))

    dfn, ddfp, dfh, rdfd, rdfp = self.get_device_fit_file_values()
    dxn, ddxp, dxh, rdxd, rdxp = self.get_device_xml_file_values()

    self.write_fit_file_to(self.dump_directory, dfn)
    self.write_fit_file_to(self.dump_directory, dxn)

    os.makedirs(rdxd, exist_ok=False)
    self.write_fit_file_to(rdxd, dxn)

    self.assertEqual(1, tested.load()) # Forgot that we have to move this after creating the temporary file in the repo!

    self.assertTrue(tested.scan(self.dump_directory))

    tested.on_read = lambda file_path, hash, hash_file_path: self.on_read_calls.append((file_path, hash, hash_file_path))

    self.assertFalse(os.path.exists(rdfp))
    self.assertTrue(os.path.exists(rdxp))
    self.assertTrue(os.path.exists(ddfp))
    self.assertTrue(os.path.exists(ddxp))

    read_result = tested.read(self.dump_directory)

    self.assertEqual(1, len(self.on_read_calls))

    on_read_device_fit:tuple[str, str, str] = None

    for file_path, hash, hash_file_path in self.on_read_calls:
      if file_path.endswith(dfn):
        on_read_device_fit = (file_path, hash, hash_file_path)

    self.assertEqual(ddfp, on_read_device_fit[0])
    self.assertEqual(dfh, on_read_device_fit[1])
    self.assertEqual(rdfp, on_read_device_fit[2])

    self.assertEqual(1, len(read_result.keys()))

    self.assertIn(dfh, read_result.keys())
    self.assertEqual(ddfp, read_result[dfh][0])
    self.assertEqual(rdfp, read_result[dfh][1])

    self.assertFalse(os.path.exists(ddfp))
    self.assertFalse(os.path.exists(ddxp))
    self.assertTrue(os.path.exists(rdfp))
    self.assertTrue(os.path.exists(rdxp))

  def test_read_on_successful_scan_adds_no_device_files_with_existing_device_files(self):
    tested = FitFilesRepository(self.repo_directory)
    self.assertEqual(self.repo_directory, tested.root_directory_path)
    self.assertEqual(0, len(tested.existing_hashes))

    dfn, ddfp, dfh, rdfd, rdfp = self.get_device_fit_file_values()
    dxn, ddxp, dxh, rdxd, rdxp = self.get_device_xml_file_values()

    self.write_fit_file_to(self.dump_directory, dfn)
    self.write_fit_file_to(self.dump_directory, dxn)

    os.makedirs(rdfd, exist_ok=False)
    self.write_fit_file_to(rdfd, dfn)

    os.makedirs(rdxd, exist_ok=False)
    self.write_fit_file_to(rdxd, dxn)

    self.assertEqual(2, tested.load())

    self.assertTrue(tested.scan(self.dump_directory))

    tested.on_read = lambda file_path, hash, hash_file_path: self.on_read_calls.append((file_path, hash, hash_file_path))

    self.assertTrue(os.path.exists(rdfp))
    self.assertTrue(os.path.exists(rdxp))
    self.assertTrue(os.path.exists(ddfp))
    self.assertTrue(os.path.exists(ddxp))

    read_result = tested.read(self.dump_directory)

    self.assertEqual(0, len(self.on_read_calls))
    self.assertEqual(0, len(read_result.keys()))

    self.assertFalse(os.path.exists(ddfp))
    self.assertFalse(os.path.exists(ddxp))
    self.assertTrue(os.path.exists(rdfp))
    self.assertTrue(os.path.exists(rdxp))

  def test_read_drops_pyfr_fits_file(self):
    tested = FitFilesRepository(self.repo_directory)
    self.assertEqual(self.repo_directory, tested.root_directory_path)
    self.assertEqual(0, len(tested.existing_hashes))

    dfn, ddfp, dfh, rdfd, rdfp = self.get_device_fit_file_values()
    dxn, ddxp, dxh, rdxd, rdxp = self.get_device_xml_file_values()

    self.write_fit_file_to(self.dump_directory, dfn)
    self.write_fit_file_to(self.dump_directory, dxn)

    os.makedirs(rdfd, exist_ok=False)
    self.write_fit_file_to(rdfd, dfn)

    os.makedirs(rdxd, exist_ok=False)
    self.write_fit_file_to(rdxd, dxn)

    self.assertEqual(2, tested.load())

    tsfp = self.write_fit_file_to(self.dump_directory, "TESTED.FITS")

    self.assertTrue(tested.scan(self.dump_directory))

    self.assertTrue(os.path.exists(tsfp))

    tested.on_read = lambda file_path, hash, hash_file_path: self.on_read_calls.append((file_path, hash, hash_file_path))

    self.assertTrue(os.path.exists(rdfp))
    self.assertTrue(os.path.exists(rdxp))
    self.assertTrue(os.path.exists(ddfp))
    self.assertTrue(os.path.exists(ddxp))

    read_result = tested.read(self.dump_directory)

    self.assertEqual(0, len(self.on_read_calls))
    self.assertEqual(0, len(read_result.keys()))

    self.assertFalse(os.path.exists(ddfp))
    self.assertFalse(os.path.exists(ddxp))
    self.assertTrue(os.path.exists(rdfp))
    self.assertTrue(os.path.exists(rdxp))

    self.assertFalse(os.path.exists(tsfp))
