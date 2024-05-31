""" Generate answernaut embeddings and store them in GCS.
"""
from app.services import create_rag_service
from app.settings import Config

if __name__ == "__main__":
    print("Generating embeddings with:")
    print(f"PROJECT={Config.PROJECT}")
    print(f"BUCKET={Config.BUCKET}")
    rag_svc = create_rag_service()
    print("rag service created")
    rag_svc.generate_embeddings()
