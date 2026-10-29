# File Copy Script with .env Configuration

A Python script that copies a file from a source folder to a target folder using settings from a `.env` file, with support for file renaming and overwrite confirmation handling.

---

## Files

- [copy_file.py](file:///home/kafeiaulait/HI-634-Assign_1/copy_file.py): Main Python script.
- [.env](file:///home/kafeiaulait/HI-634-Assign_1/.env): Environment configuration file.
- [.env.example](file:///home/kafeiaulait/HI-634-Assign_1/.env.example): Template for `.env`.

---

## Configuration (`.env`)

```ini
# Source folder (relative or absolute)
SOURCE_FOLDER=source_dir

# Name of the source file
SOURCE_FILE=sample.txt

# Target folder (relative or absolute)
TARGET_FOLDER=target_dir

# Rename flag: Y to rename in target folder, N to keep original name
RENAME_FILE=N

# Target file name (required only if RENAME_FILE=Y)
TARGET_FILE_NAME=renamed_sample.txt
```

---

## How It Works

1. **Loads `.env`**: Uses `python-dotenv` if installed, or automatically falls back to an internal zero-dependency parser.
2. **Validates paths**: Ensures source file exists and creates the target directory if it does not already exist.
3. **Renaming**: If `RENAME_FILE=Y`, copies the file with the name in `TARGET_FILE_NAME`. If `RENAME_FILE=N`, copies with original `SOURCE_FILE` name.
4. **Overwrite Protection**:
   - If the file exists in the target location, it prompts:
     ```text
     File '...' already exists in '...'.
     Do you want to overwrite it? (Y/N):
     ```
   - Answering `N` (or anything other than `Y`) raises a `FileExistsError` inside a `try..except` block and displays a friendly notice without overwriting.
   - Answering `Y` proceeds with the overwrite using `shutil.copy2` (preserving file metadata).

---

## Usage

```bash
python3 copy_file.py
```
