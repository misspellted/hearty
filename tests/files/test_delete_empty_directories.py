
import unittest
import tempfile
import os
import shutil

from hearty.files import delete_empty_directory

class TestDeleteEmptyDirectory(unittest.TestCase):
  def setUp(self):
    # Always have a temporary directory for these tests.
    self.directory_path:str = tempfile.mkdtemp()

  def tearDown(self):
    # Ensure the temporary directory is deleted.
    if os.path.exists(self.directory_path):
      shutil.rmtree(self.directory_path)

  def test_directory_already_empty(self):
    self.assertTrue(os.path.exists(self.directory_path))
    delete_empty_directory(self.directory_path)
    self.assertFalse(os.path.exists(self.directory_path))

  def test_directory_with_file_does_not_delete(self):
    self.assertTrue(os.path.exists(self.directory_path))
    # Create a temporary file.
    file_path:str = os.path.join(self.directory_path, "hello.txt")
    with open(file_path, "w") as file:
      file.write("hello!\n")
    self.assertTrue(os.path.exists(file_path))
    delete_empty_directory(self.directory_path)
    self.assertTrue(os.path.exists(self.directory_path))

  def test_directory_with_empty_subdirectory_does_delete(self):
    self.assertTrue(os.path.exists(self.directory_path))
    # Create a temporary directory inside it.
    ed_path = os.path.join(self.directory_path, "empty")
    os.mkdir(ed_path)
    self.assertTrue(os.path.exists(ed_path))
    delete_empty_directory(self.directory_path)
    self.assertFalse(os.path.exists(self.directory_path))

  def test_directory_with_file_in_subdirectory_does_not_delete(self):
    self.assertTrue(os.path.exists(self.directory_path))
    # Create a temporary directory inside it.
    fd_path = os.path.join(self.directory_path, "files")
    os.mkdir(fd_path)
    self.assertTrue(os.path.exists(fd_path))
    # Create a temporary file.
    file_path:str = os.path.join(fd_path, "world.log")
    with open(file_path, "w") as file:
      file.write("world\n")
    self.assertTrue(os.path.exists(file_path))
    delete_empty_directory(self.directory_path)
    self.assertTrue(os.path.exists(self.directory_path))
