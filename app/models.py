from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator, model_validator

Language = Literal["en", "nb"]
Audience = Literal["student", "teacher"]
ObjectKind = Literal["concept", "exercise", "figure", "resource", "collection"]
Visibility = Literal["private", "teacher", "student", "public"]
ContentStatus = Literal["draft", "review", "approved", "published", "archived"]
ResourceStatus = Literal["candidate", "reviewed", "approved", "published"]
TranslationState = Literal["draft", "missing", "machine_draft", "edited", "approved"]
OutputFormat = Literal["html", "pdf", "revealjs", "handout", "exercise-sheet"]

SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


class AIInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_fields: list[str] = Field(default_factory=list)
    source: str | None = None
    created_on: date | None = None
    review_state: Literal["pending", "approved", "rejected"] | None = None


class ApprovalHistoryEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Literal["reviewed", "approved", "published"]
    by: str = Field(min_length=1)
    acted_on: date


class BaseContentModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(pattern=SLUG_PATTERN)
    kind: ObjectKind
    status: str
    visibility: Visibility
    languages: list[Language]
    title: dict[str, str]
    courses: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    outputs: list[OutputFormat] = Field(default_factory=lambda: ["html"])
    owners: list[str] = Field(default_factory=list)
    updated: date
    translation_status: dict[str, TranslationState] = Field(default_factory=dict)
    ai: AIInfo = Field(default_factory=AIInfo)

    @field_validator("languages")
    @classmethod
    def validate_languages(cls, value: list[Language]) -> list[Language]:
        unique = list(dict.fromkeys(value))
        if not unique:
            raise ValueError("languages must not be empty")
        return unique

    @model_validator(mode="after")
    def validate_localized_fields(self) -> BaseContentModel:
        language_set = set(self.languages)
        title_keys = set(self.title)
        if title_keys != language_set:
            raise ValueError(f"title keys must match languages exactly: {sorted(language_set)}")
        translation_keys = set(self.translation_status)
        if translation_keys != language_set:
            raise ValueError(
                f"translation_status keys must match languages exactly: {sorted(language_set)}"
            )
        return self


class Concept(BaseContentModel):
    kind: Literal["concept"]
    status: ContentStatus
    level: Literal["introductory", "beginner", "intermediate", "advanced"]
    prerequisites: list[str] = Field(default_factory=list)
    related: list[str] = Field(default_factory=list)


class Exercise(BaseContentModel):
    kind: Literal["exercise"]
    status: ContentStatus
    exercise_type: Literal["conceptual", "calculation", "proof", "coding"]
    difficulty: Literal["easy", "medium", "hard"]
    estimated_time_minutes: int = Field(gt=0)
    concepts: list[str] = Field(default_factory=list)
    solution_storage: Literal["separate-file"] = "separate-file"
    solution_visibility: Literal["private", "teacher"] = "teacher"


class Figure(BaseContentModel):
    kind: Literal["figure"]
    status: ContentStatus
    concepts: list[str] = Field(default_factory=list)
    caption: dict[str, str]
    alt_text: dict[str, str]
    svg_path: Literal["figure.svg"] = "figure.svg"
    pdf_path: Literal["figure.pdf"] = "figure.pdf"
    interactive_path: Literal["figure.js"] | None = None
    asset_inventory: list[str] = Field(default_factory=list)

    @field_validator("asset_inventory")
    @classmethod
    def validate_asset_inventory(cls, value: list[str]) -> list[str]:
        unique = list(dict.fromkeys(value))
        for item in unique:
            if not item:
                raise ValueError("asset_inventory entries must not be empty")
            path = Path(item)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("asset_inventory entries must stay inside the figure folder")
        return unique

    @model_validator(mode="after")
    def validate_localized_figure_fields(self) -> Figure:
        language_set = set(self.languages)
        if set(self.caption) != language_set:
            raise ValueError("caption keys must match languages exactly")
        if set(self.alt_text) != language_set:
            raise ValueError("alt_text keys must match languages exactly")
        if self.interactive_path and "html" not in self.outputs:
            raise ValueError("interactive figures must declare html output eligibility")
        required_assets = [self.svg_path, self.pdf_path]
        if self.interactive_path:
            required_assets.append(self.interactive_path)
        self.asset_inventory = list(dict.fromkeys([*required_assets, *self.asset_inventory]))
        return self


class Resource(BaseContentModel):
    kind: Literal["resource"]
    status: ResourceStatus
    resource_kind: Literal["article", "paper", "podcast", "video", "book", "chapter", "website"]
    authors: list[str] = Field(default_factory=list)
    published_on: date
    url: AnyHttpUrl
    difficulty: Literal["introductory", "intermediate", "advanced"]
    estimated_time_minutes: int = Field(gt=0)
    summary: dict[str, str] = Field(default_factory=dict)
    why_selected: dict[str, str] = Field(default_factory=dict)
    instructor_note: dict[str, str] = Field(default_factory=dict)
    freshness: Literal["evergreen", "time-sensitive"]
    review_after: date | None = None
    approved_by: str | None = None
    approved_on: date | None = None
    approval_history: list[ApprovalHistoryEntry] = Field(default_factory=list)
    stale_flag: bool = False

    @model_validator(mode="after")
    def validate_localized_resource_fields(self) -> Resource:
        language_set = set(self.languages)
        if not self.courses and not self.topics:
            raise ValueError("resource must link to at least one course or topic")
        for field_name in ("summary", "why_selected", "instructor_note"):
            value = getattr(self, field_name)
            if value and set(value) != language_set:
                raise ValueError(f"{field_name} keys must match languages exactly")
        if self.freshness == "time-sensitive" and self.review_after is None:
            raise ValueError("time-sensitive resources must declare review_after")
        if self.status in {"candidate", "reviewed"}:
            if self.approved_by or self.approved_on:
                raise ValueError(
                    "candidate/reviewed resources must not declare approved_by or approved_on"
                )
        if self.status in {"approved", "published"}:
            if not self.approved_by or self.approved_on is None:
                raise ValueError(
                    "approved/published resources must declare approved_by and approved_on"
                )
            for field_name in ("summary", "why_selected"):
                value = getattr(self, field_name)
                if set(value) != language_set:
                    raise ValueError(
                        f"approved/published resources require localized {field_name}"
                    )
                if any(not text.strip() for text in value.values()):
                    raise ValueError(
                        f"approved/published resources require non-empty {field_name} values"
                    )
        return self


class Collection(BaseContentModel):
    kind: Literal["collection"]
    status: ContentStatus
    collection_kind: Literal["lecture", "module", "assignment", "reading-list"]
    items: list[str]

    @field_validator("items")
    @classmethod
    def validate_items(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("items must not be empty")
        return value


ContentModel = Concept | Exercise | Figure | Resource | Collection


class CourseDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(pattern=SLUG_PATTERN)
    status: ContentStatus
    visibility: Visibility
    languages: list[Language]
    title: dict[str, str]
    summary: dict[str, str]
    owners: list[str] = Field(default_factory=list)
    updated: date

    @model_validator(mode="after")
    def validate_localized_course_fields(self) -> CourseDefinition:
        language_set = set(self.languages)
        if set(self.title) != language_set:
            raise ValueError("title keys must match languages exactly")
        if set(self.summary) != language_set:
            raise ValueError("summary keys must match languages exactly")
        return self


class CoursePlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lectures: list[str] = Field(default_factory=list)
    assignments: list[str] = Field(default_factory=list)


class RepresentativeTarget(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(pattern=SLUG_PATTERN)
    audience: Audience
    language: Language
    format: OutputFormat
    label: str = Field(min_length=1)


class RepresentativeTargetRegistry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    targets: list[RepresentativeTarget] = Field(default_factory=list)

    @field_validator("targets")
    @classmethod
    def validate_targets(cls, value: list[RepresentativeTarget]) -> list[RepresentativeTarget]:
        if not value:
            raise ValueError("targets must not be empty")
        seen: set[tuple[str, str, str, str]] = set()
        for target in value:
            key = (target.id, target.audience, target.language, target.format)
            if key in seen:
                raise ValueError(f"duplicate representative target: {key}")
            seen.add(key)
        return value
