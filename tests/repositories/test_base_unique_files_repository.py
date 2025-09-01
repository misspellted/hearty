
import unittest
import tempfile
import os
import shutil

from hearty.repositories.base import *

class TestUniqueFilesRepository(unittest.TestCase):
  def setUp(self):
    # Utilize temporary directories for these tests.
    self.repo_directory:str = tempfile.mkdtemp()
    self.dump_directory:str = tempfile.mkdtemp()

    # Intercept calls as needed and the argument values of those calls.
    self.on_drop_calls:list[tuple[str, str]] = []
    self.on_file_calls:list[str] = []
    self.on_read_calls:list[tuple[str, str, str]] = []

  def tearDown(self):
    # Ensure the temporary directories are deleted.
    if os.path.exists(self.dump_directory):
      shutil.rmtree(self.dump_directory)

    if os.path.exists(self.repo_directory):
      shutil.rmtree(self.repo_directory)

  def test_new_instance_defaults_to_sha3_512_hashes(self):
    tested = UniqueFilesRepository(self.repo_directory)

    self.assertEqual(self.repo_directory, tested.root_directory)
    self.assertEqual(0, len(tested.existing_hashes))
    self.assertEqual(sha3_512, tested.hasher)

  def write_file(self, directory:str, name:str) -> str:
    fp = os.path.join(directory, name)
    with open(fp, "w") as f:
      f.write(name)
    return fp

  def test_load_without_existing_hashes_and_without_new_hashes(self):
    tested = UniqueFilesRepository(self.repo_directory)

    self.assertEqual(0, len(tested.existing_hashes))
    self.assertEqual(0, tested.load())
    self.assertEqual(0, len(tested.existing_hashes))

  def test_load_without_existing_hashes_and_with_new_hashes(self):
    tested = UniqueFilesRepository(self.repo_directory)

    self.assertEqual(0, len(tested.existing_hashes))

    os.makedirs(os.path.join(self.repo_directory, "deadbeef"))

    self.assertEqual(1, tested.load())
    self.assertEqual(1, len(tested.existing_hashes))
    self.assertEqual("deadbeef", tested.existing_hashes[0])

  def test_load_with_existing_hashes_and_without_new_hashes(self):
    tested = UniqueFilesRepository(self.repo_directory)

    tested.existing_hashes.append("deadbeef")

    self.assertEqual(0, tested.load())
    self.assertEqual(1, len(tested.existing_hashes))
    self.assertEqual("deadbeef", tested.existing_hashes[0])

  def test_load_with_existing_hashes_and_with_new_hashes(self):
    tested = UniqueFilesRepository(self.repo_directory)

    tested.existing_hashes.append("deadbeef")

    os.makedirs(os.path.join(self.repo_directory, "beadfeed"))

    self.assertEqual(1, tested.load())
    self.assertEqual(2, len(tested.existing_hashes))
    self.assertEqual("deadbeef", tested.existing_hashes[0])
    self.assertEqual("beadfeed", tested.existing_hashes[1])

  def test_scan_fails_with_file_path(self):
    tested = UniqueFilesRepository(self.repo_directory)

    fp = self.write_file(self.dump_directory, "temp.txt")
    self.assertTrue(os.path.exists(fp))

    self.assertFalse(tested.scan(fp))

  def test_scan_succeeds_with_directory_path(self):
    tested = UniqueFilesRepository(self.repo_directory)

    self.assertTrue(tested.scan(self.dump_directory))

  def test_drop_deletes_file_to_be_deleted(self):
    tested = UniqueFilesRepository(self.repo_directory)

    fp = self.write_file(self.dump_directory, "temp.txt")
    self.assertTrue(os.path.exists(fp))

    tested.drop(fp, "TEST: Default on_drop returns True -> file should not remain.")
    self.assertFalse(os.path.exists(fp))

  def on_drop_returns_false(self, file_path:str, reason:str) -> bool:
    self.on_drop_calls.append((file_path, reason))
    return False

  def test_drop_leaves_file_to_be_deleted(self):
    tested = UniqueFilesRepository(self.repo_directory)

    fp = self.write_file(self.dump_directory, "temp.txt")
    self.assertTrue(os.path.exists(fp))

    tested.on_drop = self.on_drop_returns_false

    tested.drop(fp, "TEST: Overridden on_drop returns False -> file should remain.")
    self.assertTrue(os.path.exists(fp))

    self.assertEqual(1, len(self.on_drop_calls))

  def scan_returns_false(self, dump_directory:str) -> bool:
    return False

  def test_read_on_failing_scan_adds_zero_hashes(self):
    tested = UniqueFilesRepository(self.repo_directory)
    tested.scan = self.scan_returns_false

    self.assertEqual(0, len(tested.read(self.dump_directory).keys()))
    self.assertEqual(0, len(tested.existing_hashes))

  def test_read_on_succeeding_scan_with_zero_files_adds_zero_hashes(self):
    tested = UniqueFilesRepository(self.repo_directory)
    
    self.assertEqual(0, len(tested.read(self.dump_directory).keys()))
    self.assertEqual(0, len(tested.existing_hashes))

  def on_file_returns_false(self, file_path:str) -> bool:
    self.on_file_calls.append(file_path)
    return False

  def test_read_on_succeeding_scan_with_skipped_file_adds_zero_hashes(self):
    tested = UniqueFilesRepository(self.repo_directory)
    tested.on_file = self.on_file_returns_false

    fp = self.write_file(self.dump_directory, "temp.txt")
    self.assertTrue(os.path.exists(fp))
    
    self.assertEqual(0, len(tested.read(self.dump_directory).keys()))
    self.assertEqual(0, len(tested.existing_hashes))

  def on_file_returns_true(self, file_path:str) -> bool:
    self.on_file_calls.append(file_path)
    return True

  def test_read_on_succeeding_scan_drops_file_with_existing_hash_adds_zero_hashes(self):
    tested = UniqueFilesRepository(self.repo_directory)
    # `echo "temp.txt" | sha3-512sum` -- well, that was easy to create the hash.. nice!
    # tested.existing_hashes.append("659d63c1fc55479e682e6eec57cc56bca4a7e9d02e9ef462c06a4311cc1cb69ceb22c674bd78f9c9571aa611447444fc944154e777a8e68cd6634e041a38da84")
    # Actually... the "81bc1908689d7e00367e159a0793780ba7d014e2e3217e97e9a87546f69d8174748f73c33cb039415c78f942470725e5991e10f71d742ad92231287f495883dc" was 'wrong'...
    # because... echo adds a new line at the end of the input by default.
    # The correct command to generate hashes here is to add the `-n` switch: `echo -n "temp.txt" | sha3-512sum`, which suppresses the hidden new line addition.
    # Thew new  result is the one to inject: 659d63c1fc55479e682e6eec57cc56bca4a7e9d02e9ef462c06a4311cc1cb69ceb22c674bd78f9c9571aa611447444fc944154e777a8e68cd6634e041a38da84
    tested.existing_hashes.append("659d63c1fc55479e682e6eec57cc56bca4a7e9d02e9ef462c06a4311cc1cb69ceb22c674bd78f9c9571aa611447444fc944154e777a8e68cd6634e041a38da84")
    tested.on_file = self.on_file_returns_true
    tested.on_drop = self.on_drop_returns_false # It'll get cleaned up with tearDown().

    fp = self.write_file(self.dump_directory, "temp.txt")
    self.assertTrue(os.path.exists(fp))
    
    self.assertEqual(0, len(tested.read(self.dump_directory).keys()))
    self.assertEqual(1, len(tested.existing_hashes))
    self.assertEqual(1, len(self.on_file_calls))
    self.assertEqual(fp, self.on_file_calls[0])
    self.assertEqual(1, len(self.on_drop_calls))
    self.assertEqual(fp, self.on_drop_calls[0][0])
    self.assertTrue("duplicate" in self.on_drop_calls[0][1])

  def on_read(self, file_path:str, hash:str, hash_file_path:str):
    self.on_read_calls.append((file_path, hash, hash_file_path))

  def test_read_on_succeeding_scan_reads_file_without_existing_hashes_adds_one_hash(self):
    tested = UniqueFilesRepository(self.repo_directory)
    self.assertEqual(0, len(tested.existing_hashes))

    tested.on_file = self.on_file_returns_true
    tested.on_read = self.on_read

    fp = self.write_file(self.dump_directory, "temp.txt")
    self.assertTrue(os.path.exists(fp))
    hash = "659d63c1fc55479e682e6eec57cc56bca4a7e9d02e9ef462c06a4311cc1cb69ceb22c674bd78f9c9571aa611447444fc944154e777a8e68cd6634e041a38da84"

    result:dict[str, tuple[str, str]] = tested.read(self.dump_directory)

    self.assertEqual(1, len(result.keys()))
    self.assertTrue(hash in result.keys())
    self.assertEqual(fp, result[hash][0])
    self.assertEqual(os.path.join(self.repo_directory, hash, "_", "temp.txt"), result[hash][1])
    self.assertEqual(1, len(self.on_file_calls))
    self.assertEqual(fp, self.on_file_calls[0])
    self.assertEqual(1, len(self.on_read_calls))
    self.assertEqual(fp, self.on_read_calls[0][0])
    self.assertEqual(hash, self.on_read_calls[0][1])
    self.assertEqual(os.path.join(self.repo_directory, hash, "_", "temp.txt"), self.on_read_calls[0][2])
