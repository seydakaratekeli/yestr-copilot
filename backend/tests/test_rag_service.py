from unittest.mock import patch

import pytest

from app.schemas.search import AskProjectSource
from app.services.llm_provider import (
    GroundedAnswer,
    LLMGenerationError,
)
from app.services.rag_context_service import (
    build_rag_sources,
    render_rag_context,
)
from app.services.rag_service import validate_grounded_answer_sources
from app.services.semantic_search_service import (
    RetrievedChunk,
    search_project_chunks,
)


class _ExecuteResponse:
    def __init__(self, data):
        self.data = data


class _RpcRequest:
    def __init__(self, data):
        self._data = data

    def execute(self):
        return _ExecuteResponse(self._data)


class _SupabaseForSearch:
    def __init__(self, *, rpc_data):
        self.rpc_data = rpc_data
        self.rpc_args = None

    def rpc(self, name, args):
        self.rpc_args = (name, args)
        return _RpcRequest(self.rpc_data)


def _chunk(**overrides):
    data = {
        "id": "chunk-1",
        "document_id": "doc-1",
        "project_id": "project-1",
        "page_number": 1,
        "chunk_index": 0,
        "content": (
            "Lavabo bataryalarının maksimum debisi "
            "5 litre/dakika olacaktır."
        ),
        "document_type": "technical_specification",
        "original_filename": "mekanik.pdf",
        "extraction_method": "native_pdf",
        "similarity": 0.81,
    }
    data.update(overrides)
    return RetrievedChunk(**data)


def test_search_project_chunks_calls_project_scoped_rpc():
    supabase = _SupabaseForSearch(
        rpc_data=[
            {
                "id": "chunk-1",
                "document_id": "doc-1",
                "project_id": "project-1",
                "page_number": 1,
                "chunk_index": 0,
                "content": "Doğru proje chunk.",
                "document_type": "other",
                "original_filename": "a.pdf",
                "extraction_method": "native_pdf",
                "similarity": 0.91,
            },
        ],
    )

    with patch(
        "app.services.semantic_search_service.generate_query_embedding",
        return_value=[0.0] * 384,
    ):
        results = search_project_chunks(
            supabase=supabase,
            project_id="project-1",
            query="armatür",
            limit=5,
            minimum_similarity=0.45,
        )

    assert [result.id for result in results] == ["chunk-1"]
    assert supabase.rpc_args[0] == "match_project_chunks"
    assert (
        supabase.rpc_args[1]["target_project_id"]
        == "project-1"
    )


def test_build_rag_sources_marks_ocr_and_renders_source_id():
    sources = build_rag_sources(
        [
            _chunk(
                id="chunk-ocr",
                extraction_method="ocr",
            )
        ],
        max_total_characters=500,
    )

    assert sources[0].source_id == "S1"
    assert sources[0].extraction_method == "ocr"
    assert "5 litre/dakika" in sources[0].content

    rendered = render_rag_context(sources)
    assert "[SOURCE_ID: S1]" in rendered
    assert "PAGE: 1" in rendered


def test_validate_answer_citations_rejects_unknown_citation():
    sources = [
        AskProjectSource(
            citation="S1",
            chunk_id="chunk-1",
            document_id="doc-1",
            original_filename="a.pdf",
            page_number=1,
            quote="Kanıt.",
            similarity=0.8,
            extraction_method="native_pdf",
            is_ocr=False,
        )
    ]

    with pytest.raises(
        LLMGenerationError,
        match="gecersiz kaynak",
    ):
        validate_grounded_answer_sources(
            grounded_answer=GroundedAnswer(
                answer="Bu cevap destekleniyor [S2].",
                source_ids=["S2"],
                answer_status="grounded",
            ),
            sources=sources,
        )


def test_validate_grounded_answer_rejects_mismatched_markers():
    sources = [
        AskProjectSource(
            citation="S1",
            chunk_id="chunk-1",
            document_id="doc-1",
            original_filename="a.pdf",
            page_number=1,
            quote="Kanıt.",
            similarity=0.8,
            extraction_method="native_pdf",
            is_ocr=False,
        ),
        AskProjectSource(
            citation="S2",
            chunk_id="chunk-2",
            document_id="doc-1",
            original_filename="a.pdf",
            page_number=2,
            quote="Ek kanıt.",
            similarity=0.7,
            extraction_method="native_pdf",
            is_ocr=False,
        ),
    ]

    with pytest.raises(
        LLMGenerationError,
        match="eslesmiyor",
    ):
        validate_grounded_answer_sources(
            grounded_answer=GroundedAnswer(
                answer="Bu cevap destekleniyor [S1].",
                source_ids=["S1", "S2"],
                answer_status="grounded",
            ),
            sources=sources,
        )
