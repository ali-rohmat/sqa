"""
File Compressor Module
Handles compressing files and directories into ZIP archives.
"""

import os
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime


def get_file_hash(filepath: str) -> str:
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def compress_files(
    source_paths: list,
    output_path: str = None,
    compression_level: int = 9,
    include_metadata: bool = True,
) -> dict:
    """
    Compress one or more files/directories into a ZIP archive.

    Args:
        source_paths: List of file/directory paths to compress
        output_path: Output ZIP file path (auto-generated if None)
        compression_level: 0-9, higher = smaller file
        include_metadata: Include a metadata.txt inside ZIP

    Returns:
        dict with compression results
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"output/archive_{timestamp}.zip"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    results = {
        "output_path": output_path,
        "files_added": [],
        "total_original_size": 0,
        "compressed_size": 0,
        "compression_ratio": 0,
        "errors": [],
        "success": False,
    }

    try:
        with zipfile.ZipFile(
            output_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=compression_level,
        ) as zf:

            # Add metadata file if requested
            if include_metadata:
                meta_content = f"""Archive Metadata
================
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Compression Level: {compression_level}/9
Sources: {len(source_paths)} item(s)
"""
                zf.writestr("metadata.txt", meta_content)

            for source_path in source_paths:
                path = Path(source_path)

                if not path.exists():
                    results["errors"].append(f"Path not found: {source_path}")
                    continue

                if path.is_file():
                    # Single file
                    original_size = path.stat().st_size
                    results["total_original_size"] += original_size
                    zf.write(path, path.name)
                    results["files_added"].append(
                        {
                            "name": path.name,
                            "original_size": original_size,
                            "hash": get_file_hash(str(path)),
                        }
                    )

                elif path.is_dir():
                    # Directory - walk all files
                    for root, dirs, files in os.walk(path):
                        # Skip hidden directories
                        dirs[:] = [d for d in dirs if not d.startswith(".")]
                        for filename in files:
                            if filename.startswith("."):
                                continue
                            file_path = Path(root) / filename
                            arcname = file_path.relative_to(path.parent)
                            original_size = file_path.stat().st_size
                            results["total_original_size"] += original_size
                            zf.write(file_path, arcname)
                            results["files_added"].append(
                                {
                                    "name": str(arcname),
                                    "original_size": original_size,
                                    "hash": get_file_hash(str(file_path)),
                                }
                            )

        results["compressed_size"] = os.path.getsize(output_path)

        if results["total_original_size"] > 0:
            results["compression_ratio"] = round(
                (1 - results["compressed_size"] / results["total_original_size"]) * 100,
                2,
            )

        results["success"] = True

    except Exception as e:
        results["errors"].append(str(e))

    return results


def list_zip_contents(zip_path: str) -> list:
    """List all files inside a ZIP archive."""
    contents = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            contents.append(
                {
                    "filename": info.filename,
                    "compressed_size": info.compress_size,
                    "original_size": info.file_size,
                    "date_modified": datetime(*info.date_time).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }
            )
    return contents
