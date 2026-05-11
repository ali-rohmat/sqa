"""
Unit Tests for DevTools Suite
Tests compressor and selenium modules independently.
"""

import os
import sys
import zipfile
import unittest
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.compressor import compress_files, list_zip_contents, get_file_hash
from src.selenium_tests import run_mock_selenium_tests, TestResult, TestSuite


class TestCompressor(unittest.TestCase):
    """Tests for the ZIP compression module."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(self.output_dir)

        # Create sample files
        self.file1 = os.path.join(self.test_dir, "hello.txt")
        self.file2 = os.path.join(self.test_dir, "data.csv")

        with open(self.file1, "w") as f:
            f.write("Hello, World!\n" * 100)

        with open(self.file2, "w") as f:
            f.write("id,name,value\n")
            for i in range(50):
                f.write(f"{i},item_{i},{i * 10}\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_compress_single_file(self):
        """Should compress a single file successfully."""
        output = os.path.join(self.output_dir, "test.zip")
        result = compress_files([self.file1], output)

        self.assertTrue(result["success"])
        self.assertTrue(os.path.exists(output))
        self.assertGreater(result["compressed_size"], 0)
        self.assertEqual(len([f for f in result["files_added"] if "metadata" not in f["name"]]), 1)

    def test_compress_multiple_files(self):
        """Should compress multiple files into one archive."""
        output = os.path.join(self.output_dir, "multi.zip")
        result = compress_files([self.file1, self.file2], output)

        self.assertTrue(result["success"])
        # 2 source files + metadata.txt = 3 entries
        self.assertGreaterEqual(len(result["files_added"]), 2)

    def test_compress_directory(self):
        """Should recursively compress a directory."""
        sub_dir = os.path.join(self.test_dir, "subdir")
        os.makedirs(sub_dir)
        for i in range(3):
            with open(os.path.join(sub_dir, f"file{i}.txt"), "w") as f:
                f.write(f"Content {i}\n" * 50)

        output = os.path.join(self.output_dir, "dir.zip")
        result = compress_files([sub_dir], output)

        self.assertTrue(result["success"])
        self.assertEqual(len([f for f in result["files_added"] if "metadata" not in f["name"]]), 3)

    def test_compression_reduces_size(self):
        """Compressed file should be smaller than original."""
        output = os.path.join(self.output_dir, "compressed.zip")
        result = compress_files([self.file1], output)

        self.assertTrue(result["success"])
        self.assertGreater(result["compression_ratio"], 0)

    def test_missing_file_reports_error(self):
        """Should report error for non-existent path."""
        output = os.path.join(self.output_dir, "err.zip")
        result = compress_files(["/nonexistent/path/file.txt"], output)

        self.assertGreater(len(result["errors"]), 0)

    def test_zip_is_valid(self):
        """Output should be a valid ZIP file."""
        output = os.path.join(self.output_dir, "valid.zip")
        compress_files([self.file1], output)

        self.assertTrue(zipfile.is_zipfile(output))

    def test_list_zip_contents(self):
        """Should list files in an existing ZIP."""
        output = os.path.join(self.output_dir, "list_test.zip")
        compress_files([self.file1, self.file2], output)

        contents = list_zip_contents(output)
        self.assertIsInstance(contents, list)
        self.assertGreater(len(contents), 0)
        self.assertIn("filename", contents[0])
        self.assertIn("original_size", contents[0])

    def test_file_hash_consistency(self):
        """Same file should always produce same hash."""
        h1 = get_file_hash(self.file1)
        h2 = get_file_hash(self.file1)
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 32)  # MD5 hex length

    def test_metadata_included(self):
        """Should include metadata.txt by default."""
        output = os.path.join(self.output_dir, "meta.zip")
        compress_files([self.file1], output, include_metadata=True)

        contents = list_zip_contents(output)
        names = [c["filename"] for c in contents]
        self.assertIn("metadata.txt", names)

    def test_metadata_excluded(self):
        """Should exclude metadata when include_metadata=False."""
        output = os.path.join(self.output_dir, "nometa.zip")
        compress_files([self.file1], output, include_metadata=False)

        contents = list_zip_contents(output)
        names = [c["filename"] for c in contents]
        self.assertNotIn("metadata.txt", names)

    def test_compression_levels(self):
        """Level 9 should produce smaller or equal file than level 1."""
        out1 = os.path.join(self.output_dir, "level1.zip")
        out9 = os.path.join(self.output_dir, "level9.zip")

        compress_files([self.file1], out1, compression_level=1)
        compress_files([self.file1], out9, compression_level=9)

        size1 = os.path.getsize(out1)
        size9 = os.path.getsize(out9)
        self.assertLessEqual(size9, size1)


class TestSeleniumModule(unittest.TestCase):
    """Tests for the Selenium testing module."""

    def setUp(self):
        self.suite = run_mock_selenium_tests("https://example.com")

    def test_suite_returns_results(self):
        """Test suite should contain results."""
        self.assertIsInstance(self.suite, TestSuite)
        self.assertGreater(self.suite.total, 0)

    def test_results_have_required_fields(self):
        """Each result should have name, status, duration, message."""
        for result in self.suite.results:
            self.assertIsInstance(result, TestResult)
            self.assertIn(result.status, ["PASS", "FAIL", "SKIP", "ERROR"])
            self.assertIsInstance(result.duration, float)
            self.assertGreater(result.duration, 0)
            self.assertIsInstance(result.name, str)
            self.assertTrue(len(result.name) > 0)

    def test_suite_statistics(self):
        """Suite statistics should be consistent."""
        self.assertEqual(
            self.suite.passed + self.suite.failed + self.suite.skipped + self.suite.errors,
            self.suite.total
        )

    def test_success_rate_range(self):
        """Success rate should be between 0 and 100."""
        self.assertGreaterEqual(self.suite.success_rate, 0)
        self.assertLessEqual(self.suite.success_rate, 100)

    def test_different_url_runs(self):
        """Running with different URLs should both return valid suites."""
        suite1 = run_mock_selenium_tests("https://google.com")
        suite2 = run_mock_selenium_tests("https://github.com")

        self.assertGreater(suite1.total, 0)
        self.assertGreater(suite2.total, 0)

    def test_suite_has_name(self):
        """Suite name should reference the URL."""
        self.assertIn("example.com", self.suite.name)


if __name__ == "__main__":
    # Pretty test runner
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestCompressor))
    suite.addTests(loader.loadTestsFromTestCase(TestSeleniumModule))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    sys.exit(0 if result.wasSuccessful() else 1)
