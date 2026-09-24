from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"

FAISS_INDEX_DIR = DATA_DIR / "faiss_index"