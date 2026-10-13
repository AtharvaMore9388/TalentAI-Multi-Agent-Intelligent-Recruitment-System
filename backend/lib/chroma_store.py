"""
TalentAI — ChromaDB Vector Store Manager
Handles embedding, indexing, and semantic retrieval of resumes.
"""
from __future__ import annotations
import os
import uuid
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from lib.models import Candidate


# Lazy-loaded embedding model (loaded once, reused)
_embedding_model: SentenceTransformer | None = None


def _get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


def _embed(texts: list[str]) -> list[list[float]]:
    model = _get_embedding_model()
    return model.encode(texts, convert_to_numpy=True).tolist()


class ChromaStore:
    """Wrapper around ChromaDB for semantic resume and job storage."""

    def __init__(self, persist_dir: str = "./chroma_store"):
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False),
        )
        self.resume_collection = self.client.get_or_create_collection(
            name=os.getenv("CHROMA_COLLECTION_RESUMES", "talent_resumes"),
            metadata={"hnsw:space": "cosine"},
        )

    # ─── Resume CRUD ────────────────────────────────────────────────────────

    def add_resume(self, candidate: Candidate) -> None:
        """Embed and store a candidate resume."""
        text = self._candidate_to_text(candidate)
        embedding = _embed([text])[0]
        self.resume_collection.upsert(
            ids=[candidate.id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                "name": candidate.name,
                "email": candidate.email,
                "experience_years": candidate.experience_years,
                "skills": ", ".join(candidate.skills),
                "education": candidate.education,
            }],
        )

    def add_resumes_batch(self, candidates: list[Candidate]) -> None:
        """Batch-embed and store multiple resumes."""
        ids, embeddings, documents, metadatas = [], [], [], []
        texts = [self._candidate_to_text(c) for c in candidates]
        embs = _embed(texts)
        for c, emb, text in zip(candidates, embs, texts):
            ids.append(c.id)
            embeddings.append(emb)
            documents.append(text)
            metadatas.append({
                "name": c.name,
                "email": c.email,
                "experience_years": c.experience_years,
                "skills": ", ".join(c.skills),
                "education": c.education,
            })
        self.resume_collection.upsert(
            ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
        )

    def semantic_search(
        self,
        query: str,
        n_results: int = 10,
        min_experience: float | None = None,
    ) -> list[dict]:
        """Retrieve top-n semantically similar candidates."""
        query_embedding = _embed([query])[0]
        where = {}
        if min_experience is not None:
            where = {"experience_years": {"$gte": min_experience}}

        results = self.resume_collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, self.resume_collection.count() or 1),
            include=["documents", "metadatas", "distances"],
            where=where if where else None,
        )
        hits = []
        if results and results["ids"]:
            for i, cid in enumerate(results["ids"][0]):
                hits.append({
                    "id": cid,
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "similarity": round(1 - results["distances"][0][i], 4),
                })
        return hits

    def count(self) -> int:
        return self.resume_collection.count()

    def clear(self) -> None:
        """Clear all stored resumes (useful for tests)."""
        self.client.delete_collection(
            os.getenv("CHROMA_COLLECTION_RESUMES", "talent_resumes")
        )
        self.resume_collection = self.client.get_or_create_collection(
            name=os.getenv("CHROMA_COLLECTION_RESUMES", "talent_resumes"),
            metadata={"hnsw:space": "cosine"},
        )

    # ─── Helpers ────────────────────────────────────────────────────────────

    @staticmethod
    def _candidate_to_text(c: Candidate) -> str:
        return (
            f"Name: {c.name}\n"
            f"Summary: {c.summary}\n"
            f"Skills: {', '.join(c.skills)}\n"
            f"Experience: {c.experience_years} years\n"
            f"Education: {c.education}\n"
            f"Resume: {c.raw_resume}"
        )


# Singleton instance
_store: ChromaStore | None = None


def get_store(persist_dir: str | None = None) -> ChromaStore:
    global _store
    if _store is None:
        _store = ChromaStore(
            persist_dir=persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./chroma_store")
        )
    return _store
