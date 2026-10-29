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
        # Built-in lightweight .env loader (zero external dependencies required)
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
                    # Strip surrounding single or double quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    os.environ.setdefault(key, value)


def copy_file_with_env_config():
    """
    Copies a file based on .env configuration, handles optional renaming,
    and protects against accidental overwrites with interactive confirmation.
    """
    # 1. Load configuration from .env
    load_env_file(".env")

    source_folder = os.getenv("SOURCE_FOLDER")
    source_file = os.getenv("SOURCE_FILE")
    target_folder = os.getenv("TARGET_FOLDER")
    rename_flag = os.getenv("RENAME_FILE", "N").strip().upper()
    target_file_name = os.getenv("TARGET_FILE_NAME", "").strip()

    # Validate essential environment variables
    missing_vars = []
    if not source_folder:
        missing_vars.append("SOURCE_FOLDER")
    if not source_file:
        missing_vars.append("SOURCE_FILE")
    if not target_folder:
        missing_vars.append("TARGET_FOLDER")

    if missing_vars:
        print(f"[Error] Missing required .env variable(s): {', '.join(missing_vars)}")
        sys.exit(1)

    # Determine destination file name based on rename flag
    should_rename = rename_flag in ("Y", "YES", "TRUE", "1")
    if should_rename:
        if not target_file_name:
            print("[Error] RENAME_FILE is set to 'Y', but TARGET_FILE_NAME is not provided in .env.")
            sys.exit(1)
        dest_filename = target_file_name
    else:
        dest_filename = source_file

    source_path = Path(source_folder) / source_file
    target_dir = Path(target_folder)
    target_path = target_dir / dest_filename

    # 2. Execute copy operation inside a try..except block
    try:
        # Check if source file exists
        if not source_path.is_file():
            raise FileNotFoundError(f"Source file does not exist: {source_path}")

        # Ensure destination directory exists
        target_dir.mkdir(parents=True, exist_ok=True)

        # Check if target file already exists
        if target_path.exists():
            confirm = input(
                f"File '{dest_filename}' already exists in '{target_folder}'.\n"
                f"Do you want to overwrite it? (Y/N): "
            ).strip().upper()

            if confirm not in ("Y", "YES"):
                # Raise an exception when the user chooses not to overwrite
                raise FileExistsError(
                    f"File '{dest_filename}' already exists in target destination. Overwrite cancelled by user."
                )

        # Copy the file (copy2 preserves file metadata such as timestamps)
        shutil.copy2(source_path, target_path)
        print(f"\n[Success] Successfully copied:")
        print(f"  From: {source_path.resolve()}")
        print(f"  To:   {target_path.resolve()}")

    except FileExistsError as err:
        print(f"\n[Notice] {err}")
        print("No changes were made to the target file.")
    except FileNotFoundError as err:
        print(f"\n[Error] {err}")
    except PermissionError as err:
        print(f"\n[Permission Error] Unable to access or write file: {err}")
    except Exception as err:
        print(f"\n[Error] An unexpected error occurred: {err}")


if __name__ == "__main__":
    copy_file_with_env_config()
