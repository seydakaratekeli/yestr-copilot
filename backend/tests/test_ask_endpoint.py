from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.auth import AuthenticatedUser, get_current_user
from app.main import app
from app.services.llm_provider import GroundedAnswer
from app.services.semantic_search_service import (
    RetrievedChunk,
)


FAKE_USER_ID = "user-test-123"
FAKE_PROJECT_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
ENDPOINT = f"/api/projects/{FAKE_PROJECT_ID}/ask"


class _FakeLLMProvider:
    def __init__(self, answer):
        self.answer = answer
        self.calls = []

    def generate_grounded_answer(self, **kwargs):
        self.calls.append(kwargs)
        return self.answer


def _auth_headers():
    return {"Authorization": "Bearer fake-token"}


def _chunk(**overrides):
    data = {
        "id": "chunk-1",
        "document_id": "doc-1",
        "project_id": FAKE_PROJECT_ID,
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


@pytest.fixture
def client():
    async def _override_user():
        return AuthenticatedUser(
            id=FAKE_USER_ID,
            email="test@example.com",
        )

    app.dependency_overrides[get_current_user] = _override_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_current_user, None)


def test_ask_endpoint_returns_grounded_answer_with_sources(client):
    provider = _FakeLLMProvider(
        GroundedAnswer(
            answer=(
                "Belgede lavabo bataryaları için en fazla "
                "5 litre/dakika debi şartı yer alıyor [S1]."
            ),
            source_ids=["S1"],
            answer_status="grounded",
        )
    )

    with (
        patch(
            "app.api.routes.search.get_supabase_admin",
            return_value=MagicMock(),
        ) as get_supabase_admin,
        patch(
            "app.api.routes.search.get_accessible_project",
            return_value={
                "id": FAKE_PROJECT_ID,
                "created_by": FAKE_USER_ID,
            },
        ) as get_accessible_project,
        patch(
            "app.services.rag_service.search_project_chunks",
            return_value=[_chunk()],
        ) as search_project_chunks,
        patch(
            "app.services.rag_service.get_llm_provider",
            return_value=provider,
        ),
    ):
        response = client.post(
            ENDPOINT,
            headers=_auth_headers(),
            json={
                "question": (
                    "Düşük debili armatür kullanılıyor mu?"
                ),
                "limit": 5,
                "minimum_similarity": 0.45,
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["answer_status"] == "grounded"
    assert body["has_sufficient_evidence"] is True
    assert body["sources"][0]["citation"] == "S1"
    assert body["sources"][0]["similarity"] == 0.81
    assert body["sources"][0]["is_ocr"] is False
    assert provider.calls
    assert search_project_chunks.call_args.kwargs["project_id"] == FAKE_PROJECT_ID
    get_supabase_admin.assert_called_once()
    get_accessible_project.assert_called_once()


def test_ask_endpoint_does_not_call_llm_without_sources(client):
    provider = _FakeLLMProvider(
        GroundedAnswer(
            answer="Bu çağrılmamalı [S1].",
            source_ids=["S1"],
            answer_status="grounded",
        )
    )

    with (
        patch(
            "app.api.routes.search.get_supabase_admin",
            return_value=MagicMock(),
        ),
        patch(
            "app.api.routes.search.get_accessible_project",
            return_value={
                "id": FAKE_PROJECT_ID,
                "created_by": FAKE_USER_ID,
            },
        ),
        patch(
            "app.services.rag_service.search_project_chunks",
            return_value=[],
        ),
        patch(
            "app.services.rag_service.get_llm_provider",
            return_value=provider,
        ),
    ):
        response = client.post(
            ENDPOINT,
            headers=_auth_headers(),
            json={
                "question": (
                    "Düşük debili armatür kullanılıyor mu?"
                )
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["answer_status"] == "insufficient_evidence"
    assert body["has_sufficient_evidence"] is False
    assert body["sources"] == []
    assert provider.calls == []
