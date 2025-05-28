"""
File Tools Module
================

This module provides essential utilities for file operations, including:
- File reading/writing
- Directory operations
- File validation
- File compression/decompression
- File size management
- File type handling
- Error handling
- Async/await support

Features:
- Safe file operations with error handling
- Efficient file reading/writing
- Directory management
- File compression support
- File type validation
- Size management
- Temporary file handling
- Async operations
"""

import logging
import os
import shutil
import tempfile
import zipfile
import tarfile
import gzip
import json
import csv
import yaml
from typing import Any, Dict, List, Optional, Union, AsyncGenerator, Generator
from pathlib import Path
import aiofiles
from contextlib import contextmanager
from functools import wraps

logger = logging.getLogger(__name__)

class FileError(Exception):
    """Custom exception for file-related errors."""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(message)

class FileTools:
    """Class containing various file utility functions."""

    def __init__(self, base_dir: str = None):
        """Initialize file tools with optional base directory.

        Args:
            base_dir (str, optional): Base directory for file operations
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()

    @staticmethod
    def validate_path(path: Union[str, Path]) -> Path:
        """Validate and normalize a file path.

        Args:
            path (str or Path): Input path

        Returns:
            Path: Validated and normalized path

        Raises:
            ValueError: If path is invalid
        """
        if not path:
            raise ValueError("Path cannot be empty")
        
        path = Path(path)
        if not path.exists():
            raise ValueError(f"Path does not exist: {path}")
        
        return path.resolve()

    @staticmethod
    def get_file_size(path: Union[str, Path]) -> int:
        """Get the size of a file in bytes.

        Args:
            path (str or Path): File path

        Returns:
            int: File size in bytes

        Raises:
            FileError: If file cannot be accessed
        """
        try:
            return os.path.getsize(str(path))
        except OSError as e:
            raise FileError(f"Error getting file size: {e}", e)

    @staticmethod
    def get_directory_size(path: Union[str, Path]) -> int:
        """Get the total size of a directory in bytes.

        Args:
            path (str or Path): Directory path

        Returns:
            int: Directory size in bytes

        Raises:
            FileError: If directory cannot be accessed
        """
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(str(path)):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
            return total_size
        except OSError as e:
            raise FileError(f"Error getting directory size: {e}", e)

    @staticmethod
    def read_json_file(path: Union[str, Path]) -> Dict:
        """Read and parse a JSON file.

        Args:
            path (str or Path): JSON file path

        Returns:
            dict: Parsed JSON data

        Raises:
            FileError: If file cannot be read or parsed
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            raise FileError(f"Error reading JSON file: {e}", e)

    @staticmethod
    def write_json_file(data: Dict, path: Union[str, Path], indent: int = 2) -> None:
        """Write data to a JSON file.

        Args:
            data (dict): Data to write
            path (str or Path): Output file path
            indent (int): JSON indentation level

        Raises:
            FileError: If file cannot be written
        """
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
        except IOError as e:
            raise FileError(f"Error writing JSON file: {e}", e)

    @staticmethod
    def read_yaml_file(path: Union[str, Path]) -> Dict:
        """Read and parse a YAML file.

        Args:
            path (str or Path): YAML file path

        Returns:
            dict: Parsed YAML data

        Raises:
            FileError: If file cannot be read or parsed
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except (IOError, yaml.YAMLError) as e:
            raise FileError(f"Error reading YAML file: {e}", e)

    @staticmethod
    def write_yaml_file(data: Dict, path: Union[str, Path]) -> None:
        """Write data to a YAML file.

        Args:
            data (dict): Data to write
            path (str or Path): Output file path

        Raises:
            FileError: If file cannot be written
        """
        try:
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False)
        except IOError as e:
            raise FileError(f"Error writing YAML file: {e}", e)

    @staticmethod
    def read_csv_file(path: Union[str, Path]) -> List[Dict]:
        """Read and parse a CSV file.

        Args:
            path (str or Path): CSV file path

        Returns:
            list: List of dictionaries (one per row)

        Raises:
            FileError: If file cannot be read or parsed
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return list(csv.DictReader(f))
        except (IOError, csv.Error) as e:
            raise FileError(f"Error reading CSV file: {e}", e)

    @staticmethod
    def write_csv_file(data: List[Dict], path: Union[str, Path]) -> None:
        """Write data to a CSV file.

        Args:
            data (list): List of dictionaries to write
            path (str or Path): Output file path

        Raises:
            FileError: If file cannot be written
        """
        try:
            if not data:
                return

            fieldnames = data[0].keys()
            with open(path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
        except (IOError, csv.Error) as e:
            raise FileError(f"Error writing CSV file: {e}", e)

    @staticmethod
    def create_temp_file(suffix: str = None) -> Path:
        """Create a temporary file.

        Args:
            suffix (str, optional): File suffix

        Returns:
            Path: Path to temporary file
        """
        return Path(tempfile.mkstemp(suffix=suffix)[1])

    @staticmethod
    def create_temp_directory() -> Path:
        """Create a temporary directory.

        Returns:
            Path: Path to temporary directory
        """
        return Path(tempfile.mkdtemp())

    @staticmethod
    def zip_directory(
        source_dir: Union[str, Path],
        output_path: Union[str, Path],
        compression: int = zipfile.ZIP_DEFLATED
    ) -> None:
        """Compress a directory to a ZIP file.

        Args:
            source_dir (str or Path): Directory to compress
            output_path (str or Path): Output ZIP file path
            compression (int): Compression level

        Raises:
            FileError: If compression fails
        """
        try:
            with zipfile.ZipFile(output_path, 'w', compression=compression) as zipf:
                for root, _, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
        except Exception as e:
            raise FileError(f"Error creating ZIP file: {e}", e)

    @staticmethod
    def unzip_file(
        zip_path: Union[str, Path],
        output_dir: Union[str, Path]
    ) -> None:
        """Extract a ZIP file to a directory.

        Args:
            zip_path (str or Path): ZIP file path
            output_dir (str or Path): Output directory

        Raises:
            FileError: If extraction fails
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(output_dir)
        except Exception as e:
            raise FileError(f"Error extracting ZIP file: {e}", e)

    @staticmethod
    def create_tarball(
        source_dir: Union[str, Path],
        output_path: Union[str, Path],
        compression: str = 'gz'
    ) -> None:
        """Create a tarball from a directory.

        Args:
            source_dir (str or Path): Directory to compress
            output_path (str or Path): Output tarball path
            compression (str): Compression type ('gz', 'bz2', 'xz')

        Raises:
            FileError: If tarball creation fails
        """
        try:
            with tarfile.open(output_path, f'w:{compression}') as tar:
                tar.add(source_dir, arcname=os.path.basename(source_dir))
        except Exception as e:
            raise FileError(f"Error creating tarball: {e}", e)

    @staticmethod
    def extract_tarball(
        tar_path: Union[str, Path],
        output_dir: Union[str, Path]
    ) -> None:
        """Extract a tarball to a directory.

        Args:
            tar_path (str or Path): Tarball path
            output_dir (str or Path): Output directory

        Raises:
            FileError: If extraction fails
        """
        try:
            with tarfile.open(tar_path, 'r:*') as tar:
                tar.extractall(output_dir)
        except Exception as e:
            raise FileError(f"Error extracting tarball: {e}", e)

    @staticmethod
    async def async_read_file(path: Union[str, Path]) -> str:
        """Asynchronously read a file.

        Args:
            path (str or Path): File path

        Returns:
            str: File contents

        Raises:
            FileError: If file cannot be read
        """
        try:
            async with aiofiles.open(path, mode='r', encoding='utf-8') as f:
                return await f.read()
        except Exception as e:
            raise FileError(f"Error reading file asynchronously: {e}", e)

    @staticmethod
    async def async_write_file(
        content: str,
        path: Union[str, Path]
    ) -> None:
        """Asynchronously write to a file.

        Args:
            content (str): Content to write
            path (str or Path): File path

        Raises:
            FileError: If file cannot be written
        """
        try:
            async with aiofiles.open(path, mode='w', encoding='utf-8') as f:
                await f.write(content)
        except Exception as e:
            raise FileError(f"Error writing file asynchronously: {e}", e)

    @staticmethod
    def atomic_write_file(
        content: str,
        path: Union[str, Path]
    ) -> None:
        """Atomically write to a file.

        Args:
            content (str): Content to write
            path (str or Path): File path

        Raises:
            FileError: If file cannot be written
        """
        try:
            temp_path = f"{path}.tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(content)
            os.replace(temp_path, path)
        except Exception as e:
            raise FileError(f"Error writing file atomically: {e}", e)

    @staticmethod
    def copy_file(
        src: Union[str, Path],
        dst: Union[str, Path],
        overwrite: bool = True
    ) -> None:
        """Copy a file.

        Args:
            src (str or Path): Source file path
            dst (str or Path): Destination file path
            overwrite (bool): Whether to overwrite existing file

        Raises:
            FileError: If copy fails
        """
        try:
            if not overwrite and os.path.exists(dst):
                raise FileError(f"Destination file already exists: {dst}")
            shutil.copy2(src, dst)
        except Exception as e:
            raise FileError(f"Error copying file: {e}", e)

    @staticmethod
    def move_file(
        src: Union[str, Path],
        dst: Union[str, Path],
        overwrite: bool = True
    ) -> None:
        """Move a file.

        Args:
            src (str or Path): Source file path
            dst (str or Path): Destination file path
            overwrite (bool): Whether to overwrite existing file

        Raises:
            FileError: If move fails
        """
        try:
            if not overwrite and os.path.exists(dst):
                raise FileError(f"Destination file already exists: {dst}")
            shutil.move(src, dst)
        except Exception as e:
            raise FileError(f"Error moving file: {e}", e)

    @staticmethod
    def delete_file(path: Union[str, Path]) -> None:
        """Delete a file.

        Args:
            path (str or Path): File path

        Raises:
            FileError: If deletion fails
        """
        try:
            os.remove(path)
        except Exception as e:
            raise FileError(f"Error deleting file: {e}", e)

    @staticmethod
    def delete_directory(path: Union[str, Path], recursive: bool = True) -> None:
        """Delete a directory.

        Args:
            path (str or Path): Directory path
            recursive (bool): Whether to delete recursively

        Raises:
            FileError: If deletion fails
        """
        try:
            if recursive:
                shutil.rmtree(path)
            else:
                os.rmdir(path)
        except Exception as e:
            raise FileError(f"Error deleting directory: {e}", e)

    @staticmethod
    def list_files(
        directory: Union[str, Path],
        recursive: bool = False,
        pattern: str = None
    ) -> List[Path]:
        """List files in a directory.

        Args:
            directory (str or Path): Directory path
            recursive (bool): Whether to search recursively
            pattern (str): File pattern to match

        Returns:
            list: List of file paths
        """
        path = Path(directory)
        if recursive:
            files = list(path.rglob(pattern or '*'))
        else:
            files = list(path.glob(pattern or '*'))
        return [f for f in files if f.is_file()]

    @staticmethod
    def get_file_extension(path: Union[str, Path]) -> str:
        """Get file extension.

        Args:
            path (str or Path): File path

        Returns:
            str: File extension (including leading .)
        """
        return Path(path).suffix.lower()

    @staticmethod
    def get_file_name_without_extension(path: Union[str, Path]) -> str:
        """Get file name without extension.

        Args:
            path (str or Path): File path

        Returns:
            str: File name without extension
        """
        return Path(path).stem

    @staticmethod
    def get_file_size_human_readable(size_bytes: int) -> str:
        """Convert file size to human-readable format.

        Args:
            size_bytes (int): Size in bytes

        Returns:
            str: Human-readable size (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"

# Example usage:
if __name__ == "__main__":
    # Initialize file tools
    ft = FileTools()

    # File operations
    temp_file = ft.create_temp_file(suffix='.txt')
    ft.atomic_write_file("Hello, World!", temp_file)
    content = ft.async_read_file(temp_file)
    
    # Directory operations
    temp_dir = ft.create_temp_directory()
    ft.zip_directory("source_dir", "archive.zip")
    ft.unzip_file("archive.zip", "extracted_dir")
    
    # File format operations
    data = {"key": "value"}
    ft.write_json_file(data, "data.json")
    loaded_data = ft.read_json_file("data.json")
    
    # File size operations
    size = ft.get_file_size("data.json")
    human_size = ft.get_file_size_human_readable(size)
    
    # Clean up
    ft.delete_file(temp_file)
    ft.delete_directory(temp_dir, recursive=True)