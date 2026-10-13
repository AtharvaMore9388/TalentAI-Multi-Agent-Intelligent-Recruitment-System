"""
TalentAI — RAG Tool
CrewAI-compatible tool for semantic retrieval from ChromaDB.
"""
from __future__ import annotations
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from lib.chroma_store import get_store


class RAGSearchInput(BaseModel):
    query: str = Field(..., description="Job requirements or skill query to search for")
    n_results: int = Field(default=10, description="Number of candidates to retrieve")
    min_experience: float | None = Field(
        default=None, description="Minimum years of experience filter"
    )


class RAGRetrievalTool(BaseTool):
    """
    Retrieves semantically relevant candidates from the ChromaDB vector store
    using Retrieval-Augmented Generation (RAG). Returns ranked candidates
    with similarity scores for downstream matching analysis.
    """

    name: str = "rag_retrieval_tool"
    description: str = (
        "Searches the resume database using semantic similarity. "
        "Input a job requirements query; returns top matching candidates with scores."
    )
    args_schema: type[BaseModel] = RAGSearchInput

    def _run(self, query: str, n_results: int = 10, min_experience: float | None = None) -> str:
        store = get_store()
        if store.count() == 0:
            return "ERROR: No resumes indexed in the database. Please ingest resumes first."

        hits = store.semantic_search(query=query, n_results=n_results, min_experience=min_experience)
        if not hits:
            return "No matching candidates found for the given query."

        lines = [f"Found {len(hits)} candidates:\n"]
        for i, h in enumerate(hits, 1):
            meta = h["metadata"]
            lines.append(
                f"{i}. ID={h['id']} | {meta.get('name')} | "
                f"Similarity={h['similarity']:.3f} | "
                f"Experience={meta.get('experience_years')} yrs | "
                f"Skills: {meta.get('skills', '')[:100]}"
            )
        return "\n".join(lines)
