from app.schemas.answer import AnswerCitation
from app.schemas.llm_answer import (
    LlmGroundedAnswer,
)


def apply_answer_guards(
    *,
    answer: LlmGroundedAnswer,
    citations: list[AnswerCitation],
) -> LlmGroundedAnswer:
    warnings = list(answer.warnings)

    status = answer.status
    confidence = answer.confidence
    answer_text = answer.answer
    citation_ids = [
        citation.source_id
        for citation in citations
    ]

    if status == "insufficient_evidence":
        confidence = 0.0
        citation_ids = []
        answer_text = (
            "Yüklenen proje belgelerinde bu "
            "soruyu yanıtlamak için yeterli "
            "kanıt bulunamadı."
        )

    if status == "conflicting_evidence":
        warnings.append(
            "Belge sürümleri veya geçerlilik tarihleri kontrol edilmelidir."
        )

    if status == "answered" and not citations:
        status = "insufficient_evidence"
        confidence = 0.0
        citation_ids = []

        answer_text = (
            "Getirilen kaynaklar cevabı güvenilir "
            "şekilde desteklemediği için kesin bir "
            "sonuca ulaşılamadı."
        )

        warnings.append(
            "Model cevabı geçerli bir kaynakla "
            "desteklenemedi."
        )

    if citations:
        maximum_similarity = max(
            citation.similarity
            for citation in citations
        )

        if maximum_similarity < 0.45:
            confidence = min(
                confidence,
                0.45,
            )

            warnings.append(
                "Bulunan kaynakların sorguyla "
                "benzerliği sınırlı."
            )

    return LlmGroundedAnswer(
        status=status,
        answer=answer_text,
        confidence=round(confidence, 4),
        citation_ids=citation_ids,
        missing_information=(
            answer.missing_information
        ),
        warnings=list(dict.fromkeys(warnings)),
    )
