from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from gera1.adapters.local_files import BoundedFileError, read_bounded_regular_file
from gera1.adapters.strict_json import StrictJsonError, loads_strict_json


class BoundedLocalFileTests(unittest.TestCase):
    def test_regular_file_is_read_once_within_limit(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "input.txt"
            path.write_bytes(b"safe local input")

            self.assertEqual(
                b"safe local input",
                read_bounded_regular_file(path, maximum_bytes=32),
            )

    def test_file_over_limit_is_rejected(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "input.txt"
            path.write_bytes(b"12345")

            with self.assertRaises(BoundedFileError) as raised:
                read_bounded_regular_file(path, maximum_bytes=4)
            self.assertEqual("file_too_large", raised.exception.code)

    def test_directory_is_rejected_as_unsafe(self):
        with TemporaryDirectory() as directory:
            with self.assertRaises(BoundedFileError) as raised:
                read_bounded_regular_file(directory, maximum_bytes=32)
            self.assertEqual("unsafe_file", raised.exception.code)


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_object_key_is_rejected(self):
        with self.assertRaisesRegex(StrictJsonError, "Duplicate JSON key"):
            loads_strict_json('{"business_id":"one","business_id":"two"}')

    def test_non_standard_numeric_constant_is_rejected(self):
        with self.assertRaisesRegex(StrictJsonError, "Non-standard JSON constant"):
            loads_strict_json('{"quantity":NaN}', decimal_numbers=True)


if __name__ == "__main__":
    unittest.main()
