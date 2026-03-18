from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from app.config import REPO_ROOT
from app.indexer import IndexedObject, RepositoryIndex, load_repository, load_yaml
from app.models import Resource

RESOURCE_INBOX_TARGET_ID = "resource-inbox"
STALE_RESOURCES_REPORT_PATH = Path("build/reports/stale-resources.json")

RESOURCE_STATE_TRANSITIONS: dict[str, set[str]] = {
    "candidate": {"reviewed"},
    "reviewed": {"approved"},
    "approved": {"published"},
    "published": set(),
}


@dataclass(slots=True)
class ResourceVisibilityDecision:
    resource_id: str
    state: str
    stale: bool
    visible_to_student: bool
    reasons: list[str]


def resource_is_stale(model: Resource, *, today: date | None = None) -> bool:
    reference_date = today or date.today()
    if model.stale_flag:
        return True
    if model.review_after is None:
        return False
    return model.review_after <= reference_date


def resource_student_visibility_decision(
    record: IndexedObject,
    *,
    language: str,
    require_output_format: str | None = None,
    today: date | None = None,
) -> ResourceVisibilityDecision:
    if not isinstance(record.model, Resource):
        raise TypeError(f"{record.model.id} is not a resource")

    model = record.model
    reasons: list[str] = []
    stale = resource_is_stale(model, today=today)

    if model.visibility in {"private", "teacher"}:
        reasons.append(f"visibility-{model.visibility}")
    if model.status not in {"approved", "published"}:
        reasons.append(f"state-{model.status}")
    if language not in model.languages:
        reasons.append(f"missing-language-{language}")
    elif model.translation_status.get(language) != "approved":
        reasons.append(f"translation-not-approved-{language}")
    if require_output_format and require_output_format not in model.outputs:
        reasons.append(f"missing-output-{require_output_format}")
    if model.status in {"approved", "published"} and (
        not model.approved_by or not model.approved_on
    ):
        reasons.append("missing-approval-metadata")
    if stale:
        reasons.append("stale-review")

    return ResourceVisibilityDecision(
        resource_id=model.id,
        state=model.status,
        stale=stale,
        visible_to_student=not reasons,
        reasons=reasons,
    )


def build_resource_workflow_summary(
    index: RepositoryIndex,
    *,
    language: str = "en",
    today: date | None = None,
) -> dict[str, object]:
    resources = [
        record
        for record in sorted(index.objects.values(), key=lambda item: item.model.id)
        if isinstance(record.model, Resource)
    ]
    status_counts = {
        status: 0 for status in ("candidate", "reviewed", "approved", "published")
    }
    approval_metadata_failures: list[str] = []
    stale_resources: list[dict[str, object]] = []
    unpublished_candidates: list[str] = []
    student_exclusions: list[dict[str, object]] = []
    student_visible_resources: list[str] = []

    for record in resources:
        model = record.model
        status_counts[model.status] = status_counts.get(model.status, 0) + 1
        decision = resource_student_visibility_decision(
            record,
            language=language,
            require_output_format="html",
            today=today,
        )
        if model.status == "candidate":
            unpublished_candidates.append(model.id)
        if model.status in {"approved", "published"} and (
            not model.approved_by or not model.approved_on
        ):
            approval_metadata_failures.append(model.id)
        if decision.stale:
            stale_resources.append(
                {
                    "id": model.id,
                    "status": model.status,
                    "review_after": model.review_after.isoformat()
                    if model.review_after is not None
                    else None,
                    "stale_flag": model.stale_flag,
                    "courses": model.courses,
                    "topics": model.topics,
                }
            )
        if decision.visible_to_student:
            student_visible_resources.append(model.id)
        elif model.visibility in {"student", "public"}:
            student_exclusions.append(
                {
                    "id": model.id,
                    "status": model.status,
                    "reasons": decision.reasons,
                }
            )

    return {
        "language": language,
        "status_counts": status_counts,
        "resource_count": len(resources),
        "approval_metadata_failure_count": len(approval_metadata_failures),
        "approval_metadata_failures": approval_metadata_failures,
        "stale_resource_count": len(stale_resources),
        "stale_resources": stale_resources,
        "unpublished_candidate_count": len(unpublished_candidates),
        "unpublished_candidate_ids": unpublished_candidates,
        "student_visible_resource_count": len(student_visible_resources),
        "student_visible_resource_ids": student_visible_resources,
        "student_exclusion_count": len(student_exclusions),
        "student_exclusions": student_exclusions,
    }


def stale_resource_payload(
    index: RepositoryIndex,
    *,
    today: date | None = None,
) -> dict[str, object]:
    reference_date = today or date.today()
    resources = [
        record
        for record in sorted(index.objects.values(), key=lambda item: item.model.id)
        if isinstance(record.model, Resource)
    ]
    stale_entries: list[dict[str, object]] = []

    for record in resources:
        model = record.model
        if not resource_is_stale(model, today=reference_date):
            continue
        stale_entries.append(
            {
                "id": model.id,
                "status": model.status,
                "title": model.title,
                "review_after": model.review_after.isoformat()
                if model.review_after is not None
                else None,
                "stale_flag": model.stale_flag,
                "courses": model.courses,
                "topics": model.topics,
                "approved_by": model.approved_by,
                "approved_on": model.approved_on.isoformat()
                if model.approved_on is not None
                else None,
            }
        )

    return {
        "generated_on": reference_date.isoformat(),
        "resource_count": len(resources),
        "stale_resource_count": len(stale_entries),
        "stale_resources": stale_entries,
    }


def write_stale_resource_report(
    root: Path = REPO_ROOT,
    *,
    today: date | None = None,
) -> tuple[Path, dict[str, object]]:
    index, errors = load_repository(root, collect_errors=False)
    if errors:
        raise ValueError("repository contains load errors")
    payload = stale_resource_payload(index, today=today)
    output_path = root / STALE_RESOURCES_REPORT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path, payload


def transition_resource_to_state(
    resource_id: str,
    *,
    target_state: str,
    actor: str,
    acted_on: date,
    root: Path = REPO_ROOT,
) -> tuple[Path, Resource]:
    index, errors = load_repository(root, collect_errors=False)
    if errors:
        raise ValueError("repository contains load errors")

    record = index.objects.get(resource_id)
    if record is None or not isinstance(record.model, Resource):
        raise ValueError(f"unknown resource id: {resource_id}")

    current_state = record.model.status
    if current_state == target_state:
        return record.meta_path, record.model

    allowed_targets = RESOURCE_STATE_TRANSITIONS.get(current_state, set())
    if target_state not in allowed_targets:
        allowed = ", ".join(sorted(allowed_targets)) or "no further transitions"
        raise ValueError(
            f"invalid resource transition {current_state} -> {target_state}; allowed: {allowed}"
        )

    payload = load_yaml(record.meta_path)
    payload["status"] = target_state
    payload["approved_by"] = actor if target_state in {"approved", "published"} else None
    payload["approved_on"] = (
        acted_on.isoformat() if target_state in {"approved", "published"} else None
    )
    approval_history = list(payload.get("approval_history") or [])
    approval_history.append(
        {
            "action": target_state,
            "by": actor,
            "acted_on": acted_on.isoformat(),
        }
    )
    payload["approval_history"] = approval_history

    validated = Resource.model_validate(payload)
    record.meta_path.write_text(
        yaml.safe_dump(
            validated.model_dump(mode="json", exclude_none=True),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return record.meta_path, validated


def resource_visibility_manifest_entry(
    record: IndexedObject,
    *,
    language: str,
    require_output_format: str | None = "html",
    today: date | None = None,
) -> dict[str, Any]:
    if not isinstance(record.model, Resource):
        raise TypeError(f"{record.model.id} is not a resource")
    decision = resource_student_visibility_decision(
        record,
        language=language,
        require_output_format=require_output_format,
        today=today,
    )
    return {
        **asdict(decision),
        "review_after": record.model.review_after.isoformat()
        if record.model.review_after is not None
        else None,
    }
