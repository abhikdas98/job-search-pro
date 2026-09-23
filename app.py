from app.main import load_agenticai_app, seed_rag_database_once

if __name__=="__main__":
    seed_rag_database_once()
    load_agenticai_app()