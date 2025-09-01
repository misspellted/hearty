
import unittest
import tempfile
import os
import shutil

from hearty.repositories.hashers import sha3_512

class TestSha3512(unittest.TestCase):
  def setUp(self):
    # Always have a temporary directory for these tests.
    self.directory_path:str = tempfile.mkdtemp()

  def tearDown(self):
    # Ensure the temporary directory is deleted.
    if os.path.exists(self.directory_path):
      shutil.rmtree(self.directory_path)

  @unittest.skip("Not sure what a good smaller than default buffer size would be...")
  def test_file_size_smaller_than_smaller_buffer_size(self):
    pass

  @unittest.skip("Not sure what a good smaller than default buffer size would be...")
  def test_file_size_equal_to_smaller_buffer_size(self):
    pass

  @unittest.skip("Not sure what a good smaller than default buffer size would be...")
  def test_file_size_larger_than_smaller_buffer_size(self):
    pass

  # hello.txt in TestDeleteEmptyDirectory.test_directory_with_file_does_not_delete() sha3-512sum's to
  # 7e4bc18af174e0fe3017ea290f190c3a887bb0709bd8e9b1d145debbbdadbe08f8b01d769ee12da78f527bd482e9df0b5082cfd0cff7c4140e3d433e8248b5d7
  # (had to install the sha3sum package on arch to get the sha3-512sum command, lol)
  def test_file_size_smaller_than_default_buffer_size(self):
    self.assertTrue(os.path.exists(self.directory_path))
    # Create a temporary file.
    file_path:str = os.path.join(self.directory_path, "hello.txt")
    with open(file_path, "w") as file:
      file.write("hello!\n")
    self.assertTrue(os.path.exists(file_path))
    result = sha3_512(file_path)
    self.assertEqual("7e4bc18af174e0fe3017ea290f190c3a887bb0709bd8e9b1d145debbbdadbe08f8b01d769ee12da78f527bd482e9df0b5082cfd0cff7c4140e3d433e8248b5d7", result)

  @unittest.skip("Generating a 64k file might .. be interesting...")
  def test_file_size_equal_to_default_buffer_size(self):
    pass

  @unittest.skip("Generating a >64k file might .. be interesting...")
  def test_file_size_larger_than_default_buffer_size(self):
    pass

  @unittest.skip("Not sure what a good larger than default buffer size would be...")
  def test_file_size_smaller_than_larger_buffer_size(self):
    pass

  @unittest.skip("Not sure what a good larger than default buffer size would be...")
  def test_file_size_equal_to_larger_buffer_size(self):
    pass

  @unittest.skip("Not sure what a good larger than default buffer size would be...")
  def test_file_size_larger_than_larger_buffer_size(self):
    pass
