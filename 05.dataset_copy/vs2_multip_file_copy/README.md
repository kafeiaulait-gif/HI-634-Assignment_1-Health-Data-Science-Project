# Dataset Batch Copy Utility

A Python script that traverses a source folder and copies dataset files to a target destination using `.env` settings. It supports semicolon-separated file lists, automatic filtering for `.data` extensions, optional batch renaming, and per-file overwrite protection with friendly exception handling.

---

## Files

- [dataset_copy.py](file:///home/kafeiaulait/HI-634-Assign_1/dataset_copy.py): Main Python script.
- [.env](file:///home/kafeiaulait/HI-634-Assign_1/.env): Active configuration file.
- [.env.example](file:///home/kafeiaulait/HI-634-Assign_1/.env.example): Template configuration file.

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

1. **Relative Paths**: Automatically resolves paths relative to the script's directory, making it drive-independent (works on `T:`, `C:`, or any other drive/OS).
2. **Semicolon-Separated File List**: Allows specifying multiple files in `SOURCE_FILES` separated by `;`.
3. **`.data` Extension Filter**: Only files ending with `.data` are processed. Files with other extensions (e.g. `heart-disease.names` or `.txt`) are safely skipped with a notice.
4. **Folder Traversal**: Checks direct paths and searches subfolders for any listed files.
5. **Interactive Overwrite Protection**: If a file already exists in the target directory, prompts `Do you want to overwrite it? (Y/N): `.
   - If `N`, raises a `FileExistsError` caught by a `try..except` block with a friendly message, then moves on to the next file without aborting the entire batch.
6. **Optional Batch Renaming**: When `RENAME_FILE=Y`, maps source files to `TARGET_FILES` 1-to-1.
