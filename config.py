from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
QDRANT_PATH = BASE_DIR / ".qdrant"
USER_DB_PATH = Path(os.getenv("USER_DB_PATH", DATA_DIR / "users.db"))

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_COLLECTION = "cell_vectors"
DEFAULT_SAMPLE_DATA = DATA_DIR / "sample_cells.csv"

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
ADMIN_SETUP_KEY = os.getenv("ADMIN_SETUP_KEY")
