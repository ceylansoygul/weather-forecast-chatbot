"""Load project configuration from environment variables."""

from pathlib import Path

from dotenv import load_dotenv


def load_project_environment():
    """Load the first project-level `.env` file found in the parent path.

    Returns:
        Path | None: The path to the loaded file, or None if no file exists.
    """
    project_root = Path(__file__).resolve().parents[1]

    for folder in [project_root, *project_root.parents]:
        env_file = folder / ".env"

        if env_file.exists():
            load_dotenv(env_file, override=False)
            return env_file

    return None
