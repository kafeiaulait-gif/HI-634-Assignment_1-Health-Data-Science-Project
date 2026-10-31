import os
import shutil
import sys
from pathlib import Path


def load_env_file(dotenv_path: Path | str = ".env") -> None:
    """
    Loads variables from a .env file into os.environ.
    Uses python-dotenv if installed, otherwise falls back to a built-in parser.
    """
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path)
    except ImportError:
        env_file = Path(dotenv_path)
        if not env_file.is_file():
            return
        
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    # Strip surrounding single or double quotes
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    os.environ.setdefault(key, value)


def copy_dataset_files():
    """
    Traverses the source folder and copies dataset files specified in .env.
    Filters files requiring a '.data' extension, supports optional renaming,
    and protects against overwrites using interactive confirmation.
    """
    # 1. Locate script directory and load .env
    script_dir = Path(__file__).resolve().parent
    env_file_path = script_dir / ".env"
    load_env_file(env_file_path)

    source_folder_raw = os.getenv("SOURCE_FOLDER")
    target_folder_raw = os.getenv("TARGET_FOLDER")
    # Supports both SOURCE_FILES and SOURCE_FILE
    source_files_raw = os.getenv("SOURCE_FILES") or os.getenv("SOURCE_FILE")
    rename_flag = os.getenv("RENAME_FILE", "N").strip().upper()
    # Supports both TARGET_FILES and TARGET_FILE_NAME
    target_files_raw = os.getenv("TARGET_FILES") or os.getenv("TARGET_FILE_NAME", "").strip()

    # Validate essential environment variables
    missing_vars = []
    if not source_folder_raw:
        missing_vars.append("SOURCE_FOLDER")
    if not target_folder_raw:
        missing_vars.append("TARGET_FOLDER")
    if not source_files_raw:
        missing_vars.append("SOURCE_FILES (or SOURCE_FILE)")

    if missing_vars:
        print(f"[Error] Missing required .env variable(s): {', '.join(missing_vars)}")
        sys.exit(1)

    # 2. Resolve folder paths (relative paths anchored to script_dir)
    source_dir_path = Path(source_folder_raw)
    if not source_dir_path.is_absolute():
        source_dir_path = (script_dir / source_dir_path).resolve()

    target_dir_path = Path(target_folder_raw)
    if not target_dir_path.is_absolute():
        target_dir_path = (script_dir / target_dir_path).resolve()

    if not source_dir_path.is_dir():
        print(f"[Error] Source folder does not exist or is not a directory: {source_dir_path}")
        sys.exit(1)

    # 3. Parse source files list (semicolon-separated or wildcard)
    raw_requested_files = [f.strip() for f in source_files_raw.split(";") if f.strip()]

    # If user specified "*.data" or "*", automatically grab all .data files from source_folder
    if len(raw_requested_files) == 1 and raw_requested_files[0] in ("*", "*.data"):
        valid_requested_files = sorted([
            f.name for f in source_dir_path.glob("*.data") if f.is_file()
        ])
    else:
        # 4. Filter list for files that explicitly end with '.data'
        valid_requested_files = []
        for fname in raw_requested_files:
            if fname.lower().endswith(".data"):
                valid_requested_files.append(fname)
            else:
                print(f"[Notice] Skipping '{fname}': Does not have the required '.data' extension.")

    if not valid_requested_files:
        print("[Error] No files in the list have the required '.data' extension.")
        sys.exit(1)

    # 5. Handle renaming mappings if RENAME_FILE=Y
    should_rename = rename_flag in ("Y", "YES", "TRUE", "1")
    target_rename_map = {}

    if should_rename:
        raw_target_files = [f.strip() for f in target_files_raw.split(";") if f.strip()]
        if len(raw_target_files) != len(valid_requested_files):
            print(
                f"[Error] RENAME_FILE is 'Y', but the number of target filenames ({len(raw_target_files)}) "
                f"does not match the number of valid .data source files ({len(valid_requested_files)})."
            )
            print(f"  Valid source files: {valid_requested_files}")
            print(f"  Provided target names: {raw_target_files}")
            sys.exit(1)
        for src_name, dst_name in zip(valid_requested_files, raw_target_files):
            target_rename_map[src_name] = dst_name
    else:
        for src_name in valid_requested_files:
            target_rename_map[src_name] = src_name

    # 6. Traverse source folder to find the matching files
    # Check direct location first, or recursively find files
    files_to_copy = []
    for filename in valid_requested_files:
        direct_path = source_dir_path / filename
        if direct_path.is_file():
            files_to_copy.append((direct_path, target_rename_map[filename]))
        else:
            # Recursive search in subdirectories if not at the root of source_folder
            matches = list(source_dir_path.rglob(filename))
            if matches:
                files_to_copy.append((matches[0], target_rename_map[filename]))
            else:
                print(f"[Warning] File '{filename}' was not found in '{source_dir_path}'.")

    if not files_to_copy:
        print(f"[Error] None of the specified '.data' files were found in '{source_dir_path}'.")
        sys.exit(1)

    # 7. Ensure target directory exists
    target_dir_path.mkdir(parents=True, exist_ok=True)

    print(f"\nFound {len(files_to_copy)} valid .data file(s) to process.\n")

    copied_count = 0
    skipped_count = 0

    # 8. Process each file inside a try..except block
    for src_file_path, dest_filename in files_to_copy:
        target_file_path = target_dir_path / dest_filename
        print(f"--- Processing: {src_file_path.name} -> {dest_filename} ---")

        try:
            # Check if file exists in target location
            if target_file_path.exists():
                confirm = input(
                    f"File '{dest_filename}' already exists in '{target_folder_raw}'.\n"
                    f"Do you want to overwrite it? (Y/N): "
                ).strip().upper()

                if confirm not in ("Y", "YES"):
                    # Raise FileExistsError when user declines overwrite
                    raise FileExistsError(
                        f"Overwrite cancelled by user for '{dest_filename}'."
                    )

            # Copy file preserving metadata
            shutil.copy2(src_file_path, target_file_path)
            print(f"[Success] Copied '{src_file_path.name}' to '{target_file_path.resolve()}'\n")
            copied_count += 1

        except FileExistsError as err:
            print(f"[Notice] {err}")
            print(f"Skipping '{dest_filename}'. No changes were made.\n")
            skipped_count += 1
        except FileNotFoundError as err:
            print(f"[Error] {err}\n")
            skipped_count += 1
        except PermissionError as err:
            print(f"[Permission Error] Unable to access or write '{dest_filename}': {err}\n")
            skipped_count += 1
        except Exception as err:
            print(f"[Error] An unexpected error occurred while copying '{src_file_path.name}': {err}\n")
            skipped_count += 1

    # Final summary
    print(f"==========================================")
    print(f"Summary: {copied_count} file(s) copied, {skipped_count} skipped.")
    print(f"==========================================")


if __name__ == "__main__":
    copy_dataset_files()
