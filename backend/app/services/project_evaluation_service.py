from copy import deepcopy
from typing import Any

from app.core.config import settings
from app.core.supabase import get_supabase_admin
from app.services.criterion_citation_service import (
    build_criterion_citations,
)
from app.services.criterion_evidence_service import (
    CriterionEvidenceError,
    extract_criterion_evidence,
)
from app.services.evaluation_repository import (
    complete_evaluation,
    delete_previous_results,
    fail_evaluation,
    get_evaluation,
    get_published_criteria_with_rules,
    insert_criterion_result,
    mark_evaluation_processing,
)
from app.services.extracted_value_service import (
    normalize_extracted_values,
)
from app.services.rag_context_service import (
    build_rag_sources,
)
from app.services.rule_engine import (
    RuleEvaluationError,
    evaluate_rule,
)
from app.services.semantic_search_service import (
    search_project_chunks,
)


def process_project_evaluation(
    *,
    evaluation_id: str,
) -> None:
    supabase = get_supabase_admin()

    try:
        evaluation = get_evaluation(
            supabase=supabase,
            evaluation_id=evaluation_id,
        )

        mark_evaluation_processing(
            supabase=supabase,
            evaluation_id=evaluation_id,
        )

        delete_previous_results(
            supabase=supabase,
            evaluation_id=evaluation_id,
        )

        criterion_entries = (
            get_published_criteria_with_rules(
                supabase=supabase,
                criterion_set_id=(
                    evaluation["criterion_set_id"]
                ),
            )
        )

        if not criterion_entries:
            raise RuntimeError(
                "Kriter setinde yayınlanmış kriter bulunamadı."
            )

        total_score = 0.0
        maximum_score = 0.0

        satisfied_count = 0
        not_satisfied_count = 0
        uncertain_count = 0
        manual_review_count = 0

        for entry in criterion_entries:
            criterion = entry["criterion"]
            rule = entry["rule"]

            result = _evaluate_single_criterion(
                supabase=supabase,
                evaluation=evaluation,
                criterion=criterion,
                rule=rule,
            )

            insert_criterion_result(
                supabase=supabase,
                payload=result,
            )

            awarded_score = float(
                result["awarded_score"]
            )

            criterion_maximum = float(
                result["maximum_score"]
            )

            total_score += awarded_score
            maximum_score += criterion_maximum

            match result["result_status"]:
                case "satisfied":
                    satisfied_count += 1

                case "not_satisfied":
                    not_satisfied_count += 1

                case "manual_review":
                    manual_review_count += 1

                case _:
                    uncertain_count += 1

        score_percentage = (
            round(
                total_score
                / maximum_score
                * 100,
                2,
            )
            if maximum_score > 0
            else 0.0
        )

        complete_evaluation(
            supabase=supabase,
            evaluation_id=evaluation_id,
            totals={
                "total_score": round(
                    total_score,
                    2,
                ),
                "maximum_score": round(
                    maximum_score,
                    2,
                ),
                "score_percentage": (
                    score_percentage
                ),
                "satisfied_count": (
                    satisfied_count
                ),
                "not_satisfied_count": (
                    not_satisfied_count
                ),
                "uncertain_count": (
                    uncertain_count
                ),
                "manual_review_count": (
                    manual_review_count
                ),
            },
        )

    except Exception as exc:
        fail_evaluation(
            supabase=supabase,
            evaluation_id=evaluation_id,
            message=str(exc),
        )

        print(
            "Project evaluation failed:",
            evaluation_id,
            repr(exc),
        )


def _evaluate_single_criterion(
    *,
    supabase,
    evaluation: dict[str, Any],
    criterion: dict[str, Any],
    rule: dict[str, Any] | None,
) -> dict[str, Any]:
    maximum_score = float(
        criterion["maximum_score"]
    )

    base_payload: dict[str, Any] = {
        "evaluation_id": evaluation["id"],
        "project_id": evaluation["project_id"],
        "criterion_id": criterion["id"],
        "rule_id": (
            rule["id"] if rule else None
        ),
        "maximum_score": maximum_score,
    }

    if rule is None:
        return {
            **base_payload,
            "result_status": "manual_review",
            "awarded_score": 0,
            "extracted_values": {},
            "citations": [],
            "evidence_summary": (
                "Kriter için yayınlanmış bir "
                "makine kuralı bulunmuyor."
            ),
            "missing_information": [],
            "warnings": [
                (
                    "Kriter uzman tarafından "
                    "manuel incelenmelidir."
                )
            ],
            "confidence": 0,
            "requires_manual_review": True,
            "rule_snapshot": {},
        }

    search_query = (
        criterion.get("evaluation_prompt")
        or criterion["title"]
    )

    chunks = search_project_chunks(
        supabase=supabase,
        project_id=evaluation["project_id"],
        query=search_query,
        limit=settings.rag_search_limit,
        minimum_similarity=(
            settings.rag_minimum_similarity
        ),
    )

    chunks = _filter_document_types(
        chunks=chunks,
        required_document_types=(
            criterion.get(
                "required_document_types"
            )
            or []
        ),
    )

    sources = build_rag_sources(
        chunks,
        max_total_characters=(
            settings.rag_max_context_characters
        ),
    )

    try:
        evidence = extract_criterion_evidence(
            criterion=criterion,
            rule=rule,
            sources=sources,
        )

        citations = build_criterion_citations(
            citation_ids=evidence.citation_ids,
            sources=sources,
        )

        normalized_values = (
            normalize_extracted_values(
                rule_config=rule["rule_config"],
                extracted_values=(
                    evidence.extracted_values
                ),
            )
        )

        rule_result = evaluate_rule(
            rule_type=rule["rule_type"],
            rule_config=rule["rule_config"],
            extracted_values=normalized_values,
            maximum_score=maximum_score,
            evidence_status=(
                evidence.evidence_status
            ),
        )

        confidence = _calculate_confidence(
            evidence_confidence=(
                evidence.confidence
            ),
            citations=citations,
            evidence_status=(
                evidence.evidence_status
            ),
        )

        warnings = list(
            dict.fromkeys(
                [
                    *evidence.warnings,
                    *rule_result.warnings,
                ]
            )
        )

        return {
            **base_payload,
            "result_status": (
                rule_result.status
            ),
            "awarded_score": (
                rule_result.awarded_score
            ),
            "extracted_values": normalized_values,
            "citations": citations,
            "evidence_summary": (
                evidence.evidence_summary
            ),
            "missing_information": (
                evidence.missing_information
            ),
            "warnings": warnings,
            "confidence": confidence,
            "requires_manual_review": (
                rule_result
                .requires_manual_review
            ),
            "rule_snapshot": deepcopy(rule),
        }

    except (
        CriterionEvidenceError,
        RuleEvaluationError,
    ) as exc:
        return {
            **base_payload,
            "result_status": "failed",
            "awarded_score": 0,
            "extracted_values": {},
            "citations": [],
            "evidence_summary": (
                "Kriter otomatik olarak "
                "değerlendirilemedi."
            ),
            "missing_information": [],
            "warnings": [
                str(exc),
            ],
            "confidence": 0,
            "requires_manual_review": True,
            "rule_snapshot": deepcopy(rule),
        }


def _filter_document_types(
    *,
    chunks: list,
    required_document_types: list[str],
) -> list:
    if not required_document_types:
        return chunks

    filtered = [
        chunk
        for chunk in chunks
        if chunk.document_type
        in required_document_types
    ]

    # Katı filtre hiçbir şey döndürmezse tüm semantik
    # sonuçları yok saymak yerine mevcut sonuçları koruyoruz.
    # Ancak aşağıda uyarı eklemek üzere ileride bu davranış
    # daha ayrıntılı hâle getirilebilir.
    return filtered or chunks


def _calculate_confidence(
    *,
    evidence_confidence: float,
    citations: list[dict[str, Any]],
    evidence_status: str,
) -> float:
    if not citations:
        return 0.0

    maximum_similarity = max(
        float(citation["similarity"])
        for citation in citations
    )

    extraction_quality = min(
        1.0,
        max(
            0.0,
            evidence_confidence,
        ),
    )

    status_factor = {
        "found": 1.0,
        "conflicting": 0.55,
        "ambiguous": 0.40,
        "not_found": 0.0,
    }.get(
        evidence_status,
        0.0,
    )

    confidence = (
        0.55 * maximum_similarity
        + 0.30 * extraction_quality
        + 0.15 * status_factor
    )

    return round(
        min(1.0, max(0.0, confidence)),
        4,
    )
