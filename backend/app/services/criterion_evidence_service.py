import json
from typing import Any

from pydantic import ValidationError

from app.core.config import settings
from app.core.openai_client import get_openai_client
from app.prompts.criterion_evidence import (
    CRITERION_EVIDENCE_INSTRUCTIONS,
)
from app.schemas.criterion_evidence import (
    CriterionEvidenceExtraction,
)
from app.services.rag_context_service import (
    RagSource,
    render_rag_context,
)
from app.services.retry_service import (
    retry_transient,
)


class CriterionEvidenceError(RuntimeError):
    pass


def extract_criterion_evidence(
    *,
    criterion: dict[str, Any],
    rule: dict[str, Any],
    sources: list[RagSource],
) -> CriterionEvidenceExtraction:
    if not sources:
        return CriterionEvidenceExtraction(
            evidence_status="not_found",
            extracted_values={},
            evidence_summary=(
                "Yüklenen proje belgelerinde kriteri "
                "değerlendirecek yeterli kanıt bulunamadı."
            ),
            citation_ids=[],
            missing_information=[
                (
                    "Kriterle ilişkili açık teknik bilgi "
                    "veya belge kanıtı bulunamadı."
                )
            ],
            warnings=[],
            confidence=0.0,
        )

    rule_config = rule.get("rule_config") or {}

    expected_field = str(
        rule_config.get("field", "")
    ).strip()
    unit_field = str(
        rule_config.get("unit_field", "")
    ).strip()
    extracted_values_schema = (
        _build_extracted_values_schema(
            expected_field=expected_field,
            rule_type=rule["rule_type"],
            unit_field=unit_field,
        )
    )

    rag_context = render_rag_context(sources)

    input_text = f"""
KRİTER KODU:
{criterion["code"]}

KRİTER BAŞLIĞI:
{criterion["title"]}

KRİTER AÇIKLAMASI:
{criterion.get("description") or "Açıklama yok."}

KANIT ARAMA TALİMATI:
{criterion.get("evaluation_prompt") or criterion["title"]}

ÇIKARILMASI BEKLENEN ALAN:
{expected_field or "Belirli alan tanımlanmamış."}

KURAL TÜRÜ:
{rule["rule_type"]}

KURAL YAPILANDIRMASI:
{json.dumps(rule_config, ensure_ascii=False)}

PROJE BELGE KAYNAKLARI:
{rag_context}

Yalnızca sağlanan kaynaklardan kriter kanıtını çıkar.
Puan veya sertifikasyon kararı üretme.
"""

    client = get_openai_client()

    try:
        response = retry_transient(
            lambda: client.responses.create(
                model=settings.llm_model,
                instructions=(
                    CRITERION_EVIDENCE_INSTRUCTIONS
                ),
                input=input_text,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "criterion_evidence",
                        "strict": True,
                        "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "evidence_status": {
                                "type": "string",
                                "enum": [
                                    "found",
                                    "not_found",
                                    "conflicting",
                                    "ambiguous",
                                ],
                            },
                            "extracted_values": (
                                extracted_values_schema
                            ),
                            "evidence_summary": {
                                "type": "string",
                            },
                            "citation_ids": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                },
                            },
                            "missing_information": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                },
                            },
                            "warnings": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                },
                            },
                            "confidence": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                        },
                        "required": [
                            "evidence_status",
                            "extracted_values",
                            "evidence_summary",
                            "citation_ids",
                            "missing_information",
                            "warnings",
                            "confidence",
                        ],
                        },
                    }
                },
                store=False,
            ),
            operation_name="LLM kriter kanıtı çıkarımı",
        )

        parsed = json.loads(response.output_text)

        extraction = (
            CriterionEvidenceExtraction
            .model_validate(parsed)
        )

    except (
        json.JSONDecodeError,
        ValidationError,
    ) as exc:
        raise CriterionEvidenceError(
            "LLM geçerli kriter kanıtı formatı döndürmedi."
        ) from exc

    except Exception as exc:
        raise CriterionEvidenceError(
            "Kriter kanıtı çıkarılamadı."
        ) from exc

    return _sanitize_extraction(
        extraction=extraction,
        sources=sources,
        expected_field=expected_field,
        unit_field=unit_field,
    )


def _build_extracted_values_schema(
    *,
    expected_field: str,
    rule_type: str,
    unit_field: str = "",
) -> dict[str, Any]:
    properties: dict[str, Any] = {}
    required: list[str] = []

    if expected_field:
        properties[expected_field] = {
            "type": _get_expected_value_types(
                rule_type
            ),
        }
        required.append(expected_field)

    if unit_field:
        properties[unit_field] = {
            "type": ["string", "null"],
        }
        required.append(unit_field)

    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": required,
    }


def _get_expected_value_types(
    rule_type: str,
) -> list[str]:
    if rule_type in {
        "numeric_threshold",
        "percentage_threshold",
        "numeric_range",
    }:
        return ["number", "null"]

    if rule_type == "boolean_value":
        return ["boolean", "null"]

    return [
        "string",
        "number",
        "boolean",
        "null",
    ]


def _sanitize_extraction(
    *,
    extraction: CriterionEvidenceExtraction,
    sources: list[RagSource],
    expected_field: str,
    unit_field: str = "",
) -> CriterionEvidenceExtraction:
    valid_source_ids = {
        source.source_id
        for source in sources
    }

    valid_citation_ids = list(
        dict.fromkeys(
            source_id
            for source_id in extraction.citation_ids
            if source_id in valid_source_ids
        )
    )

    extracted_values = dict(
        extraction.extracted_values
    )

    # Yalnızca kuralın beklediği değer ve birim
    # alanlarını değerlendirmeye sokuyoruz.
    expected_fields = [
        field
        for field in (
            expected_field,
            unit_field,
        )
        if field
    ]

    if expected_fields:
        extracted_values = {
            field: extracted_values.get(field)
            for field in expected_fields
        }

    evidence_status = extraction.evidence_status
    confidence = extraction.confidence
    warnings = list(extraction.warnings)

    if evidence_status == "found" and not valid_citation_ids:
        evidence_status = "ambiguous"
        confidence = min(confidence, 0.30)

        warnings.append(
            "Bulunan değer geçerli bir belge kaynağıyla "
            "doğrulanamadı."
        )

    if (
        evidence_status == "found"
        and expected_field
        and extracted_values.get(expected_field) is None
    ):
        evidence_status = "ambiguous"
        confidence = min(confidence, 0.35)

        warnings.append(
            f"Beklenen '{expected_field}' alanı "
            "kaynaklardan çıkarılamadı."
        )

    return CriterionEvidenceExtraction(
        evidence_status=evidence_status,
        extracted_values=extracted_values,
        evidence_summary=(
            extraction.evidence_summary
        ),
        citation_ids=valid_citation_ids,
        missing_information=(
            extraction.missing_information
        ),
        warnings=list(
            dict.fromkeys(warnings)
        ),
        confidence=round(confidence, 4),
    )
