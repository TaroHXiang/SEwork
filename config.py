from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
QDRANT_PATH = Path(os.getenv("QDRANT_PATH", BASE_DIR / ".qdrant"))
DATABASE_URL = os.getenv("DATABASE_URL")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_COLLECTION = "cell_vectors"
DEFAULT_SAMPLE_DATA = DATA_DIR / "sample_cells.csv"

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
ADMIN_SETUP_KEY = os.getenv("ADMIN_SETUP_KEY")

API_TOP_K_MAX = int(os.getenv("API_TOP_K_MAX", "100"))
API_UMAP_LIMIT_MAX = int(os.getenv("API_UMAP_LIMIT_MAX", "100000"))
API_METADATA_VALUES_MAX = int(os.getenv("API_METADATA_VALUES_MAX", "1000"))
MAX_INDEX_BUILD_JOBS = int(os.getenv("MAX_INDEX_BUILD_JOBS", "200"))
