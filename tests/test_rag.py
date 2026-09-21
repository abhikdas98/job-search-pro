import pathlib
from app.rag.loader import DocumentLoader
from app.rag.splitter import DocumentSplitter
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStoreService
from app.rag.retriever import RAGRetrieverService

# 1. Paths configuration
TEST_DIR = pathlib.Path(__file__).resolve().parent / "data" / "knowledge_base"
TEST_INDEX_PATH = pathlib.Path(__file__).resolve().parent / "data" / "faiss_index"

TEST_DIR.mkdir(parents=True, exist_ok=True)

#  FIX: Auto-generate a dummy test file to ensure chunks are never empty!
mock_file = TEST_DIR / "sample_resume.md"
if not mock_file.exists():
    mock_file.write_text(
        "# John Doe Profile\n"
        "Skills: Python, FastAPI, LangGraph, SQLite.\n"
        "Experience: 3 years building AI Job Search Agents."
    )
    print(f"📝 Created a dummy test file at: {mock_file}")

# 2. Extract and chunk data elements
loader_service = DocumentLoader(TEST_DIR)
docs = loader_service.load_all_documents()

splitter_service = DocumentSplitter()
chunks = splitter_service.split_documents(docs)

# 3. Handle embeddings model loading
embeds = EmbeddingService.get_embedding_model("huggingface")

# 4. FIXED: Instantiate the class itself first, do NOT chain methods on this line!
db_service = VectorStoreService(index_dir=TEST_INDEX_PATH, embedding_model=embeds)

# 5. Build or update your local index from the loaded chunks
db_service.build_or_update_index(chunks)

# 6. Load the active index back into memory safely
db_instance = db_service.load_index()

print("🚀 Success! FAISS Index compiled and loaded without errors.")

# 🔍 NEW: TEST RETRIEVAL LIFECYCLE 
# ────────────────────────────────────────────────────────
print("\n🔎 Starting Retrieval Test Module...")

# 2. Initialize the retriever service using the loaded index instance
retriever = RAGRetrieverService(db_instance)

# 3. Define a sample query similar to a job description specification
test_query = "Looking for an engineer with LangGraph and Python experience"

# 4. Fetch the matched context block as a clean string format
retrieved_context = retriever.retrieve_as_formatted_string(test_query, top_k=1)

print("\n--- RETRIEVED CONTEXT RESULTS ---")
print(retrieved_context)
print("---------------------------------")

# Simple sanity assertion verification test check
if "John Doe" in retrieved_context:
    print("✅ Retrieval match verification PASSED! Semantically matched the correct document.")
else:
    print("❌ Retrieval match FAILED! Could not isolate relevant semantic chunks.")
