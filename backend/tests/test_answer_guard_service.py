from app.schemas.answer import AnswerCitation
from app.schemas.llm_answer import LlmGroundedAnswer
from app.services.answer_guard_service import (
    apply_answer_guards,
)


def test_insufficient_evidence_clears_citations_and_confidence():
    answer = LlmGroundedAnswer(
        status="insufficient_evidence",
        answer=(
            "Kaynak S1 yüzme havuzunu doğrulamıyor."
        ),
        confidence=0.2,
        citation_ids=["S1"],
        missing_information=[
            "Yüzme havuzu bilgisi bulunamadı."
        ],
        warnings=[],
    )
    citation = AnswerCitation(
        source_id="S1",
        document_id="doc-1",
        original_filename="a.pdf",
        page_number=1,
        document_type="technical_specification",
        similarity=0.85,
        excerpt="İlgisiz kaynak.",
    )

    guarded = apply_answer_guards(
        answer=answer,
        citations=[citation],
    )

    assert guarded.status == "insufficient_evidence"
    assert guarded.confidence == 0.0
    assert guarded.citation_ids == []


def test_conflicting_evidence_adds_version_warning():
    answer = LlmGroundedAnswer(
        status="conflicting_evidence",
        answer="Kaynaklarda 5 ve 8 litre/dakika değerleri var.",
        confidence=0.45,
        citation_ids=["S1", "S2"],
        missing_information=[],
        warnings=[],
    )
    citations = [
        AnswerCitation(
            source_id="S1",
            document_id="doc-1",
            original_filename="a.pdf",
            page_number=1,
            document_type="technical_specification",
            similarity=0.88,
            excerpt="5 litre/dakika",
        ),
        AnswerCitation(
            source_id="S2",
            document_id="doc-2",
            original_filename="b.pdf",
            page_number=1,
            document_type="technical_specification",
            similarity=0.88,
            excerpt="8 litre/dakika",
        ),
    ]

    guarded = apply_answer_guards(
        answer=answer,
        citations=citations,
    )

    assert guarded.status == "conflicting_evidence"
    assert (
        "Belge sürümleri veya geçerlilik tarihleri kontrol edilmelidir."
        in guarded.warnings
    )
