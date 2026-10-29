# Dataset Batch Copy Utility

A Python script that traverses a source folder and copies dataset files to a target destination using `.env` settings. It supports semicolon-separated file lists, automatic filtering for `.data` extensions, optional batch renaming, interactive overwrite protection with friendly exception handling, and file-based logging.

---

## Files

- [copy_file.py](file:///home/kafeiaulait/HI-634-Assign_1/copy_file.py): Main Python script.
- [.env](file:///home/kafeiaulait/HI-634-Assign_1/.env): Active configuration file.
- [.env.example](file:///home/kafeiaulait/HI-634-Assign_1/.env.example): Template configuration file.
- [dataset_copy.log](file:///home/kafeiaulait/HI-634-Assign_1/dataset_copy.log): Auto-generated execution log file.

---

## Logging Configuration

The log filename is defined as a Python constant near the top of [copy_file.py](file:///home/kafeiaulait/HI-634-Assign_1/copy_file.py):

```python
# ==============================================================================
# CONSTANTS
# ==============================================================================
LOG_FILE_NAME = "dataset_copy.log"
```

The log file is automatically created in the exact same directory where the script resides (`03.dataset_copy/`).

---

## Configuration (`.env`)

```ini
# Relative paths from 03.dataset_copy/
SOURCE_FOLDER=../source_datafiles/heart+disease
TARGET_FOLDER=../project/data/raw

# Semicolon-separated list of files (or *.data for all .data files)
SOURCE_FILES=processed.cleveland.data; processed.hungarian.data; processed.switzerland.data; processed.va.data

# Rename flag: Y to rename in target, N to keep original names
RENAME_FILE=N

# Semicolon-separated target names (only used if RENAME_FILE=Y)
TARGET_FILES=cleveland.data; hungarian.data; switzerland.data; va.data
```

---

## Features

1. **File Logging**: Logs script execution timestamps, path resolutions, skipped files, overwrite decisions, exceptions, and summary statistics to a file defined by `LOG_FILE_NAME`.
2. **Relative Paths**: Automatically resolves paths relative to the script's directory, making it drive-independent (works on `T:`, `C:`, or any other drive/OS).
3. **Semicolon-Separated File List**: Allows specifying multiple files in `SOURCE_FILES` separated by `;`.
4. **`.data` Extension Filter**: Only files ending with `.data` are processed. Files with other extensions (e.g. `heart-disease.names` or `.txt`) are safely skipped with a notice and logged.
5. **Folder Traversal**: Checks direct paths and searches subfolders for any listed files.
6. **Interactive Overwrite Protection**: If a file already exists in the target directory, prompts `Do you want to overwrite it? (Y/N): `.
   - If `N`, raises a `FileExistsError` caught by a `try..except` block with a friendly message and logged warning, then proceeds to the next file without aborting the batch.
7. **Optional Batch Renaming**: When `RENAME_FILE=Y`, maps source files to `TARGET_FILES` 1-to-1.
