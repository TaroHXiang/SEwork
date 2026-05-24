from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
QDRANT_PATH = BASE_DIR / ".qdrant"

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_COLLECTION = "cell_vectors"
DEFAULT_SAMPLE_DATA = DATA_DIR / "sample_cells.csv"
