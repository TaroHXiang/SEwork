from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
DATABASE_URL = os.getenv("DATABASE_URL")
FAISS_SERVICE_URL = os.getenv("FAISS_SERVICE_URL", "http://127.0.0.1:8000")
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
ZHIPU_MODEL = os.getenv("ZHIPU_MODEL", "glm-4-flash-250414")
ZHIPU_API_URL = os.getenv("ZHIPU_API_URL", "https://open.bigmodel.cn/api/paas/v4/chat/completions")
FAISS_INDEX_PATH = Path(
    os.getenv(
        "FAISS_INDEX_PATH",
        os.getenv("VECTOR_INDEX_PATH", os.getenv("QDRANT_PATH", BASE_DIR / ".faiss")),
    )
)
FAISS_DATA_ROOT = Path(os.getenv("FAISS_DATA_ROOT", BASE_DIR))
VECTOR_INDEX_COLLECTION = "cell_vectors"
DEFAULT_SAMPLE_DATA = DATA_DIR / "sample_cells.csv"

QDRANT_PATH = FAISS_INDEX_PATH
QDRANT_URL = None
QDRANT_COLLECTION = VECTOR_INDEX_COLLECTION

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
ADMIN_SETUP_KEY = os.getenv("ADMIN_SETUP_KEY")

API_TOP_K_MAX = int(os.getenv("API_TOP_K_MAX", "10000"))
API_UMAP_LIMIT_MAX = int(os.getenv("API_UMAP_LIMIT_MAX", "100000"))
API_METADATA_VALUES_MAX = int(os.getenv("API_METADATA_VALUES_MAX", "1000"))
MAX_INDEX_BUILD_JOBS = int(os.getenv("MAX_INDEX_BUILD_JOBS", "200"))
