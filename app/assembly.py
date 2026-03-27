from __future__ import annotations

import hashlib
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import date
from html import escape
from pathlib import Path

import yaml

from app.config import REPO_ROOT, exports_dir, generated_dir
from app.indexer import IndexedCourse, IndexedObject, RepositoryIndex
from app.models import Collection, Exercise, Figure, Resource
from app.resource_workflow import (
    RESOURCE_INBOX_TARGET_ID,
    build_resource_workflow_summary,
    resource_is_stale,
    resource_student_visibility_decision,
    resource_visibility_manifest_entry,
)

MARKDOWN_LINK_RE = re.compile(r"(\!?\[[^\]]*\]\()([^)]+)(\))")
TEACHER_BLOCK_RE = re.compile(r"\n?:::\s*\{\.teacher-only\}\n.*?\n:::\s*\n?", re.DOTALL)
STUDENT_BLOCK_RE = re.compile(r"\n?:::\s*\{\.student-only\}\n.*?\n:::\s*\n?", re.DOTALL)
SOLUTION_BLOCK_MARKER = "lf-solution-block"

TOPIC_TARGET_PREFIX = "topic-"
RESOURCE_LISTING_PREFIX = "resources-"
HOME_TARGET_ID = "home"

KIND_LABELS = {
    "home": "Home",
    "collection": "Lecture",
    "concept": "Concept",
    "course": "Course",
    "exercise": "Exercise",
    "figure": "Figure",
    "resource": "Resource",
    "resource-inbox": "Resource inbox",
    "resource-listing": "Resource listing",
    "topic-listing": "Topic listing",
}

KIND_SORT_ORDER = {
    "home": -1,
    "collection": 0,
    "concept": 1,
    "exercise": 2,
    "figure": 3,
    "resource": 4,
}


class AssemblyError(RuntimeError):
    pass


@dataclass(slots=True)
class FileDependency:
    path: str
    role: str
    sha256: str


@dataclass(slots=True)
class DependencyEdge:
    source_id: str
    source_kind: str
    target_id: str
    target_kind: str
    relationship: str


@dataclass(slots=True)
class LeakageObservation:
    source_path: str
    teacher_blocks_found: int
    teacher_blocks_removed: int
    student_blocks_found: int
    student_blocks_removed: int


@dataclass(slots=True)
class SolutionObservation:
    exercise_id: str
    source_path: str
    visibility: str
    included_in_output: bool
    reason: str


@dataclass(slots=True)
class FigureObservation:
    figure_id: str
    context_target_id: str
    context_target_kind: str
    relationship: str
    svg_source_path: str
    pdf_source_path: str
    interactive_source_path: str | None
    asset_inventory: list[str]
    interactive_included: bool
    fallback_asset_path: str
    d3_included: bool


@dataclass(slots=True)
class RelatedEntry:
    identifier: str
    kind: str
    title: str
    relationship: str
    href: str | None = None


@dataclass(slots=True)
class ListingEntry:
    identifier: str
    kind: str
    title: str
    description: str
    href: str | None = None


@dataclass(slots=True)
class AssignmentSourceSet:
    exercises: list[IndexedObject]
    listing_entries: list[ListingEntry]
    total_minutes: int
    concept_ids: list[str]
    topic_ids: list[str]


@dataclass(slots=True)
class BuildTargetRef:
    identifier: str
    kind: str
    output_category: str
    title: str


@dataclass(slots=True)
class DeliveryContext:
    date: date
    term: str
    manifest_id: str
    title_override: str | None = None
    additions: list[str] = field(default_factory=list)
    removals: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AssemblyDocument:
    target: BuildTargetRef
    audience: str
    language: str
    output_format: str
    generated_path: Path
    planned_output_path: Path
    markdown: str
    file_dependencies: list[FileDependency]
    dependency_edges: list[DependencyEdge]
    related_entries: list[RelatedEntry]
    listing_entries: list[ListingEntry]
    referenced_listing_targets: list[str]
    leakage_observations: list[LeakageObservation]
    solution_observations: list[SolutionObservation]
    figure_observations: list[FigureObservation]
    resource_workflow_summary: dict[str, object] | None = None

    def build_manifest_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "target": asdict(self.target),
            "audience": self.audience,
            "language": self.language,
            "format": self.output_format,
            "generated_path": str(self.generated_path),
            "planned_output_path": str(self.planned_output_path),
            "file_dependency_count": len(self.file_dependencies),
            "dependency_edge_count": len(self.dependency_edges),
            "solution_observation_count": len(self.solution_observations),
            "figure_observation_count": len(self.figure_observations),
            "related_entries": [asdict(entry) for entry in self.related_entries],
            "listing_entries": [asdict(entry) for entry in self.listing_entries],
            "referenced_listing_targets": self.referenced_listing_targets,
            "figure_uses": [asdict(item) for item in self.figure_observations],
        }
        if self.resource_workflow_summary is not None:
            payload["resource_workflow"] = self.resource_workflow_summary
        return payload

    def dependency_manifest_payload(self) -> dict[str, object]:
        return {
            "target": asdict(self.target),
            "audience": self.audience,
            "language": self.language,
            "format": self.output_format,
            "file_dependencies": [asdict(item) for item in self.file_dependencies],
            "dependency_edges": [asdict(item) for item in self.dependency_edges],
        }


def assemble_target(
    target_id: str,
    *,
    index: RepositoryIndex,
    audience: str,
    language: str,
    output_format: str,
    root: Path = REPO_ROOT,
    delivery_context: DeliveryContext | None = None,
    delivery_output_root: Path | None = None,
) -> AssemblyDocument:
    builder = AssemblyBuilder(
        index=index,
        audience=audience,
        language=language,
        output_format=output_format,
        root=root,
        delivery_context=delivery_context,
        delivery_output_root=delivery_output_root,
    )
    return builder.assemble(target_id)


class AssemblyBuilder:
    def __init__(
        self,
        *,
        index: RepositoryIndex,
        audience: str,
        language: str,
        output_format: str,
        root: Path,
        delivery_context: DeliveryContext | None = None,
        delivery_output_root: Path | None = None,
    ) -> None:
        self.index = index
        self.audience = audience
        self.language = language
        self.output_format = output_format
        self.root = root
        self.delivery_context = delivery_context
        self.delivery_output_root = delivery_output_root
        self.file_dependencies: dict[tuple[str, str], FileDependency] = {}
        self.dependency_edges: list[DependencyEdge] = []
        self.leakage_observations: list[LeakageObservation] = []
        self.solution_observations: list[SolutionObservation] = []
        self.figure_observations: list[FigureObservation] = []
        self.referenced_listing_targets: list[str] = []
        self.resource_workflow_summary: dict[str, object] | None = None
        self._d3_inlined: bool = False

    def assemble(self, target_id: str) -> AssemblyDocument:
        if target_id == HOME_TARGET_ID:
            return self._assemble_home_page()
        if target_id == RESOURCE_INBOX_TARGET_ID:
            return self._assemble_resource_inbox()
        if target_id in self.index.objects:
            record = self.index.objects[target_id]
            if isinstance(record.model, Collection):
                return self._assemble_collection(record)
            return self._assemble_object_page(record)
        if target_id in self.index.courses:
            return self._assemble_course_page(self.index.courses[target_id])
        if target_id.startswith(TOPIC_TARGET_PREFIX):
            return self._assemble_topic_listing(target_id)
        if target_id.startswith(RESOURCE_LISTING_PREFIX):
            return self._assemble_resource_listing(target_id)
        raise AssemblyError(f"unknown target id: {target_id}")

    def _assemble_home_page(self) -> AssemblyDocument:
        if self.audience != "student" or self.output_format != "html":
            raise AssemblyError("home builds currently support student html only")

        courses = [
            course
            for course in sorted(self.index.courses.values(), key=lambda item: item.model.id)
            if not self._exclude_from_audience(course.model.visibility)
            and self.language in course.model.languages
            and course.model.status in {"approved", "published", "archived"}
        ]
        topics = collect_topics(
            [
                record
                for record in self.index.objects.values()
                if self._is_listable(record, require_output_format="html")
            ]
        )
        resources = sorted(
            [
                record
                for record in self.index.objects.values()
                if isinstance(record.model, Resource)
                and self._is_listable(record, require_output_format="html")
            ],
            key=lambda item: item.model.title[self.language],
        )

        course_entries: list[ListingEntry] = []
        topic_entries: list[ListingEntry] = []
        resource_entries: list[ListingEntry] = []

        current_output = self._planned_output_path("home", HOME_TARGET_ID)

        for course_record in courses:
            self._register_file(course_record.course_path, role="home-course")
            self._register_file(course_record.plan_path, role="home-course-plan")
            self._register_edge(
                source_id=HOME_TARGET_ID,
                source_kind="home",
                target_id=course_record.model.id,
                target_kind="course",
                relationship="home-course",
            )
            course_entries.append(
                ListingEntry(
                    identifier=course_record.model.id,
                    kind="course",
                    title=course_record.model.title[self.language],
                    description=course_record.model.summary[self.language],
                    href=self._page_href(
                        current_output=current_output,
                        target_kind="course",
                        target_id=course_record.model.id,
                    ),
                )
            )

        for topic in topics:
            listing_id = f"{TOPIC_TARGET_PREFIX}{topic}"
            self.referenced_listing_targets.append(listing_id)
            self._register_edge(
                source_id=HOME_TARGET_ID,
                source_kind="home",
                target_id=listing_id,
                target_kind="topic-listing",
                relationship="home-topic",
            )
            topic_entries.append(
                ListingEntry(
                    identifier=listing_id,
                    kind="topic-listing",
                    title=humanize_slug(topic),
                    description=localized_count_label(
                        count_topic_items(
                            [
                                record
                                for record in self.index.objects.values()
                                if self._is_listable(record, require_output_format="html")
                            ],
                            topic,
                        ),
                        self.language,
                    ),
                    href=self._page_href(
                        current_output=current_output,
                        target_kind="topic-listing",
                        target_id=listing_id,
                    ),
                )
            )

        for resource_record in resources[:6]:
            self._register_object_files(resource_record, role="home-resource", include_note=False)
            self._register_edge(
                source_id=HOME_TARGET_ID,
                source_kind="home",
                target_id=resource_record.model.id,
                target_kind="resource",
                relationship="home-resource",
            )
            resource_entries.append(
                ListingEntry(
                    identifier=resource_record.model.id,
                    kind="resource",
                    title=resource_record.model.title[self.language],
                    description=resource_record.model.why_selected[self.language],
                    href=self._page_href(
                        current_output=current_output,
                        target_kind="resource",
                        target_id=resource_record.model.id,
                    ),
                )
            )

        intro = (
            "LearnForge organizes teaching material as reusable objects. Browse by course when "
            "you want a lecture path, or browse by topic when you want concepts, exercises, "
            "figures, and resources across courses."
            if self.language == "en"
            else "LearnForge organiserer undervisningsmateriale som gjenbrukbare objekter. "
            "Start med et kurs for en forelesningssti, eller start med et tema for begreper, "
            "øvinger, figurer og ressurser på tvers av kurs."
        )
        how_to_use = (
            "Use course pages for lecture order, exercises, and readings. Use topic pages for "
            "concept-centric navigation and related material."
            if self.language == "en"
            else "Bruk kurssidene for forelesningsrekkefølge, øvinger og lesestoff. Bruk "
            "temasidene for begrepsstyrt navigasjon og relatert materiale."
        )

        if self.output_format == "html":
            hero = f'<div class="lf-hero"><p class="lf-hero-tagline">{escape(intro)}</p></div>'
            how_to_use_section = "\n".join(
                [
                    "## How to Use This Site"
                    if self.language == "en"
                    else "## Slik bruker du siden",
                    "",
                    f"::: {{.callout-tip}}\n{how_to_use}\n:::",
                ]
            )
        else:
            hero = intro
            how_to_use_section = "\n".join(
                [
                    "## How to Use This Site"
                    if self.language == "en"
                    else "## Slik bruker du siden",
                    "",
                    how_to_use,
                ]
            )

        sections = [
            hero,
            self._render_listing_section(
                title="Browse by Course" if self.language == "en" else "Bla etter kurs",
                entries=course_entries,
            ),
            self._render_listing_section(
                title="Browse by Topic" if self.language == "en" else "Bla etter tema",
                entries=topic_entries,
            ),
            self._render_listing_section(
                title="Featured Resources" if self.language == "en" else "Utvalgte ressurser",
                entries=resource_entries,
            ),
            how_to_use_section,
        ]

        target = BuildTargetRef(
            identifier=HOME_TARGET_ID,
            kind="home",
            output_category="home",
            title="LearnForge" if self.language == "en" else "LearnForge",
        )
        return self._finalize_document(
            target=target,
            markdown_body="\n\n".join(sections).rstrip(),
            related_entries=[],
            listing_entries=[*course_entries, *topic_entries, *resource_entries],
        )

    def _assemble_object_page(self, record: IndexedObject) -> AssemblyDocument:
        self._ensure_visibility(record.model.visibility, record.model.id)
        self._ensure_language(record.model.languages, record.model.id)
        self._ensure_output_supported(record.model.outputs, record.model.id)
        if self.audience == "student" and isinstance(record.model, Resource):
            decision = resource_student_visibility_decision(
                record,
                language=self.language,
                require_output_format=self.output_format,
            )
            if not decision.visible_to_student:
                raise AssemblyError(
                    f"{record.model.id} is not student-publishable: {', '.join(decision.reasons)}"
                )
        self._register_object_files(record, role="primary-object", include_note=True)

        target = BuildTargetRef(
            identifier=record.model.id,
            kind=record.model.kind,
            output_category=record.model.kind,
            title=record.model.title[self.language],
        )
        content_parts = self._object_page_context_sections(record)
        if isinstance(record.model, Figure):
            content_parts.append(
                self._render_figure_embed(
                    record,
                    target=target,
                    relationship="primary-figure",
                    heading_level=None,
                    include_note=True,
                )
            )
        else:
            content_parts.append(self._load_object_note(record))
            if record.model.kind == "concept":
                figure_records = self._concept_figure_records(record)
                if figure_records:
                    content_parts.append(
                        self._render_figure_section(
                            title="Figures" if self.language == "en" else "Figurer",
                            records=figure_records,
                            target=target,
                            relationship="concept-figure",
                        )
                    )
        if isinstance(record.model, Exercise):
            solution_section = self._render_exercise_solution_for_page(record)
            if solution_section:
                content_parts.append(solution_section)
        if isinstance(record.model, Resource):
            self.resource_workflow_summary = {
                "resource": resource_visibility_manifest_entry(
                    record,
                    language=self.language,
                    require_output_format=self.output_format,
                )
            }
        related_entries = self._related_entries_for_object(record)
        if related_entries:
            content_parts.append(
                self._render_related_section(
                    title="Related links" if self.language == "en" else "Relaterte lenker",
                    entries=related_entries,
                )
            )
        assignment_entries = self._assignment_related_entries_for_object(record)
        if assignment_entries:
            content_parts.append(
                self._render_related_section(
                    title="Used in assignments" if self.language == "en" else "Brukt i oppgaveark",
                    entries=assignment_entries,
                )
            )
        course_entries = self._course_related_entries_for_record(record)
        if course_entries:
            content_parts.append(
                self._render_related_section(
                    title="Used in these courses"
                    if self.language == "en"
                    else "Brukt i disse kursene",
                    entries=course_entries,
                )
            )

        return self._finalize_document(
            target=target,
            markdown_body="\n\n".join(part.rstrip() for part in content_parts if part).rstrip(),
            related_entries=[*related_entries, *assignment_entries, *course_entries],
            listing_entries=[],
        )

    def _assemble_collection(self, record: IndexedObject) -> AssemblyDocument:
        self._ensure_visibility(record.model.visibility, record.model.id)
        self._ensure_language(record.model.languages, record.model.id)
        self._ensure_output_supported(record.model.outputs, record.model.id)
        if record.model.collection_kind == "assignment":
            if self.output_format == "exercise-sheet":
                return self._assemble_assignment_sheet(record)
            if self.output_format == "html":
                return self._assemble_assignment_page(record)
            raise AssemblyError(
                "assignment collections currently support html and exercise-sheet only"
            )
        self._register_object_files(record, role="primary-collection", include_note=False)

        item_entries: list[ListingEntry] = []
        parts: list[str] = []
        title = record.model.title[self.language]
        if self.delivery_context and self.delivery_context.title_override:
            title = self.delivery_context.title_override
        target = BuildTargetRef(
            identifier=record.model.id,
            kind="collection",
            output_category="collection",
            title=title,
        )
        if self.output_format == "html":
            course_entries = self._course_related_entries_for_record(record)
            if course_entries:
                parts.append(
                    self._render_related_section(
                        title="Course context" if self.language == "en" else "Kurskontekst",
                        entries=course_entries,
                    )
                )
            parts.append(self._render_collection_summary(record))
            parts.append("## Lecture Notes" if self.language == "en" else "## Forelesningsnotater")

        items = list(record.model.items)
        if self.delivery_context:
            removals_set = set(self.delivery_context.removals)
            items = [i for i in items if i not in removals_set]
            items.extend(self.delivery_context.additions)

        for item_id in items:
            item_record = self.index.objects[item_id]
            if self._exclude_from_audience(item_record.model.visibility):
                continue
            self._ensure_language(item_record.model.languages, item_id)
            self._register_edge(
                source_id=record.model.id,
                source_kind="collection",
                target_id=item_record.model.id,
                target_kind=item_record.model.kind,
                relationship="item",
            )
            self._register_object_files(item_record, role="collection-item", include_note=True)
            item_entries.append(
                ListingEntry(
                    identifier=item_record.model.id,
                    kind=item_record.model.kind,
                    title=item_record.model.title[self.language],
                    description=", ".join(item_record.model.topics),
                    href=self._page_href(
                        current_output=self._planned_output_path("collection", record.model.id),
                        target_kind=item_record.model.kind,
                        target_id=item_record.model.id,
                    ),
                )
            )
            if isinstance(item_record.model, Figure):
                parts.append(
                    self._render_figure_embed(
                        item_record,
                        target=target,
                        relationship="item",
                        heading_level=2,
                        include_note=True,
                    )
                )
            else:
                parts.append(self._load_object_note(item_record))
            parts.append("")
        return self._finalize_document(
            target=target,
            markdown_body="\n\n".join(part.rstrip() for part in parts if part).rstrip(),
            related_entries=[],
            listing_entries=item_entries,
        )

    def _assemble_assignment_page(self, record: IndexedObject) -> AssemblyDocument:
        self._register_object_files(record, role="primary-assignment", include_note=False)
        current_output = self._planned_output_path("collection", record.model.id)
        source_set = self._assignment_source_set(
            record,
            current_output=current_output,
            include_notes=False,
            observe_solutions=True,
        )
        course_entries = self._course_related_entries_for_record(record)
        concept_entries = self._assignment_concept_entries(
            record,
            concept_ids=source_set.concept_ids,
            current_output=current_output,
        )
        resource_entries = self._assignment_resource_entries(
            record,
            topic_ids=source_set.topic_ids,
            current_output=current_output,
        )

        parts: list[str] = []
        if course_entries:
            parts.append(
                self._render_related_section(
                    title="Course context" if self.language == "en" else "Kurskontekst",
                    entries=course_entries,
                )
            )
        parts.append(
            self._render_assignment_page_summary(
                record=record,
                source_set=source_set,
                current_output=current_output,
            )
        )
        parts.append(
            self._render_listing_section(
                title="Included exercises" if self.language == "en" else "Inkluderte oppgaver",
                entries=source_set.listing_entries,
            )
        )
        if concept_entries:
            parts.append(
                self._render_related_section(
                    title="Linked concepts" if self.language == "en" else "Knyttede begreper",
                    entries=concept_entries,
                )
            )
        if resource_entries:
            parts.append(
                self._render_related_section(
                    title="Related resources" if self.language == "en" else "Relaterte ressurser",
                    entries=resource_entries,
                )
            )

        target = BuildTargetRef(
            identifier=record.model.id,
            kind="collection",
            output_category="collection",
            title=record.model.title[self.language],
        )
        return self._finalize_document(
            target=target,
            markdown_body="\n\n".join(part.rstrip() for part in parts if part).rstrip(),
            related_entries=[*course_entries, *concept_entries, *resource_entries],
            listing_entries=source_set.listing_entries,
        )

    def _assemble_assignment_sheet(self, record: IndexedObject) -> AssemblyDocument:
        if self.output_format != "exercise-sheet":
            raise AssemblyError("assignment collections currently support exercise-sheet only")

        self._register_object_files(record, role="primary-assignment", include_note=False)
        current_output = self._planned_output_path("collection", record.model.id)
        include_solutions = self.audience == "teacher"
        source_set = self._assignment_source_set(
            record,
            current_output=current_output,
            include_notes=True,
            observe_solutions=False,
        )
        course_entries = self._course_related_entries_for_record(record)
        parts = [
            self._render_assignment_sheet_summary(
                record=record,
                exercises=source_set.exercises,
                total_minutes=source_set.total_minutes,
                concept_ids=source_set.concept_ids,
                include_solutions=include_solutions,
            )
        ]
        for index, exercise_record in enumerate(source_set.exercises, start=1):
            parts.append(
                self._render_assignment_exercise_section(
                    exercise_record,
                    number=index,
                    include_solution=include_solutions,
                )
            )

        title = record.model.title[self.language]
        if include_solutions:
            title = (
                f"{title} - Teacher Solution Sheet"
                if self.language == "en"
                else f"{title} - Løsningsark for lærer"
            )
        target = BuildTargetRef(
            identifier=record.model.id,
            kind="collection",
            output_category="collection",
            title=title,
        )
        return self._finalize_document(
            target=target,
            markdown_body="\n\n".join(part.rstrip() for part in parts if part).rstrip(),
            related_entries=course_entries,
            listing_entries=source_set.listing_entries,
        )

    def _assemble_course_page(self, record: IndexedCourse) -> AssemblyDocument:
        self._ensure_visibility(record.model.visibility, record.model.id)
        self._ensure_language(record.model.languages, record.model.id)
        if self.output_format not in {"html", "pdf"}:
            raise AssemblyError("course builds currently support html and pdf only")

        self._register_file(record.course_path, role="course-config")
        self._register_file(record.plan_path, role="course-plan")
        syllabus_path = record.syllabus_path(self.language)
        self._register_file(syllabus_path, role="course-syllabus")
        syllabus_text = self._strip_visibility_blocks(
            rewrite_relative_links(
                syllabus_path.read_text(encoding="utf-8"),
                syllabus_path.parent,
                self._generated_path("course", record.model.id),
            ),
            syllabus_path,
        )

        lecture_entries: list[ListingEntry] = []
        assignment_entries: list[ListingEntry] = []
        exercise_entries: list[ListingEntry] = []
        course_objects = self._course_objects(record.model.id)
        topics = collect_topics(course_objects)
        topic_entries: list[ListingEntry] = []
        resource_entries: list[ListingEntry] = []

        for course_object in course_objects:
            kind = (
                course_object.model.kind
                if not isinstance(course_object.model, Collection)
                else "collection"
            )
            self._register_object_files(
                course_object,
                role="course-content-source",
                include_note=False,
            )
            self._register_edge(
                source_id=record.model.id,
                source_kind="course",
                target_id=course_object.model.id,
                target_kind=kind,
                relationship="course-content",
            )

        for lecture_id in record.plan.lectures:
            lecture_record = self.index.objects[lecture_id]
            if not self._is_listable(lecture_record):
                continue
            self._register_edge(
                source_id=record.model.id,
                source_kind="course",
                target_id=lecture_record.model.id,
                target_kind="collection",
                relationship="lecture",
            )
            self._register_object_files(lecture_record, role="course-lecture", include_note=False)
            lecture_entries.append(
                ListingEntry(
                    identifier=lecture_record.model.id,
                    kind="collection",
                    title=lecture_record.model.title[self.language],
                    description=", ".join(lecture_record.model.topics),
                    href=self._page_href(
                        current_output=self._planned_output_path("course", record.model.id),
                        target_kind="collection",
                        target_id=lecture_record.model.id,
                    ),
                )
            )

        for assignment_id in record.plan.assignments:
            assignment_record = self.index.objects[assignment_id]
            if not self._is_listable(assignment_record, require_output_format="html"):
                continue
            source_set = self._assignment_source_set(
                assignment_record,
                current_output=self._planned_output_path("course", record.model.id),
                include_notes=False,
                observe_solutions=False,
            )
            self._register_edge(
                source_id=record.model.id,
                source_kind="course",
                target_id=assignment_record.model.id,
                target_kind="collection",
                relationship="assignment",
            )
            self._register_object_files(
                assignment_record,
                role="course-assignment",
                include_note=False,
            )
            assignment_entries.append(
                ListingEntry(
                    identifier=assignment_record.model.id,
                    kind="collection",
                    title=assignment_record.model.title[self.language],
                    description=self._assignment_listing_description(source_set),
                    href=self._page_href(
                        current_output=self._planned_output_path("course", record.model.id),
                        target_kind="collection",
                        target_id=assignment_record.model.id,
                    ),
                )
            )

        exercise_objects = [item for item in course_objects if item.model.kind == "exercise"]
        exercise_objects.sort(key=lambda item: item.model.title[self.language])
        for exercise_record in exercise_objects:
            self._register_object_files(
                exercise_record,
                role="course-exercise",
                include_note=False,
            )
            self._register_edge(
                source_id=record.model.id,
                source_kind="course",
                target_id=exercise_record.model.id,
                target_kind="exercise",
                relationship="course-exercise",
            )
            exercise_entries.append(
                ListingEntry(
                    identifier=exercise_record.model.id,
                    kind="exercise",
                    title=exercise_record.model.title[self.language],
                    description=localized_minutes(
                        exercise_record.model.estimated_time_minutes,
                        self.language,
                    ),
                    href=self._page_href(
                        current_output=self._planned_output_path("course", record.model.id),
                        target_kind="exercise",
                        target_id=exercise_record.model.id,
                    ),
                )
            )

        for topic in topics:
            listing_id = f"{TOPIC_TARGET_PREFIX}{topic}"
            self.referenced_listing_targets.append(listing_id)
            self._register_edge(
                source_id=record.model.id,
                source_kind="course",
                target_id=listing_id,
                target_kind="topic-listing",
                relationship="references-topic-listing",
            )
            topic_entries.append(
                ListingEntry(
                    identifier=listing_id,
                    kind="topic-listing",
                    title=humanize_slug(topic),
                    description=localized_count_label(
                        count_topic_items(course_objects, topic),
                        self.language,
                    ),
                    href=self._page_href(
                        current_output=self._planned_output_path("course", record.model.id),
                        target_kind="topic-listing",
                        target_id=listing_id,
                    ),
                )
            )

        course_resources = [
            item
            for item in course_objects
            if isinstance(item.model, Resource) and self._is_listable(item)
        ]
        course_resources.sort(key=lambda item: item.model.title[self.language])
        resource_listing_id = f"{RESOURCE_LISTING_PREFIX}{record.model.id}"
        has_resource_listing = bool(course_resources)
        self.referenced_listing_targets.append(resource_listing_id)
        self._register_edge(
            source_id=record.model.id,
            source_kind="course",
            target_id=resource_listing_id,
            target_kind="resource-listing",
            relationship="references-resource-listing",
        )
        for resource_record in course_resources:
            self._register_object_files(resource_record, role="course-resource", include_note=False)
            self._register_edge(
                source_id=record.model.id,
                source_kind="course",
                target_id=resource_record.model.id,
                target_kind="resource",
                relationship="course-resource",
            )
            resource_entries.append(
                ListingEntry(
                    identifier=resource_record.model.id,
                    kind="resource",
                    title=resource_record.model.title[self.language],
                    description=resource_record.model.why_selected[self.language],
                    href=self._page_href(
                        current_output=self._planned_output_path("course", record.model.id),
                        target_kind="resource",
                        target_id=resource_record.model.id,
                    ),
                )
            )

        summary_text = record.model.summary[self.language]
        if self.output_format == "html":
            course_summary = f'<div class="lf-course-header"><p>{escape(summary_text)}</p></div>'
        else:
            course_summary = summary_text

        sections = [
            course_summary,
            self._render_listing_section(
                title="Lectures" if self.language == "en" else "Forelesninger",
                entries=lecture_entries,
            ),
            self._render_listing_section(
                title="Exercises" if self.language == "en" else "Øvinger",
                entries=exercise_entries,
            ),
            self._render_listing_section(
                title="Assignments" if self.language == "en" else "Oppgaveark",
                entries=assignment_entries,
            ),
            self._render_listing_section(
                title="Topics" if self.language == "en" else "Temaer",
                entries=topic_entries,
                suffix=(
                    (
                        "See all curated resources: "
                        if self.language == "en"
                        else "Se alle kuraterte ressurser: "
                    )
                    + self._render_link(
                        resource_listing_id,
                        "resource-listing",
                        "All course resources" if self.language == "en" else "Alle kursressurser",
                        self._planned_output_path("course", record.model.id),
                    )
                    if self.output_format == "html" and has_resource_listing
                    else ""
                ),
            ),
            self._render_listing_section(
                title="Resources" if self.language == "en" else "Ressurser",
                entries=resource_entries,
                suffix=(
                    self._render_link(
                        resource_listing_id,
                        "resource-listing",
                        "Full resource listing"
                        if self.language == "en"
                        else "Full ressursoversikt",
                        self._planned_output_path("course", record.model.id),
                    )
                    if self.output_format == "html" and has_resource_listing
                    else ""
                ),
            ),
        ]
        if self.audience == "teacher":
            sections.append(
                "\n".join(
                    [
                        "## Teacher Notes",
                        "",
                        f"Owners: {', '.join(record.model.owners)}",
                        "",
                        f"Tracked lectures: {len(record.plan.lectures)}",
                    ]
                )
            )
        sections.append("## Syllabus" if self.language == "en" else "## Kursbeskrivelse")
        sections.append(syllabus_text)
        body = "\n\n".join(section for section in sections if section).rstrip()
        target = BuildTargetRef(
            identifier=record.model.id,
            kind="course",
            output_category="course",
            title=record.model.title[self.language],
        )
        return self._finalize_document(
            target=target,
            markdown_body=body,
            related_entries=[],
            listing_entries=[
                *lecture_entries,
                *assignment_entries,
                *exercise_entries,
                *topic_entries,
                *resource_entries,
            ],
        )

    def _assemble_topic_listing(self, target_id: str) -> AssemblyDocument:
        if self.output_format != "html":
            raise AssemblyError("topic listing builds currently support html only")

        topic = target_id.removeprefix(TOPIC_TARGET_PREFIX)
        matches = [
            item
            for item in self.index.objects.values()
            if topic in item.model.topics and self._is_listable(item, require_output_format="html")
        ]
        if not matches:
            raise AssemblyError(f"no content found for topic {topic}")

        for record in matches:
            kind = record.model.kind if not isinstance(record.model, Collection) else "collection"
            self._register_object_files(record, role="topic-listing-entry", include_note=False)
            self._register_edge(
                source_id=target_id,
                source_kind="topic-listing",
                target_id=record.model.id,
                target_kind=kind,
                relationship="topic-match",
            )

        current_output = self._planned_output_path("listing", target_id)
        entries = [
            ListingEntry(
                identifier=record.model.id,
                kind=record.model.kind
                if not isinstance(record.model, Collection)
                else "collection",
                title=record.model.title[self.language],
                description=", ".join(record.model.courses) or humanize_slug(topic),
                href=self._page_href(
                    current_output=current_output,
                    target_kind=(
                        record.model.kind
                        if not isinstance(record.model, Collection)
                        else "collection"
                    ),
                    target_id=record.model.id,
                ),
            )
            for record in sorted(
                matches,
                key=lambda item: topic_listing_sort_key(item, language=self.language),
            )
        ]
        related_courses = self._related_course_entries_for_topic(topic)
        body = self._render_listing_page(
            title=f"Topic: {humanize_slug(topic)}"
            if self.language == "en"
            else f"Tema: {humanize_slug(topic)}",
            entries=entries,
            group_by_kind=True,
            intro=(
                self._render_related_section(
                    title="Used in courses" if self.language == "en" else "Brukt i kurs",
                    entries=related_courses,
                )
                if related_courses
                else ""
            ),
        )
        target = BuildTargetRef(
            identifier=target_id,
            kind="topic-listing",
            output_category="listing",
            title=humanize_slug(topic),
        )
        return self._finalize_document(
            target=target,
            markdown_body=body,
            related_entries=[],
            listing_entries=entries,
        )

    def _assemble_resource_listing(self, target_id: str) -> AssemblyDocument:
        if self.output_format != "html":
            raise AssemblyError("resource listing builds currently support html only")

        course_id = target_id.removeprefix(RESOURCE_LISTING_PREFIX)
        course_record = self.index.courses.get(course_id)
        if course_record is None:
            raise AssemblyError(f"unknown course for resource listing: {course_id}")

        self._register_file(course_record.course_path, role="resource-listing-course")
        all_resources = [
            item
            for item in self.index.objects.values()
            if isinstance(item.model, Resource) and course_id in item.model.courses
        ]
        included_resources: list[IndexedObject] = []
        excluded_resources: list[dict[str, object]] = []
        for record in sorted(all_resources, key=lambda item: item.model.title[self.language]):
            decision = resource_student_visibility_decision(
                record,
                language=self.language,
                require_output_format="html",
            )
            if decision.visible_to_student:
                included_resources.append(record)
            else:
                excluded_resources.append(
                    {
                        "id": record.model.id,
                        "status": record.model.status,
                        "reasons": decision.reasons,
                    }
                )
        if not included_resources:
            raise AssemblyError(f"no resources found for course {course_id}")

        current_output = self._planned_output_path("listing", target_id)
        entries: list[ListingEntry] = []
        for record in included_resources:
            self._register_object_files(record, role="resource-listing-entry", include_note=False)
            self._register_edge(
                source_id=target_id,
                source_kind="resource-listing",
                target_id=record.model.id,
                target_kind="resource",
                relationship="course-resource",
            )
            entries.append(
                ListingEntry(
                    identifier=record.model.id,
                    kind="resource",
                    title=record.model.title[self.language],
                    description=record.model.why_selected[self.language],
                    href=self._page_href(
                        current_output=current_output,
                        target_kind="resource",
                        target_id=record.model.id,
                    ),
                )
            )

        title = (
            f"Resources for {course_record.model.title[self.language]}"
            if self.language == "en"
            else f"Ressurser for {course_record.model.title[self.language]}"
        )
        body = self._render_listing_page(
            title=title,
            entries=entries,
            group_by_kind=False,
            intro=self._render_related_section(
                title="Course page" if self.language == "en" else "Kursside",
                entries=[
                    RelatedEntry(
                        identifier=course_record.model.id,
                        kind="course",
                        title=course_record.model.title[self.language],
                        relationship="resource-listing-course",
                        href=self._page_href(
                            current_output=current_output,
                            target_kind="course",
                            target_id=course_record.model.id,
                        ),
                    )
                ],
            ),
        )
        self.resource_workflow_summary = {
            "course_id": course_id,
            "included_resource_ids": [record.model.id for record in included_resources],
            "excluded_resources": excluded_resources,
            "status_counts": build_resource_workflow_summary(
                self.index,
                language=self.language,
            )["status_counts"],
        }
        target = BuildTargetRef(
            identifier=target_id,
            kind="resource-listing",
            output_category="listing",
            title=title,
        )
        return self._finalize_document(
            target=target,
            markdown_body=body,
            related_entries=[],
            listing_entries=entries,
        )

    def _assemble_resource_inbox(self) -> AssemblyDocument:
        if self.audience != "teacher" or self.output_format != "html":
            raise AssemblyError("resource inbox builds currently support teacher html only")

        workflow_summary = build_resource_workflow_summary(self.index, language=self.language)
        resource_records = [
            record
            for record in sorted(self.index.objects.values(), key=lambda item: item.model.id)
            if isinstance(record.model, Resource)
        ]
        current_output = self._planned_output_path("listing", RESOURCE_INBOX_TARGET_ID)
        candidate_entries: list[ListingEntry] = []
        reviewed_entries: list[ListingEntry] = []
        stale_entries: list[ListingEntry] = []

        for record in resource_records:
            self._register_object_files(record, role="resource-inbox-entry", include_note=False)
            self._register_edge(
                source_id=RESOURCE_INBOX_TARGET_ID,
                source_kind="resource-inbox",
                target_id=record.model.id,
                target_kind="resource",
                relationship="resource-inbox-entry",
            )
            entry = ListingEntry(
                identifier=record.model.id,
                kind="resource",
                title=record.model.title[self.language],
                description=self._resource_inbox_description(record),
                href=self._page_href(
                    current_output=current_output,
                    target_kind="resource",
                    target_id=record.model.id,
                ),
            )
            if record.model.status == "candidate":
                candidate_entries.append(entry)
            if record.model.status == "reviewed":
                reviewed_entries.append(entry)
            if resource_is_stale(record.model):
                stale_entries.append(entry)

        counts = workflow_summary["status_counts"]
        body_sections = [
            "# Resource Inbox" if self.language == "en" else "# Ressursinnboks",
            "",
            (
                "Use this inbox to review candidate resources before they are approved for "
                "student publication."
                if self.language == "en"
                else "Bruk denne innboksen til a gjennomga ressurskandidater for de godkjennes "
                "for studentpublisering."
            ),
            "",
            "## Workflow summary" if self.language == "en" else "## Arbeidsflytsammendrag",
            "",
            f"- Candidate: {counts['candidate']}",
            f"- Reviewed: {counts['reviewed']}",
            f"- Approved: {counts['approved']}",
            f"- Published: {counts['published']}",
            (
                f"- Stale resources: {workflow_summary['stale_resource_count']}"
                if self.language == "en"
                else f"- Utløpende ressurser: {workflow_summary['stale_resource_count']}"
            ),
            "",
            self._render_listing_section(
                title="Candidate resources" if self.language == "en" else "Kandidatressurser",
                entries=candidate_entries,
            ),
            "",
            self._render_listing_section(
                title="Reviewed resources" if self.language == "en" else "Gjennomgaatte ressurser",
                entries=reviewed_entries,
            ),
            "",
            self._render_listing_section(
                title="Stale resources" if self.language == "en" else "Utløpende ressurser",
                entries=stale_entries,
            ),
        ]
        self.resource_workflow_summary = workflow_summary
        target = BuildTargetRef(
            identifier=RESOURCE_INBOX_TARGET_ID,
            kind="resource-inbox",
            output_category="listing",
            title="Resource Inbox" if self.language == "en" else "Ressursinnboks",
        )
        return self._finalize_document(
            target=target,
            markdown_body="\n".join(body_sections).rstrip(),
            related_entries=[],
            listing_entries=[*candidate_entries, *reviewed_entries, *stale_entries],
        )

    def _finalize_document(
        self,
        *,
        target: BuildTargetRef,
        markdown_body: str,
        related_entries: list[RelatedEntry],
        listing_entries: list[ListingEntry],
    ) -> AssemblyDocument:
        generated_path = self._generated_path(target.output_category, target.identifier)
        planned_output_path = self._planned_output_path(target.output_category, target.identifier)
        frontmatter_payload = {
            "title": target.title,
            "lang": self.language,
            "audience": self.audience,
            "language_variant": self.language,
        }
        if self.delivery_context:
            frontmatter_payload["date"] = self.delivery_context.date.isoformat()
        frontmatter = render_frontmatter(frontmatter_payload)
        body = markdown_body.rstrip()
        if self.audience in {"student", "teacher"} and self.output_format == "html":
            body = self._render_html_site_document(target=target, markdown_body=body)
        if self.output_format in {"html", "revealjs", "slides-pdf"} and self.figure_observations:
            body = "\n\n".join(
                [
                    "<style>",
                    FIGURE_RENDER_STYLE,
                    "</style>",
                    body,
                ]
            ).rstrip()
        markdown = frontmatter + "\n" + body + "\n"
        generated_path.parent.mkdir(parents=True, exist_ok=True)
        generated_path.write_text(markdown, encoding="utf-8")
        return AssemblyDocument(
            target=target,
            audience=self.audience,
            language=self.language,
            output_format=self.output_format,
            generated_path=generated_path,
            planned_output_path=planned_output_path,
            markdown=markdown,
            file_dependencies=sorted(
                self.file_dependencies.values(),
                key=lambda item: (item.role, item.path),
            ),
            dependency_edges=self.dependency_edges,
            related_entries=related_entries,
            listing_entries=listing_entries,
            referenced_listing_targets=sorted(set(self.referenced_listing_targets)),
            leakage_observations=self.leakage_observations,
            solution_observations=self.solution_observations,
            figure_observations=self.figure_observations,
            resource_workflow_summary=self.resource_workflow_summary,
        )

    def _render_html_site_document(
        self,
        *,
        target: BuildTargetRef,
        markdown_body: str,
    ) -> str:
        current_output = self._planned_output_path(target.output_category, target.identifier)
        page_style = self._html_page_style(target.kind)
        footer = self._render_html_footer(current_output=current_output)
        shell = [
            self._render_html_shell_assets(current_output=current_output),
            (
                f'<div class="lf-app-shell" data-target-kind="{escape(target.kind)}" '
                f'data-page-style="{page_style}" data-audience="{self.audience}">'
            ),
            self._render_html_shell(target=target, current_output=current_output),
            '<main class="lf-page-frame">',
            '<div class="lf-page-content">',
        ]
        if self.audience == "teacher":
            shell.extend(
                [
                    self._render_teacher_preview_notice(),
                    self._render_teacher_review_panel(target=target),
                ]
            )
        shell.extend(
            [
                markdown_body,
                "</div>",
                "</main>",
            ]
        )
        if footer:
            shell.append(footer)
        shell.append("</div>")
        return "\n\n".join(part for part in shell if part).rstrip()

    def _html_page_style(self, target_kind: str) -> str:
        if target_kind in {"home", "course", "topic-listing", "resource-listing", "resource-inbox"}:
            return "explore"
        return "document"

    def _render_html_shell_assets(self, *, current_output: Path) -> str:
        css_href = self._html_shell_asset_href(
            current_output=current_output,
            filename="learnforge-shell.css",
        )
        script_href = self._html_shell_asset_href(
            current_output=current_output,
            filename="learnforge-shell.js",
        )
        return "\n".join(
            [
                f'<link rel="stylesheet" href="{css_href}" />',
                f'<script src="{script_href}" defer></script>',
            ]
        )

    def _render_html_shell(self, *, target: BuildTargetRef, current_output: Path) -> str:
        if self.audience == "teacher":
            return self._render_teacher_shell(target=target, current_output=current_output)
        return self._render_student_shell(target=target, current_output=current_output)

    def _render_student_shell(self, *, target: BuildTargetRef, current_output: Path) -> str:
        home_href = self._student_home_href(current_output=current_output)
        courses_href = f"{home_href}#browse-by-course" if home_href else "#browse-by-course"
        topics_href = f"{home_href}#browse-by-topic" if home_href else "#browse-by-topic"
        resources_href = f"{home_href}#featured-resources" if home_href else "#featured-resources"
        search_placeholder = (
            "Search concepts, lectures, exercises, or resources"
            if self.language == "en"
            else "Søk i begreper, forelesninger, øvinger eller ressurser"
        )
        search_label = "Search LearnForge" if self.language == "en" else "Søk i LearnForge"
        search_button = "Search" if self.language == "en" else "Søk"
        nav_label = "Student site navigation" if self.language == "en" else "Studentnavigasjon"
        menu_label = "Menu" if self.language == "en" else "Meny"
        search_toggle_label = "Search" if self.language == "en" else "Søk"
        empty_results_message = "No matching pages." if self.language == "en" else "Ingen treff."
        search_unavailable_message = (
            "Search index is not available for this page yet."
            if self.language == "en"
            else "Søkeindeksen er ikke tilgjengelig for denne siden ennå."
        )
        nav_panel_id = "lf-shell-nav"
        search_panel_id = "lf-shell-search"

        sections = [
            '<header class="lf-app-header">',
            '<div class="lf-app-header-bar">',
            f'<a class="lf-brand" href="{home_href}">LearnForge</a>',
            '<div class="lf-shell-toggle-row">',
            (
                f'<button class="lf-shell-toggle" type="button" '
                f'data-shell-toggle="{nav_panel_id}" aria-controls="{nav_panel_id}" '
                f'aria-expanded="false">{menu_label}</button>'
            ),
            (
                f'<button class="lf-shell-toggle" type="button" '
                f'data-shell-toggle="{search_panel_id}" aria-controls="{search_panel_id}" '
                f'aria-expanded="false">{search_toggle_label}</button>'
            ),
            "</div>",
            "</div>",
            f'<div id="{nav_panel_id}" class="lf-shell-panel lf-shell-nav-panel" hidden>',
            f'<nav class="lf-primary-nav" aria-label="{nav_label}">',
            self._render_student_nav_links(
                home_href=home_href,
                courses_href=courses_href,
                topics_href=topics_href,
                resources_href=resources_href,
            ),
            "</nav>",
            '<div class="lf-utility-links">',
            self._render_shell_utility_links(target=target, current_output=current_output),
            "</div>",
            "</div>",
            f'<div id="{search_panel_id}" class="lf-shell-panel lf-shell-search-panel" hidden>',
            self._render_student_search_form(
                current_output=current_output,
                search_label=search_label,
                search_button=search_button,
                search_placeholder=search_placeholder,
                empty_results_message=empty_results_message,
                search_unavailable_message=search_unavailable_message,
            ),
            "</div>",
            "</header>",
        ]
        return "\n".join(part for part in sections if part)

    def _render_teacher_shell(self, *, target: BuildTargetRef, current_output: Path) -> str:
        home_href = self._student_home_href(current_output=current_output) or "#"
        sections = [
            '<header class="lf-app-header">',
            '<div class="lf-app-header-bar">',
            f'<a class="lf-brand" href="{home_href}">LearnForge</a>',
            "</div>",
            '<div class="lf-shell-panel lf-shell-utility-panel">',
            '<div class="lf-utility-links">',
            self._render_shell_utility_links(target=target, current_output=current_output),
            "</div>",
            "</div>",
            "</header>",
        ]
        return "\n".join(part for part in sections if part)

    def _render_shell_utility_links(
        self,
        *,
        target: BuildTargetRef,
        current_output: Path,
    ) -> str:
        sections = [
            self._render_breadcrumbs(target=target, current_output=current_output),
            self._render_view_switch(target=target, current_output=current_output),
            self._render_language_switch(target=target, current_output=current_output),
            self._render_export_links(target=target, current_output=current_output),
        ]
        return "\n".join(part for part in sections if part)

    def _render_student_nav_links(
        self,
        *,
        home_href: str | None,
        courses_href: str,
        topics_href: str,
        resources_href: str,
    ) -> str:
        links = [
            (
                home_href,
                "Home" if self.language == "en" else "Hjem",
            ),
            (
                courses_href,
                "Courses" if self.language == "en" else "Kurs",
            ),
            (
                topics_href,
                "Topics" if self.language == "en" else "Temaer",
            ),
            (
                resources_href,
                "Resources" if self.language == "en" else "Ressurser",
            ),
        ]
        return "\n".join(
            f'<a class="lf-primary-nav-link" href="{href}">{label}</a>'
            for href, label in links
            if href
        )

    def _render_student_search_form(
        self,
        *,
        current_output: Path,
        search_label: str,
        search_button: str,
        search_placeholder: str,
        empty_results_message: str,
        search_unavailable_message: str,
    ) -> str:
        sections = [
            (
                f'<form class="lf-search-form" '
                f'data-search-index="{self._search_index_href(current_output)}" '
                f'data-empty-results-message="{escape(empty_results_message)}" '
                f'data-search-unavailable-message="{escape(search_unavailable_message)}" '
                'data-result-label="lf-search-results" role="search">'
            ),
            f'<label for="lf-search-input">{search_label}</label>',
            '<div class="lf-search-controls">',
            (
                f'<input id="lf-search-input" name="q" type="search" '
                f'placeholder="{search_placeholder}" />'
            ),
            f'<button type="submit">{search_button}</button>',
            "</div>",
            '<div class="lf-search-results" hidden aria-live="polite"></div>',
            "</form>",
        ]
        return "\n".join(sections)

    def _html_shell_asset_href(self, *, current_output: Path, filename: str) -> str:
        asset_path = html_shell_asset_path(self.root, self.audience, self.language, filename)
        return os.path.relpath(asset_path, current_output.parent).replace(os.sep, "/")

    def _render_html_footer(self, *, current_output: Path) -> str:
        if self.audience != "student":
            return ""
        return self._render_student_footer(current_output=current_output)

    def _render_student_footer(self, *, current_output: Path) -> str:
        home_href = self._student_home_href(current_output=current_output)
        course_browse_href = f"{home_href}#browse-by-course" if home_href else "#browse-by-course"
        topic_browse_href = f"{home_href}#browse-by-topic" if home_href else "#browse-by-topic"
        text = (
            "Browse by course for lecture order and assignments, "
            "or by topic for concept-first study."
            if self.language == "en"
            else "Bla etter kurs for forelesningsrekkefølge og oppgaver, "
            "eller etter tema for begrepsbasert lesing."
        )
        course_label = "course index" if self.language == "en" else "kursoversikt"
        topic_label = "topic index" if self.language == "en" else "temaoversikt"
        return "\n".join(
            [
                '<footer class="lf-page-footer">',
                (f"<p>{text} Start from the " if self.language == "en" else f"<p>{text} Start fra ")
                + f'<a href="{course_browse_href}">{course_label}</a> '
                + ("or the " if self.language == "en" else "eller ")
                + f'<a href="{topic_browse_href}">{topic_label}</a>.</p>',
                "</footer>",
            ]
        )

    def _render_breadcrumbs(self, *, target: BuildTargetRef, current_output: Path) -> str:
        parts = self._breadcrumbs(target=target, current_output=current_output)
        label = "Breadcrumbs" if self.language == "en" else "Brødsmuler"
        return f'<p class="lf-breadcrumbs"><strong>{label}:</strong> {" / ".join(parts)}</p>'

    def _breadcrumbs(self, *, target: BuildTargetRef, current_output: Path) -> list[str]:
        home_href = self._student_home_href(current_output=current_output)
        home_label = "Home" if self.language == "en" else "Hjem"
        parts = [f'<a href="{home_href}">{home_label}</a>']

        if target.kind == "home":
            return [home_label]

        if target.kind == "course":
            parts.append(target.title)
            return parts

        if target.kind == "collection":
            record = self.index.objects[target.identifier]
            parts.extend(self._course_breadcrumb_parts(record.model.courses, current_output))
            parts.append(target.title)
            return parts

        if target.kind == "topic-listing":
            parts.append(
                f'<a href="{home_href}#browse-by-topic">'
                + ("Topics" if self.language == "en" else "Temaer")
                + "</a>"
            )
            parts.append(target.title)
            return parts

        if target.kind == "resource-listing":
            course_id = target.identifier.removeprefix(RESOURCE_LISTING_PREFIX)
            course_record = self.index.courses.get(course_id)
            parts.extend(self._course_breadcrumb_parts([course_id], current_output))
            parts.append("Resources" if self.language == "en" else "Ressurser")
            if course_record is None:
                return parts
            return parts

        if target.kind == "resource-inbox":
            parts.append(target.title)
            return parts

        if target.kind in {"concept", "exercise", "figure", "resource"}:
            record = self.index.objects[target.identifier]
            if self.audience == "student" and record.model.topics:
                topic = record.model.topics[0]
                topic_id = f"{TOPIC_TARGET_PREFIX}{topic}"
                topic_href = self._page_href(
                    current_output=current_output,
                    target_kind="topic-listing",
                    target_id=topic_id,
                )
                parts.append(f'<a href="{topic_href}">{humanize_slug(topic)}</a>')
            else:
                parts.extend(self._course_breadcrumb_parts(record.model.courses, current_output))
            parts.append(target.title)
            return parts

        parts.append(target.title)
        return parts

    def _course_breadcrumb_parts(self, course_ids: list[str], current_output: Path) -> list[str]:
        if not course_ids:
            return []
        course_record = next(
            (
                self.index.courses[course_id]
                for course_id in course_ids
                if course_id in self.index.courses
                and self.language in self.index.courses[course_id].model.title
            ),
            None,
        )
        if course_record is None:
            return []
        course_href = self._page_href(
            current_output=current_output,
            target_kind="course",
            target_id=course_record.model.id,
        )
        return [f'<a href="{course_href}">{course_record.model.title[self.language]}</a>']

    def _render_language_switch(self, *, target: BuildTargetRef, current_output: Path) -> str:
        label = "Language" if self.language == "en" else "Språk"
        options: list[str] = []
        for language in ("en", "nb"):
            language_label = localized_language_name(language, self.language)
            if language == self.language:
                options.append(f"<strong>{language_label}</strong>")
                continue
            href = self._counterpart_href(
                target=target,
                current_output=current_output,
                language=language,
            )
            if href:
                options.append(f'<a href="{href}">{language_label}</a>')
            else:
                fallback = self._fallback_language_home_href(
                    current_output=current_output,
                    language=language,
                )
                fallback_suffix = "(home)" if self.language == "en" else "(hjem)"
                options.append(f'<a href="{fallback}">{language_label} {fallback_suffix}</a>')
        return f'<p class="lf-language-switch"><strong>{label}:</strong> {" | ".join(options)}</p>'

    def _render_view_switch(self, *, target: BuildTargetRef, current_output: Path) -> str:
        if target.kind in {"home", "topic-listing", "resource-listing", "resource-inbox"}:
            return ""
        counterpart_audience = "teacher" if self.audience == "student" else "student"
        href = self._audience_counterpart_href(
            target=target,
            current_output=current_output,
            audience=counterpart_audience,
            language=self.language,
        )
        if href is None:
            return ""
        label = "View" if self.language == "en" else "Visning"
        student_label = "Student" if self.language == "en" else "Student"
        teacher_label = "Instructor" if self.language == "en" else "Instruktør"
        current_label = student_label if self.audience == "student" else teacher_label
        counterpart_label = teacher_label if self.audience == "student" else student_label
        options = [f"<strong>{current_label}</strong>", f'<a href="{href}">{counterpart_label}</a>']
        return f'<p class="lf-view-switch"><strong>{label}:</strong> {" | ".join(options)}</p>'

    def _counterpart_href(
        self,
        *,
        target: BuildTargetRef,
        current_output: Path,
        language: str,
    ) -> str | None:
        if target.kind == "home":
            return self._page_href_for_variant(
                current_output=current_output,
                target_kind="home",
                target_id=HOME_TARGET_ID,
                audience=self.audience,
                language=language,
            )

        if target.kind == "course":
            course_record = self.index.courses.get(target.identifier)
            if course_record is None:
                return None
            if self.audience == "student":
                if not (
                    course_record.model.visibility not in {"private", "teacher"}
                    and course_record.model.status in {"approved", "published"}
                    and language in course_record.model.languages
                ):
                    return None
            elif language not in course_record.model.languages:
                return None
            return self._page_href_for_variant(
                current_output=current_output,
                target_kind="course",
                target_id=target.identifier,
                audience=self.audience,
                language=language,
            )

        if target.kind in {"topic-listing", "resource-listing"}:
            counterpart_supported = self._listing_has_language(
                target.identifier, target.kind, language
            )
            if not counterpart_supported:
                return None
            return self._page_href_for_variant(
                current_output=current_output,
                target_kind=target.kind,
                target_id=target.identifier,
                audience=self.audience,
                language=language,
            )

        if target.identifier not in self.index.objects:
            return None
        record = self.index.objects[target.identifier]
        if not self._language_available(
            record.model.languages, record.model.translation_status, language
        ):
            return None
        return self._page_href_for_variant(
            current_output=current_output,
            target_kind=target.kind,
            target_id=target.identifier,
            audience=self.audience,
            language=language,
        )

    def _listing_has_language(self, identifier: str, target_kind: str, language: str) -> bool:
        if target_kind == "topic-listing":
            topic = identifier.removeprefix(TOPIC_TARGET_PREFIX)
            return any(
                topic in record.model.topics
                and self._is_listable(
                    record,
                    language=language,
                    require_output_format="html",
                )
                for record in self.index.objects.values()
            )
        if target_kind == "resource-listing":
            course_id = identifier.removeprefix(RESOURCE_LISTING_PREFIX)
            course_record = self.index.courses.get(course_id)
            if course_record is None or language not in course_record.model.languages:
                return False
            return any(
                isinstance(record.model, Resource)
                and course_id in record.model.courses
                and self._is_listable(
                    record,
                    language=language,
                    require_output_format="html",
                )
                for record in self.index.objects.values()
            )
        return False

    def _fallback_language_home_href(self, *, current_output: Path, language: str) -> str:
        return (
            self._page_href_for_variant(
                current_output=current_output,
                target_kind="home",
                target_id=HOME_TARGET_ID,
                audience="student",
                language=language,
            )
            or "#"
        )

    def _render_export_links(self, *, target: BuildTargetRef, current_output: Path) -> str:
        export_links = self._available_export_links(target=target, current_output=current_output)
        if not export_links:
            return ""
        label = "Exports" if self.language == "en" else "Eksporter"
        return (
            f'<p class="lf-export-links"><strong>{label}:</strong> {" | ".join(export_links)}</p>'
        )

    def _available_export_links(self, *, target: BuildTargetRef, current_output: Path) -> list[str]:
        if target.kind in {"home", "topic-listing", "resource-listing"}:
            return []
        if target.kind == "course":
            if target.identifier not in self.index.courses:
                return []
            outputs = {"html", "pdf"}
        else:
            record = self.index.objects.get(target.identifier)
            if record is None:
                return []
            outputs = set(record.model.outputs)

        links: list[str] = []
        labels = {
            "pdf": "PDF",
            "revealjs": "Slides" if self.language == "en" else "Lysbilder",
            "slides-pdf": "Slide PDF" if self.language == "en" else "Lysbilder PDF",
            "handout": "Handout" if self.language == "en" else "Handout",
            "exercise-sheet": (
                "Solution sheet"
                if self.audience == "teacher" and self.language == "en"
                else (
                    "Løsningsark"
                    if self.audience == "teacher"
                    else ("Exercise sheet" if self.language == "en" else "Øvingsark")
                )
            ),
        }
        if "revealjs" in outputs:
            outputs.add("slides-pdf")

        for export_format in ("pdf", "revealjs", "slides-pdf", "handout", "exercise-sheet"):
            if export_format not in outputs:
                continue
            export_path = planned_target_output_path(
                self.root,
                audience=self.audience,
                language=self.language,
                output_format=export_format,
                target_kind=target.kind,
                target_id=target.identifier,
            )
            if not export_path.exists():
                continue
            href = os.path.relpath(export_path, current_output.parent).replace(os.sep, "/")
            links.append(f'<a href="{href}">{labels[export_format]}</a>')
        return links

    def _search_index_href(self, current_output: Path) -> str:
        search_index_path = student_search_index_path(self.root, self.language)
        return os.path.relpath(search_index_path, current_output.parent).replace(os.sep, "/")

    def _output_label(self, output_format: str) -> str:
        labels = {
            "html": "HTML",
            "pdf": "PDF",
            "revealjs": "Slides" if self.language == "en" else "Lysbilder",
            "slides-pdf": "Slide PDF" if self.language == "en" else "Lysbilder PDF",
            "handout": "Handout" if self.language == "en" else "Handout",
            "exercise-sheet": "Exercise sheet" if self.language == "en" else "Øvingsark",
        }
        return labels.get(output_format, output_format)

    def _render_teacher_preview_notice(self) -> str:
        text = (
            "Instructor preview only. Edit source files in nvim and keep approvals in the CLI."
            if self.language == "en"
            else (
                "Kun instruktørforhåndsvisning. Rediger kildefilene i nvim og "
                "behold godkjenninger i CLI-en."
            )
        )
        return f'<section class="lf-preview-notice"><p>{escape(text)}</p></section>'

    def _render_teacher_review_panel(self, *, target: BuildTargetRef) -> str:
        title = "Instructor preview context" if self.language == "en" else "Instruktørkontekst"
        items = "\n".join(
            f"<li><strong>{escape(label)}:</strong> {escape(value)}</li>"
            for label, value in self._teacher_review_panel_rows(target=target)
        )
        return "\n".join(
            [
                '<section class="lf-review-panel lf-meta-panel">',
                f'<p class="lf-review-panel-title">{escape(title)}</p>',
                "<ul>",
                items,
                "</ul>",
                "</section>",
            ]
        )

    def _teacher_review_panel_rows(self, *, target: BuildTargetRef) -> list[tuple[str, str]]:
        labels = {
            "id": "ID" if self.language == "en" else "ID",
            "kind": "Kind" if self.language == "en" else "Type",
            "audience": "Audience" if self.language == "en" else "Målgruppe",
            "language": "Language" if self.language == "en" else "Språk",
            "visibility": "Visibility" if self.language == "en" else "Synlighet",
            "status": "Status" if self.language == "en" else "Status",
            "updated": "Updated" if self.language == "en" else "Oppdatert",
            "outputs": "Outputs" if self.language == "en" else "Utdata",
            "translation_state": (
                "Translation state" if self.language == "en" else "Oversettelsesstatus"
            ),
            "solution_visibility": (
                "Solution visibility" if self.language == "en" else "Løsningssynlighet"
            ),
            "collection_type": ("Collection type" if self.language == "en" else "Samlingstype"),
            "review_after": "Review after" if self.language == "en" else "Gjennomgå etter",
            "stale": "Stale" if self.language == "en" else "Utløpt",
        }
        rows = [
            (labels["id"], target.identifier),
            (labels["kind"], self._teacher_target_kind_label(target.kind)),
            (labels["audience"], "Instructor" if self.language == "en" else "Instruktør"),
            (labels["language"], localized_language_name(self.language, self.language)),
        ]
        if target.kind == "resource-inbox":
            rows.extend(
                [
                    (labels["visibility"], "Teacher" if self.language == "en" else "Lærer"),
                    (labels["status"], "Review" if self.language == "en" else "Gjennomgang"),
                    (labels["updated"], "-"),
                    (labels["outputs"], self._output_label("html")),
                ]
            )
            return rows

        if target.kind == "course":
            course_record = self.index.courses[target.identifier]
            rows.extend(
                [
                    (labels["visibility"], course_record.model.visibility),
                    (labels["status"], course_record.model.status),
                    (labels["updated"], course_record.model.updated.isoformat()),
                    (
                        labels["outputs"],
                        ", ".join(self._output_label(item) for item in ("html", "pdf")),
                    ),
                ]
            )
            return rows

        record = self.index.objects[target.identifier]
        rows.extend(
            [
                (labels["visibility"], record.model.visibility),
                (labels["status"], record.model.status),
                (labels["updated"], record.model.updated.isoformat()),
                (
                    labels["outputs"],
                    ", ".join(self._output_label(item) for item in record.model.outputs),
                ),
            ]
        )
        translation_state = record.model.translation_status.get(self.language)
        if translation_state:
            rows.append((labels["translation_state"], translation_state))
        if isinstance(record.model, Exercise):
            rows.append((labels["solution_visibility"], record.model.solution_visibility))
        if isinstance(record.model, Collection):
            rows.append((labels["collection_type"], record.model.collection_kind))
        if isinstance(record.model, Resource):
            if record.model.review_after is not None:
                rows.append((labels["review_after"], record.model.review_after.isoformat()))
            stale_value = "Yes" if resource_is_stale(record.model) else "No"
            if self.language != "en":
                stale_value = "Ja" if resource_is_stale(record.model) else "Nei"
            rows.append((labels["stale"], stale_value))
        return rows

    def _teacher_target_kind_label(self, kind: str) -> str:
        labels = {
            "collection": "Collection" if self.language == "en" else "Samling",
            "concept": "Concept" if self.language == "en" else "Begrep",
            "course": "Course" if self.language == "en" else "Kurs",
            "exercise": "Exercise" if self.language == "en" else "Øvelse",
            "figure": "Figure" if self.language == "en" else "Figur",
            "resource": "Resource" if self.language == "en" else "Ressurs",
            "resource-inbox": "Resource inbox" if self.language == "en" else "Ressursinnboks",
        }
        return labels.get(kind, kind)

    def _object_page_context_sections(self, record: IndexedObject) -> list[str]:
        if record.model.kind == "concept":
            return [self._render_concept_summary(record)]
        if record.model.kind == "exercise":
            return [self._render_exercise_summary(record)]
        if record.model.kind == "figure":
            return [self._render_figure_summary(record)]
        if record.model.kind == "resource":
            return [self._render_resource_summary(record)]
        return []

    def _render_concept_summary(self, record: IndexedObject) -> str:
        heading = "## At a glance" if self.language == "en" else "## Kort oversikt"
        items = [
            f"- {('Level' if self.language == 'en' else 'Nivå')}: {record.model.level}",
        ]
        topic_links = self._topic_links(record, current_kind="concept")
        if topic_links:
            items.append(
                f"- {('Topics' if self.language == 'en' else 'Temaer')}: {', '.join(topic_links)}"
            )
        course_links = self._course_links(record.model.courses, record.model.kind, record.model.id)
        if course_links:
            items.append(
                f"- {('Courses' if self.language == 'en' else 'Kurs')}: {', '.join(course_links)}"
            )
        if self.output_format == "html":
            inner = "\n".join(items)
            return f'{heading}\n\n<div class="lf-meta-panel">\n\n{inner}\n\n</div>'
        return "\n".join([heading, "", *items])

    def _render_exercise_summary(self, record: IndexedObject) -> str:
        heading = "## Exercise details" if self.language == "en" else "## Oppgavedetaljer"
        items = [
            f"- {('Type' if self.language == 'en' else 'Type')}: {record.model.exercise_type}",
            (
                f"- {('Difficulty' if self.language == 'en' else 'Vanskelighetsgrad')}: "
                f"{record.model.difficulty}"
            ),
            (
                f"- {('Time' if self.language == 'en' else 'Tid')}: "
                f"{localized_minutes(record.model.estimated_time_minutes, self.language)}"
            ),
            (
                f"- {('Solution visibility' if self.language == 'en' else 'Løsningssynlighet')}: "
                + (
                    "teacher-only separate file"
                    if record.model.solution_visibility == "teacher" and self.language == "en"
                    else (
                        "egen fil kun for lærer"
                        if record.model.solution_visibility == "teacher"
                        else ("private file" if self.language == "en" else "privat fil")
                    )
                )
            ),
            (
                f"- {('Outputs' if self.language == 'en' else 'Utdata')}: "
                f"{', '.join(self._output_label(output) for output in record.model.outputs)}"
            ),
        ]
        concept_links = [
            self._render_link(
                concept_id,
                "concept",
                self.index.objects[concept_id].model.title[self.language],
                self._planned_output_path(record.model.kind, record.model.id),
            )
            for concept_id in record.model.concepts
            if concept_id in self.index.objects
            and self._is_listable(
                self.index.objects[concept_id],
                require_output_format="html",
            )
        ]
        if concept_links:
            items.append(
                f"- {('Concepts' if self.language == 'en' else 'Begreper')}: "
                f"{', '.join(concept_links)}"
            )
        course_links = self._course_links(record.model.courses, record.model.kind, record.model.id)
        if course_links:
            items.append(
                f"- {('Courses' if self.language == 'en' else 'Kurs')}: {', '.join(course_links)}"
            )
        if self.output_format == "html":
            inner = "\n".join(items)
            return f'{heading}\n\n<div class="lf-meta-panel">\n\n{inner}\n\n</div>'
        return "\n".join([heading, "", *items])

    def _render_figure_summary(self, record: IndexedObject) -> str:
        interactive_label = (
            "local JS enhancement with static fallback"
            if record.model.interactive_path and self.language == "en"
            else (
                "lokal JS-forbedring med statisk fallback"
                if record.model.interactive_path
                else ("static only" if self.language == "en" else "kun statisk")
            )
        )
        heading = "## Figure details" if self.language == "en" else "## Figurdetaljer"
        items = [
            f"- {('Interactive mode' if self.language == 'en' else 'Interaktiv modus')}: "
            f"{interactive_label}",
            (
                f"- {('Outputs' if self.language == 'en' else 'Utdata')}: "
                f"{', '.join(self._output_label(output) for output in record.model.outputs)}"
            ),
        ]
        concept_links = [
            self._render_link(
                concept_id,
                "concept",
                self.index.objects[concept_id].model.title[self.language],
                self._planned_output_path(record.model.kind, record.model.id),
            )
            for concept_id in record.model.concepts
            if concept_id in self.index.objects
            and self._is_listable(
                self.index.objects[concept_id],
                require_output_format="html",
            )
        ]
        if concept_links:
            items.append(
                f"- {('Linked concepts' if self.language == 'en' else 'Knyttede begreper')}: "
                f"{', '.join(concept_links)}"
            )
        topic_links = self._topic_links(record, current_kind="figure")
        if topic_links:
            items.append(
                f"- {('Topics' if self.language == 'en' else 'Temaer')}: {', '.join(topic_links)}"
            )
        course_links = self._course_links(record.model.courses, record.model.kind, record.model.id)
        if course_links:
            items.append(
                f"- {('Courses' if self.language == 'en' else 'Kurs')}: {', '.join(course_links)}"
            )
        if self.output_format == "html":
            inner = "\n".join(items)
            return f'{heading}\n\n<div class="lf-meta-panel">\n\n{inner}\n\n</div>'
        return "\n".join([heading, "", *items])

    def _concept_figure_records(self, record: IndexedObject) -> list[IndexedObject]:
        figures: list[IndexedObject] = []
        for related_id in record.model.related:
            related_record = self.index.objects.get(related_id)
            if related_record is None or not isinstance(related_record.model, Figure):
                continue
            if not self._is_listable(related_record):
                continue
            figures.append(related_record)
        return figures

    def _render_figure_section(
        self,
        *,
        title: str,
        records: list[IndexedObject],
        target: BuildTargetRef,
        relationship: str,
    ) -> str:
        sections = [f"## {title}"]
        for record in records:
            sections.extend(
                [
                    "",
                    self._render_figure_embed(
                        record,
                        target=target,
                        relationship=relationship,
                        heading_level=3,
                        include_note=True,
                    ),
                ]
            )
        return "\n".join(sections).rstrip()

    def _render_figure_embed(
        self,
        record: IndexedObject,
        *,
        target: BuildTargetRef,
        relationship: str,
        heading_level: int | None,
        include_note: bool,
    ) -> str:
        if not isinstance(record.model, Figure):
            raise AssemblyError(f"{record.model.id} is not a figure object")

        self._register_object_files(record, role=relationship, include_note=include_note)
        self._register_figure_assets(record, role=relationship)
        if record.model.id != target.identifier or target.kind != "figure":
            self._register_edge(
                source_id=target.identifier,
                source_kind=target.kind,
                target_id=record.model.id,
                target_kind="figure",
                relationship=relationship,
            )
        self._observe_figure_use(
            record,
            target=target,
            relationship=relationship,
        )

        parts: list[str] = []
        if heading_level is not None:
            parts.extend(["#" * heading_level + f" {record.model.title[self.language]}", ""])
        if self.output_format in {"html", "revealjs", "slides-pdf"}:
            interactive = self.output_format == "html" and bool(record.model.interactive_path)
            parts.append(
                self._render_figure_html_block(
                    record,
                    interactive=interactive,
                )
            )
        else:
            parts.append(self._render_figure_print_block(record, target=target))
        if include_note:
            note_text = self._load_object_note(record)
            if note_text:
                parts.extend(["", note_text])
        return "\n".join(part.rstrip() for part in parts if part).rstrip()

    def _render_figure_html_block(self, record: IndexedObject, *, interactive: bool) -> str:
        svg_markup = self._load_figure_svg_markup(record)
        caption_label = "Caption" if self.language == "en" else "Bildetekst"
        interactive_marker = "true" if interactive else "false"
        parts = [
            (
                f'<div class="lf-figure-card" data-figure-id="{record.model.id}" '
                f'data-figure-interactive="{interactive_marker}">'
            ),
            '<div class="lf-figure-surface" data-figure-surface>',
            svg_markup,
            "</div>",
            (
                f'<p class="lf-figure-caption"><strong>{caption_label}:</strong> '
                f"{escape(record.model.caption[self.language])}</p>"
            ),
            "</div>",
        ]
        if interactive and record.model.interactive_path:
            script_path = record.directory / record.model.interactive_path
            script_text = script_path.read_text(encoding="utf-8").rstrip()
            if script_text.startswith("// @learnforge:requires d3") and not self._d3_inlined:
                d3_path = Path(__file__).parent / "web_assets" / "d3.min.js"
                d3_text = d3_path.read_text(encoding="utf-8").rstrip()
                parts.extend(["<script>", d3_text, "</script>"])
                self._d3_inlined = True
            parts.extend(["<script>", script_text, "</script>"])
        return "\n".join(parts)

    def _render_figure_print_block(self, record: IndexedObject, *, target: BuildTargetRef) -> str:
        image_path = record.directory / record.model.pdf_path
        relative_image = os.path.relpath(
            image_path,
            self._generated_path(target.output_category, target.identifier).parent,
        ).replace(os.sep, "/")
        caption = record.model.caption[self.language]
        alt_text = record.model.alt_text[self.language]
        return f'![{caption}]({relative_image}){{fig-alt="{alt_text}"}}'

    def _load_figure_svg_markup(self, record: IndexedObject) -> str:
        svg_path = record.directory / record.model.svg_path
        svg_markup = svg_path.read_text(encoding="utf-8").strip()
        title = escape(record.model.title[self.language])
        desc = escape(record.model.alt_text[self.language])
        if "<title" in svg_markup:
            svg_markup = re.sub(
                r"<title[^>]*>.*?</title>",
                f"<title>{title}</title>",
                svg_markup,
                count=1,
                flags=re.DOTALL,
            )
        else:
            svg_markup = re.sub(
                r"(<svg\b[^>]*>)",
                r"\1<title>" + title + "</title>",
                svg_markup,
                count=1,
            )
        if "<desc" in svg_markup:
            svg_markup = re.sub(
                r"<desc[^>]*>.*?</desc>",
                f"<desc>{desc}</desc>",
                svg_markup,
                count=1,
                flags=re.DOTALL,
            )
        else:
            svg_markup = re.sub(
                r"(<svg\b[^>]*>)",
                r"\1<desc>" + desc + "</desc>",
                svg_markup,
                count=1,
            )
        return svg_markup.replace("<svg ", '<svg class="lf-figure-svg" ', 1)

    def _register_figure_assets(self, record: IndexedObject, *, role: str) -> None:
        if not isinstance(record.model, Figure):
            return
        for asset in record.model.asset_inventory:
            self._register_file(record.directory / asset, role=f"{role}-figure-asset")

    def _observe_figure_use(
        self,
        record: IndexedObject,
        *,
        target: BuildTargetRef,
        relationship: str,
    ) -> None:
        if not isinstance(record.model, Figure):
            return
        svg_source_path = str((record.directory / record.model.svg_path).relative_to(self.root))
        pdf_source_path = str((record.directory / record.model.pdf_path).relative_to(self.root))
        interactive_source_path = (
            str((record.directory / record.model.interactive_path).relative_to(self.root))
            if record.model.interactive_path
            else None
        )
        d3_included = False
        if self.output_format == "html" and record.model.interactive_path:
            js_path = record.directory / record.model.interactive_path
            if js_path.exists():
                first_line = js_path.read_text(encoding="utf-8").split("\n", 1)[0]
                d3_included = first_line.startswith("// @learnforge:requires d3")
        self.figure_observations.append(
            FigureObservation(
                figure_id=record.model.id,
                context_target_id=target.identifier,
                context_target_kind=target.kind,
                relationship=relationship,
                svg_source_path=svg_source_path,
                pdf_source_path=pdf_source_path,
                interactive_source_path=interactive_source_path,
                asset_inventory=[
                    str((record.directory / asset).relative_to(self.root))
                    for asset in record.model.asset_inventory
                ],
                interactive_included=(
                    self.output_format == "html" and bool(record.model.interactive_path)
                ),
                fallback_asset_path=str(
                    (
                        record.directory
                        / (
                            record.model.pdf_path
                            if self.output_format in {"pdf", "handout", "exercise-sheet"}
                            else record.model.svg_path
                        )
                    ).relative_to(self.root)
                ),
                d3_included=d3_included,
            )
        )

    def _assignment_source_set(
        self,
        record: IndexedObject,
        *,
        current_output: Path,
        include_notes: bool,
        observe_solutions: bool,
    ) -> AssignmentSourceSet:
        exercise_records: list[IndexedObject] = []
        listing_entries: list[ListingEntry] = []
        total_minutes = 0
        concept_ids: list[str] = []
        topic_ids: list[str] = []

        for item_id in record.model.items:
            item_record = self.index.objects[item_id]
            if not isinstance(item_record.model, Exercise):
                raise AssemblyError(
                    f"assignment collection {record.model.id} may only include exercises: {item_id}"
                )
            if self._exclude_from_audience(item_record.model.visibility):
                continue
            self._ensure_language(item_record.model.languages, item_id)
            if "exercise-sheet" not in item_record.model.outputs:
                raise AssemblyError(f"{item_id} does not support exercise-sheet builds")
            self._register_edge(
                source_id=record.model.id,
                source_kind="collection",
                target_id=item_record.model.id,
                target_kind="exercise",
                relationship="assignment-item",
            )
            self._register_object_files(
                item_record,
                role="assignment-item",
                include_note=include_notes,
            )
            if observe_solutions:
                self._load_exercise_solution(item_record, include_solution=False)
            exercise_records.append(item_record)
            total_minutes += item_record.model.estimated_time_minutes
            concept_ids.extend(item_record.model.concepts)
            topic_ids.extend(item_record.model.topics)
            listing_entries.append(
                ListingEntry(
                    identifier=item_record.model.id,
                    kind="exercise",
                    title=item_record.model.title[self.language],
                    description=localized_minutes(
                        item_record.model.estimated_time_minutes,
                        self.language,
                    ),
                    href=self._page_href(
                        current_output=current_output,
                        target_kind="exercise",
                        target_id=item_record.model.id,
                    ),
                )
            )

        if not exercise_records:
            raise AssemblyError(f"assignment collection {record.model.id} has no visible exercises")

        return AssignmentSourceSet(
            exercises=exercise_records,
            listing_entries=listing_entries,
            total_minutes=total_minutes,
            concept_ids=sorted(dict.fromkeys(concept_ids)),
            topic_ids=sorted(dict.fromkeys(topic_ids)),
        )

    def _assignment_listing_description(self, source_set: AssignmentSourceSet) -> str:
        exercise_count = len(source_set.exercises)
        exercise_label = "exercises" if self.language == "en" else "oppgaver"
        time_label = localized_minutes(source_set.total_minutes, self.language)
        return f"{exercise_count} {exercise_label}, {time_label}"

    def _render_assignment_page_summary(
        self,
        *,
        record: IndexedObject,
        source_set: AssignmentSourceSet,
        current_output: Path,
    ) -> str:
        lines = [
            "## Assignment details" if self.language == "en" else "## Oppgavearkdetaljer",
            "",
            f"- {('Exercises' if self.language == 'en' else 'Oppgaver')}: "
            f"{len(source_set.exercises)}",
            (
                f"- {('Estimated time' if self.language == 'en' else 'Estimert tid')}: "
                f"{localized_minutes(source_set.total_minutes, self.language)}"
            ),
            (
                f"- {('Outputs' if self.language == 'en' else 'Utdata')}: "
                f"{', '.join(self._output_label(output) for output in record.model.outputs)}"
            ),
        ]
        course_links = self._course_links(record.model.courses, "collection", record.model.id)
        if course_links:
            lines.append(
                f"- {('Course suitability' if self.language == 'en' else 'Passer for kurs')}: "
                f"{', '.join(course_links)}"
            )
        if source_set.concept_ids:
            concept_links = [
                self._render_link(
                    concept_id,
                    "concept",
                    self.index.objects[concept_id].model.title[self.language],
                    current_output,
                )
                for concept_id in source_set.concept_ids
                if concept_id in self.index.objects
                and self._is_listable(
                    self.index.objects[concept_id],
                    require_output_format="html",
                )
            ]
            if concept_links:
                lines.append(
                    f"- {('Linked concepts' if self.language == 'en' else 'Knyttede begreper')}: "
                    f"{', '.join(concept_links)}"
                )

        export_links = self._available_export_links(
            target=BuildTargetRef(
                identifier=record.model.id,
                kind="collection",
                output_category="collection",
                title=record.model.title[self.language],
            ),
            current_output=current_output,
        )
        if export_links:
            lines.extend(
                [
                    "",
                    "## Available outputs" if self.language == "en" else "## Tilgjengelige utdata",
                    "",
                    *[f"- {link}" for link in export_links],
                ]
            )
        return "\n".join(lines)

    def _render_assignment_sheet_summary(
        self,
        *,
        record: IndexedObject,
        exercises: list[IndexedObject],
        total_minutes: int,
        concept_ids: list[str],
        include_solutions: bool,
    ) -> str:
        heading = (
            "## Teacher solution sheet" if include_solutions and self.language == "en" else None
        )
        if include_solutions and self.language == "nb":
            heading = "## Løsningsark for lærer"
        if not include_solutions and self.language == "en":
            heading = "## Exercise sheet"
        if not include_solutions and self.language == "nb":
            heading = "## Øvingsark"

        lines = [heading, ""]
        if include_solutions:
            lines.append(
                "For teacher use only. This version includes solution material that is excluded "
                "from student builds."
                if self.language == "en"
                else "Kun for lærerbruk. Denne versjonen inkluderer løsningsmateriale som er "
                "utelatt fra studentbyggen."
            )
        else:
            lines.append(
                "Student-facing compiled sheet assembled from reusable exercise objects."
                if self.language == "en"
                else "Studentvendt kompilert ark satt sammen av gjenbrukbare oppgaveobjekter."
            )
        lines.extend(
            [
                "",
                f"- {('Exercises' if self.language == 'en' else 'Oppgaver')}: {len(exercises)}",
                f"- {('Estimated time' if self.language == 'en' else 'Estimert tid')}: "
                f"{localized_minutes(total_minutes, self.language)}",
            ]
        )
        concept_links = [
            self._render_link(
                concept_id,
                "concept",
                self.index.objects[concept_id].model.title[self.language],
                self._planned_output_path("collection", record.model.id),
            )
            for concept_id in concept_ids
            if concept_id in self.index.objects
            and self._is_listable(self.index.objects[concept_id], require_output_format="html")
        ]
        if concept_links:
            lines.append(
                f"- {('Linked concepts' if self.language == 'en' else 'Knyttede begreper')}: "
                f"{', '.join(concept_links)}"
            )
        course_links = self._course_links(record.model.courses, "collection", record.model.id)
        if course_links:
            lines.append(
                f"- {('Course suitability' if self.language == 'en' else 'Passer for kurs')}: "
                f"{', '.join(course_links)}"
            )
        return "\n".join(lines)

    def _render_assignment_exercise_section(
        self,
        record: IndexedObject,
        *,
        number: int,
        include_solution: bool,
    ) -> str:
        lines = [
            (
                f"## Exercise {number}: {record.model.title[self.language]}"
                if self.language == "en"
                else f"## Oppgave {number}: {record.model.title[self.language]}"
            ),
            "",
            f"- {('Type' if self.language == 'en' else 'Type')}: {record.model.exercise_type}",
            (
                f"- {('Difficulty' if self.language == 'en' else 'Vanskelighetsgrad')}: "
                f"{record.model.difficulty}"
            ),
            (
                f"- {('Estimated time' if self.language == 'en' else 'Estimert tid')}: "
                f"{localized_minutes(record.model.estimated_time_minutes, self.language)}"
            ),
            "",
            self._load_object_note(record),
        ]
        solution_block = self._render_exercise_solution_block(
            record,
            heading_level=3,
            include_solution=include_solution,
        )
        if solution_block:
            lines.extend(["", solution_block])
        return "\n".join(lines).rstrip()

    def _render_exercise_solution_for_page(self, record: IndexedObject) -> str:
        return self._render_exercise_solution_block(
            record,
            heading_level=2,
            include_solution=self.audience == "teacher",
        )

    def _render_exercise_solution_block(
        self,
        record: IndexedObject,
        *,
        heading_level: int,
        include_solution: bool,
    ) -> str:
        solution_text = self._load_exercise_solution(record, include_solution=include_solution)
        if not solution_text:
            return ""
        heading_prefix = "#" * heading_level
        heading = "Solution" if self.language == "en" else "Losning"
        return "\n".join(
            [
                f"::: {{.{SOLUTION_BLOCK_MARKER}}}",
                f"{heading_prefix} {heading}",
                "",
                solution_text.rstrip(),
                ":::",
            ]
        )

    def _render_resource_summary(self, record: IndexedObject) -> str:
        why_label = "Why this matters" if self.language == "en" else "Hvorfor dette er nyttig"
        summary_label = "Summary" if self.language == "en" else "Sammendrag"
        heading = "## Resource details" if self.language == "en" else "## Ressursdetaljer"
        items = [
            (
                f"- {('Workflow state' if self.language == 'en' else 'Arbeidsflytstatus')}: "
                f"{record.model.status}"
            ),
            f"- {('Type' if self.language == 'en' else 'Type')}: {record.model.resource_kind}",
            (
                f"- {('Authors' if self.language == 'en' else 'Forfattere')}: "
                f"{', '.join(record.model.authors)}"
            ),
            (
                f"- {('Published' if self.language == 'en' else 'Publisert')}: "
                f"{record.model.published_on.isoformat()}"
            ),
            (
                f"- {('Time' if self.language == 'en' else 'Tid')}: "
                f"{localized_minutes(record.model.estimated_time_minutes, self.language)}"
            ),
            f"- {summary_label}: {record.model.summary.get(self.language, '')}",
            f"- {why_label}: {record.model.why_selected.get(self.language, '')}",
        ]
        open_label = "Open resource" if self.language == "en" else "Apne ressurs"
        if self.output_format == "html":
            items.append(
                f'- <a href="{record.model.url}" class="lf-resource-open" '
                f'target="_blank" rel="noopener">{open_label}</a>'
            )
        else:
            items.append(f"- {open_label}: [{record.model.url}]({record.model.url})")
        if record.model.review_after is not None:
            items.append(
                f"- {('Review after' if self.language == 'en' else 'Revurder etter')}: "
                f"{record.model.review_after.isoformat()}"
            )
        if self.audience == "teacher":
            stale_label = "yes" if self.language == "en" else "ja"
            fresh_label = "no" if self.language == "en" else "nei"
            instructor_label = "Instructor note" if self.language == "en" else "Faglærermerknad"
            approval_history_label = (
                "Approval history" if self.language == "en" else "Godkjenningshistorikk"
            )
            items.extend(
                [
                    (
                        f"- {instructor_label}: "
                        f"{record.model.instructor_note.get(self.language, '')}"
                    ),
                    (
                        f"- {('Stale' if self.language == 'en' else 'Utlopt')}: "
                        f"{stale_label if resource_is_stale(record.model) else fresh_label}"
                    ),
                ]
            )
            if record.model.approval_history:
                history_entries = ", ".join(
                    f"{item.action}:{item.by}@{item.acted_on.isoformat()}"
                    for item in record.model.approval_history
                )
                items.append(f"- {approval_history_label}: {history_entries}")
            if record.model.ai.source or record.model.ai.generated_fields:
                items.append(
                    f"- {('AI provenance' if self.language == 'en' else 'AI-opphav')}: "
                    f"{record.model.ai.source or 'unknown'}"
                )
        topic_links = self._topic_links(record, current_kind="resource")
        if topic_links:
            items.append(
                f"- {('Topics' if self.language == 'en' else 'Temaer')}: {', '.join(topic_links)}"
            )
        course_links = self._course_links(record.model.courses, record.model.kind, record.model.id)
        if course_links:
            items.append(
                f"- {('Courses' if self.language == 'en' else 'Kurs')}: {', '.join(course_links)}"
            )
        if self.output_format == "html":
            inner = "\n".join(items)
            return f'{heading}\n\n<div class="lf-meta-panel">\n\n{inner}\n\n</div>'
        return "\n".join([heading, "", *items])

    def _resource_inbox_description(self, record: IndexedObject) -> str:
        summary = record.model.summary.get(self.language) or record.model.why_selected.get(
            self.language,
            "",
        )
        descriptors = [
            f"state={record.model.status}",
            f"courses={','.join(record.model.courses) or '-'}",
            f"topics={','.join(record.model.topics) or '-'}",
        ]
        if resource_is_stale(record.model):
            descriptors.append("stale=yes")
        if record.model.ai.source:
            descriptors.append(f"ai={record.model.ai.source}")
        if summary:
            descriptors.append(summary)
        return "; ".join(descriptors)

    def _render_collection_summary(self, record: IndexedObject) -> str:
        current_output = self._planned_output_path("collection", record.model.id)
        entries = [
            ListingEntry(
                identifier=item_record.model.id,
                kind=item_record.model.kind,
                title=item_record.model.title[self.language],
                description=", ".join(item_record.model.topics),
                href=self._page_href(
                    current_output=current_output,
                    target_kind=item_record.model.kind,
                    target_id=item_record.model.id,
                ),
            )
            for item_record in [self.index.objects[item_id] for item_id in record.model.items]
            if self._is_listable(item_record, require_output_format="html")
        ]
        return self._render_listing_section(
            title="This lecture includes"
            if self.language == "en"
            else "Denne forelesningen inkluderer",
            entries=entries,
        )

    def _assignment_concept_entries(
        self,
        record: IndexedObject,
        *,
        concept_ids: list[str],
        current_output: Path,
    ) -> list[RelatedEntry]:
        entries: list[RelatedEntry] = []
        for concept_id in concept_ids:
            concept_record = self.index.objects.get(concept_id)
            if concept_record is None or not self._is_listable(
                concept_record,
                require_output_format="html",
            ):
                continue
            self._register_object_files(
                concept_record,
                role="assignment-concept",
                include_note=False,
            )
            self._register_edge(
                source_id=record.model.id,
                source_kind="collection",
                target_id=concept_id,
                target_kind="concept",
                relationship="assignment-concept",
            )
            entries.append(
                RelatedEntry(
                    identifier=concept_id,
                    kind="concept",
                    title=concept_record.model.title[self.language],
                    relationship="assignment-concept",
                    href=self._page_href(
                        current_output=current_output,
                        target_kind="concept",
                        target_id=concept_id,
                    ),
                )
            )
        return entries

    def _assignment_resource_entries(
        self,
        record: IndexedObject,
        *,
        topic_ids: list[str],
        current_output: Path,
    ) -> list[RelatedEntry]:
        candidates: list[tuple[int, IndexedObject]] = []
        for item in self.index.objects.values():
            if not isinstance(item.model, Resource) or not self._is_listable(
                item,
                require_output_format="html",
            ):
                continue
            if not set(record.model.courses) & set(item.model.courses):
                continue
            shared_topics = sorted(set(topic_ids) & set(item.model.topics))
            if not shared_topics:
                continue
            shared_courses = set(record.model.courses) & set(item.model.courses)
            score = len(shared_topics) * 100 + len(shared_courses) * 10
            candidates.append((score, item))

        entries: list[RelatedEntry] = []
        for _, item in sorted(candidates, key=lambda value: (-value[0], value[1].model.id))[:5]:
            self._register_object_files(item, role="assignment-resource", include_note=False)
            self._register_edge(
                source_id=record.model.id,
                source_kind="collection",
                target_id=item.model.id,
                target_kind="resource",
                relationship="assignment-resource",
            )
            entries.append(
                RelatedEntry(
                    identifier=item.model.id,
                    kind="resource",
                    title=item.model.title[self.language],
                    relationship="assignment-resource",
                    href=self._page_href(
                        current_output=current_output,
                        target_kind="resource",
                        target_id=item.model.id,
                    ),
                )
            )
        return entries

    def _course_related_entries_for_record(self, record: IndexedObject) -> list[RelatedEntry]:
        entries: list[RelatedEntry] = []
        current_output = self._planned_output_path(
            output_category_for_kind(
                record.model.kind if not isinstance(record.model, Collection) else "collection"
            ),
            record.model.id,
        )
        for course_id in sorted(set(record.model.courses)):
            course_record = self.index.courses.get(course_id)
            if course_record is None or self.language not in course_record.model.languages:
                continue
            self._register_file(course_record.course_path, role="related-course")
            self._register_edge(
                source_id=record.model.id,
                source_kind=record.model.kind,
                target_id=course_id,
                target_kind="course",
                relationship="used-in-course",
            )
            entries.append(
                RelatedEntry(
                    identifier=course_record.model.id,
                    kind="course",
                    title=course_record.model.title[self.language],
                    relationship="used-in-course",
                    href=self._page_href(
                        current_output=current_output,
                        target_kind="course",
                        target_id=course_id,
                    ),
                )
            )
        return entries

    def _related_course_entries_for_topic(self, topic: str) -> list[RelatedEntry]:
        course_ids = sorted(
            {
                course_id
                for record in self.index.objects.values()
                if topic in record.model.topics and self._is_listable(record)
                for course_id in record.model.courses
            }
        )
        current_output = self._planned_output_path("listing", f"{TOPIC_TARGET_PREFIX}{topic}")
        entries: list[RelatedEntry] = []
        for course_id in course_ids:
            course_record = self.index.courses.get(course_id)
            if course_record is None or self.language not in course_record.model.languages:
                continue
            entries.append(
                RelatedEntry(
                    identifier=course_id,
                    kind="course",
                    title=course_record.model.title[self.language],
                    relationship="topic-course",
                    href=self._page_href(
                        current_output=current_output,
                        target_kind="course",
                        target_id=course_id,
                    ),
                )
            )
        return entries

    def _course_links(self, course_ids: list[str], current_kind: str, current_id: str) -> list[str]:
        current_output = self._planned_output_path(
            output_category_for_kind(current_kind), current_id
        )
        links: list[str] = []
        for course_id in course_ids:
            course_record = self.index.courses.get(course_id)
            if course_record is None or self.language not in course_record.model.languages:
                continue
            href = self._page_href(
                current_output=current_output,
                target_kind="course",
                target_id=course_id,
            )
            if href:
                links.append(f"[{course_record.model.title[self.language]}]({href})")
            else:
                links.append(course_record.model.title[self.language])
        return links

    def _topic_links(self, record: IndexedObject, *, current_kind: str) -> list[str]:
        current_output = self._planned_output_path(record.model.kind, record.model.id)
        links: list[str] = []
        for topic in record.model.topics:
            listing_id = f"{TOPIC_TARGET_PREFIX}{topic}"
            href = self._page_href(
                current_output=current_output,
                target_kind="topic-listing",
                target_id=listing_id,
            )
            if href:
                links.append(f"[{humanize_slug(topic)}]({href})")
        return links

    def _listing_lines(self, entries: list[ListingEntry], *, empty_message: str) -> list[str]:
        if not entries:
            return [empty_message]
        if self.output_format == "html":
            return self._listing_cards(entries)
        lines: list[str] = []
        for entry in entries:
            if entry.description:
                lines.append(f"- {entry.title} - {entry.description}")
            else:
                lines.append(f"- {entry.title}")
        return lines

    def _listing_cards(self, entries: list[ListingEntry]) -> list[str]:
        cards: list[str] = []
        for entry in entries:
            kind_label = self._kind_label(entry.kind, entry.identifier)
            link = (
                f'<a href="{entry.href}" class="lf-listing-link">{escape(entry.title)}</a>'
                if entry.href
                else f'<span class="lf-listing-link">{escape(entry.title)}</span>'
            )
            badge = f'<span class="lf-listing-badge">{escape(kind_label.lower())}</span>'
            desc = (
                f'<p class="lf-listing-desc">{escape(entry.description)}</p>'
                if entry.description
                else ""
            )
            cards.append(f'<div class="lf-listing-card">{link} {badge}{desc}</div>')
        return cards

    def _course_objects(self, course_id: str) -> list[IndexedObject]:
        return [
            record
            for record in self.index.objects.values()
            if course_id in record.model.courses and self._is_listable(record)
        ]

    def _related_entries_for_object(self, record: IndexedObject) -> list[RelatedEntry]:
        if record.model.kind == "concept":
            return self._related_entries_for_concept(record)
        if record.model.kind == "exercise":
            return self._related_entries_for_exercise(record)
        if record.model.kind == "resource":
            return self._related_entries_for_resource(record)
        return []

    def _assignment_related_entries_for_object(self, record: IndexedObject) -> list[RelatedEntry]:
        if record.model.kind == "exercise":
            return self._assignment_entries_for_exercise(record)
        if record.model.kind == "concept":
            return self._assignment_entries_for_concept(record)
        return []

    def _assignment_entries_for_exercise(self, record: IndexedObject) -> list[RelatedEntry]:
        current_output = self._planned_output_path(record.model.kind, record.model.id)
        entries: list[RelatedEntry] = []
        for item in sorted(self.index.objects.values(), key=lambda value: value.model.id):
            if not (
                isinstance(item.model, Collection)
                and item.model.collection_kind == "assignment"
                and record.model.id in item.model.items
                and self._is_listable(item, require_output_format="html")
            ):
                continue
            self._register_object_files(item, role="assignment-context", include_note=False)
            self._register_edge(
                source_id=record.model.id,
                source_kind="exercise",
                target_id=item.model.id,
                target_kind="collection",
                relationship="used-in-assignment",
            )
            entries.append(
                RelatedEntry(
                    identifier=item.model.id,
                    kind="collection",
                    title=item.model.title[self.language],
                    relationship="used-in-assignment",
                    href=self._page_href(
                        current_output=current_output,
                        target_kind="collection",
                        target_id=item.model.id,
                    ),
                )
            )
        return entries

    def _assignment_entries_for_concept(self, record: IndexedObject) -> list[RelatedEntry]:
        current_output = self._planned_output_path(record.model.kind, record.model.id)
        entries: list[RelatedEntry] = []
        for item in sorted(self.index.objects.values(), key=lambda value: value.model.id):
            if not (
                isinstance(item.model, Collection)
                and item.model.collection_kind == "assignment"
                and self._is_listable(item, require_output_format="html")
            ):
                continue
            supports_concept = any(
                exercise_id in self.index.objects
                and isinstance(self.index.objects[exercise_id].model, Exercise)
                and record.model.id in self.index.objects[exercise_id].model.concepts
                for exercise_id in item.model.items
            )
            if not supports_concept:
                continue
            self._register_object_files(item, role="assignment-context", include_note=False)
            self._register_edge(
                source_id=record.model.id,
                source_kind="concept",
                target_id=item.model.id,
                target_kind="collection",
                relationship="used-in-assignment",
            )
            entries.append(
                RelatedEntry(
                    identifier=item.model.id,
                    kind="collection",
                    title=item.model.title[self.language],
                    relationship="used-in-assignment",
                    href=self._page_href(
                        current_output=current_output,
                        target_kind="collection",
                        target_id=item.model.id,
                    ),
                )
            )
        return entries

    def _related_entries_for_concept(self, record: IndexedObject) -> list[RelatedEntry]:
        entries: list[RelatedEntry] = []
        seen_ids: set[str] = set()
        for related_id in record.model.related:
            related_record = self.index.objects.get(related_id)
            if related_record is None or not self._is_listable(
                related_record, require_output_format="html"
            ):
                continue
            seen_ids.add(related_id)
            self._register_object_files(related_record, role="related-content", include_note=False)
            self._register_edge(
                source_id=record.model.id,
                source_kind="concept",
                target_id=related_record.model.id,
                target_kind=related_record.model.kind,
                relationship="explicit-related",
            )
            entries.append(
                RelatedEntry(
                    identifier=related_record.model.id,
                    kind=related_record.model.kind,
                    title=related_record.model.title[self.language],
                    relationship="explicit-related",
                    href=self._page_href(
                        current_output=self._planned_output_path(
                            record.model.kind,
                            record.model.id,
                        ),
                        target_kind=related_record.model.kind,
                        target_id=related_record.model.id,
                    ),
                )
            )

        collections = [
            item
            for item in self.index.objects.values()
            if isinstance(item.model, Collection)
            and record.model.id in item.model.items
            and self._is_listable(item, require_output_format="html")
        ]
        for collection_record in sorted(collections, key=lambda item: item.model.id):
            if collection_record.model.id in seen_ids:
                continue
            self._register_object_files(
                collection_record,
                role="used-in-collection",
                include_note=False,
            )
            self._register_edge(
                source_id=record.model.id,
                source_kind="concept",
                target_id=collection_record.model.id,
                target_kind="collection",
                relationship="used-in-collection",
            )
            entries.append(
                RelatedEntry(
                    identifier=collection_record.model.id,
                    kind="collection",
                    title=collection_record.model.title[self.language],
                    relationship="used-in-collection",
                    href=self._page_href(
                        current_output=self._planned_output_path(
                            record.model.kind,
                            record.model.id,
                        ),
                        target_kind="collection",
                        target_id=collection_record.model.id,
                    ),
                )
            )
        return entries

    def _related_entries_for_exercise(self, record: IndexedObject) -> list[RelatedEntry]:
        entries: list[RelatedEntry] = []
        current_output = self._planned_output_path(record.model.kind, record.model.id)

        for concept_id in record.model.concepts:
            concept_record = self.index.objects.get(concept_id)
            if concept_record is None or not self._is_listable(
                concept_record, require_output_format="html"
            ):
                continue
            self._register_object_files(concept_record, role="related-content", include_note=False)
            self._register_edge(
                source_id=record.model.id,
                source_kind="exercise",
                target_id=concept_record.model.id,
                target_kind="concept",
                relationship="exercise-concept",
            )
            entries.append(
                RelatedEntry(
                    identifier=concept_record.model.id,
                    kind="concept",
                    title=concept_record.model.title[self.language],
                    relationship="exercise-concept",
                    href=self._page_href(
                        current_output=current_output,
                        target_kind="concept",
                        target_id=concept_record.model.id,
                    ),
                )
            )

        for item in sorted(self.index.objects.values(), key=lambda value: value.model.id):
            if (
                isinstance(item.model, Collection)
                and item.model.collection_kind != "assignment"
                and record.model.id in item.model.items
                and self._is_listable(item, require_output_format="html")
            ):
                self._register_object_files(item, role="related-content", include_note=False)
                self._register_edge(
                    source_id=record.model.id,
                    source_kind="exercise",
                    target_id=item.model.id,
                    target_kind="collection",
                    relationship="used-in-collection",
                )
                entries.append(
                    RelatedEntry(
                        identifier=item.model.id,
                        kind="collection",
                        title=item.model.title[self.language],
                        relationship="used-in-collection",
                        href=self._page_href(
                            current_output=current_output,
                            target_kind="collection",
                            target_id=item.model.id,
                        ),
                    )
                )
        return entries

    def _related_entries_for_resource(self, record: IndexedObject) -> list[RelatedEntry]:
        candidates: list[tuple[int, IndexedObject]] = []
        for item in self.index.objects.values():
            if item.model.id == record.model.id or not self._is_listable(
                item, require_output_format="html"
            ):
                continue
            shared_topics = sorted(set(record.model.topics) & set(item.model.topics))
            shared_courses = sorted(set(record.model.courses) & set(item.model.courses))
            score = len(shared_topics) * 100 + len(shared_courses) * 10
            if score == 0:
                continue
            candidates.append((score, item))

        entries: list[RelatedEntry] = []
        for _, item in sorted(
            candidates,
            key=lambda value: (
                -value[0],
                KIND_SORT_ORDER.get(
                    value[1].model.kind
                    if not isinstance(value[1].model, Collection)
                    else "collection",
                    99,
                ),
                value[1].model.id,
            ),
        )[:5]:
            kind = item.model.kind if not isinstance(item.model, Collection) else "collection"
            self._register_object_files(item, role="related-content", include_note=False)
            self._register_edge(
                source_id=record.model.id,
                source_kind="resource",
                target_id=item.model.id,
                target_kind=kind,
                relationship="shared-topics-or-courses",
            )
            entries.append(
                RelatedEntry(
                    identifier=item.model.id,
                    kind=kind,
                    title=item.model.title[self.language],
                    relationship="shared-topics-or-courses",
                    href=self._page_href(
                        current_output=self._planned_output_path(
                            record.model.kind,
                            record.model.id,
                        ),
                        target_kind=kind,
                        target_id=item.model.id,
                    ),
                )
            )
        return entries

    def _render_related_section(self, *, title: str, entries: list[RelatedEntry]) -> str:
        if self.output_format == "html":
            return self._render_html_listing_section(
                title=title,
                entries=[
                    ListingEntry(
                        identifier=entry.identifier,
                        kind=entry.kind,
                        title=entry.title,
                        description="",
                        href=entry.href,
                    )
                    for entry in entries
                ],
            )
        lines = [f"## {title}", ""]
        for entry in entries:
            kind_label = self._kind_label(entry.kind, entry.identifier)
            target_text = (
                f"[{entry.title}]({entry.href})"
                if self.output_format == "html" and entry.href
                else entry.title
            )
            lines.append(f"- {target_text} [{kind_label.lower()}]")
        return "\n".join(lines)

    def _kind_label(self, kind: str, identifier: str) -> str:
        if kind == "collection":
            record = self.index.objects.get(identifier)
            if record is not None and isinstance(record.model, Collection):
                labels = {
                    "lecture": "Lecture" if self.language == "en" else "Forelesning",
                    "assignment": "Assignment" if self.language == "en" else "Oppgaveark",
                    "module": "Module" if self.language == "en" else "Modul",
                    "reading-list": "Reading list" if self.language == "en" else "Leseliste",
                }
                return labels.get(record.model.collection_kind, "Collection")
        return KIND_LABELS.get(kind, kind.title())

    def _render_listing_section(
        self,
        *,
        title: str,
        entries: list[ListingEntry],
        suffix: str = "",
    ) -> str:
        if self.output_format == "html":
            return self._render_html_listing_section(
                title=title,
                entries=entries,
                suffix=suffix,
            )
        lines = [f"## {title}", ""]
        if not entries:
            lines.append("No entries.")
        else:
            for entry in entries:
                if entry.description:
                    lines.append(f"- {entry.title} - {entry.description}")
                else:
                    lines.append(f"- {entry.title}")
        if suffix:
            lines.extend(["", suffix])
        return "\n".join(lines)

    def _render_listing_page(
        self,
        *,
        title: str,
        entries: list[ListingEntry],
        group_by_kind: bool,
        intro: str = "",
    ) -> str:
        lines = [title, ""]
        if intro:
            lines.extend([intro, ""])
        if group_by_kind:
            grouped: dict[str, list[ListingEntry]] = {}
            for entry in entries:
                grouped.setdefault(entry.kind, []).append(entry)
            for kind in sorted(grouped, key=lambda item: KIND_SORT_ORDER.get(item, 99)):
                if self.output_format == "html":
                    lines.extend(
                        [
                            self._render_html_listing_section(
                                title=f"{KIND_LABELS.get(kind, kind.title())}s",
                                entries=grouped[kind],
                            ),
                            "",
                        ]
                    )
                else:
                    lines.append(f"## {KIND_LABELS.get(kind, kind.title())}s")
                    lines.append("")
                    for entry in grouped[kind]:
                        if entry.description:
                            lines.append(f"- {entry.title} - {entry.description}")
                        else:
                            lines.append(f"- {entry.title}")
                lines.append("")
            return "\n".join(lines).rstrip()

        if self.output_format == "html":
            lines.append(self._render_html_listing_section(title=None, entries=entries))
        else:
            for entry in entries:
                lines.append(f"- {entry.title} - {entry.description}")
        return "\n".join(lines).rstrip()

    def _render_html_listing_section(
        self,
        *,
        title: str | None,
        entries: list[ListingEntry],
        suffix: str = "",
        empty_message: str = "No entries.",
    ) -> str:
        parts = ['<section class="lf-section lf-section--listing">']
        if title or suffix:
            parts.append('<div class="lf-section-header">')
            if title:
                parts.append(f"<h2>{escape(title)}</h2>")
            if suffix:
                parts.append(f'<p class="lf-section-actions">{suffix}</p>')
            parts.append("</div>")

        if entries:
            parts.append('<div class="lf-card-grid">')
            parts.extend(self._listing_cards(entries))
            parts.append("</div>")
        else:
            parts.append(f'<p class="lf-empty-state">{escape(empty_message)}</p>')

        parts.append("</section>")
        return "\n".join(parts)

    def _register_object_files(
        self,
        record: IndexedObject,
        *,
        role: str,
        include_note: bool,
    ) -> None:
        self._register_file(record.meta_path, role=role)
        if include_note and not isinstance(record.model, Collection):
            self._register_file(record.note_path(self.language), role=role)

    def _register_file(self, path: Path, *, role: str) -> None:
        relative_path = str(path.relative_to(self.root))
        key = (relative_path, role)
        if key in self.file_dependencies:
            return
        self.file_dependencies[key] = FileDependency(
            path=relative_path,
            role=role,
            sha256=sha256_file(path),
        )

    def _register_edge(
        self,
        *,
        source_id: str,
        source_kind: str,
        target_id: str,
        target_kind: str,
        relationship: str,
    ) -> None:
        edge = DependencyEdge(
            source_id=source_id,
            source_kind=source_kind,
            target_id=target_id,
            target_kind=target_kind,
            relationship=relationship,
        )
        if edge not in self.dependency_edges:
            self.dependency_edges.append(edge)

    def _load_object_note(self, record: IndexedObject) -> str:
        note_path = record.note_path(self.language)
        raw = note_path.read_text(encoding="utf-8")
        rewritten = rewrite_relative_links(
            raw,
            note_path.parent,
            self._generated_path(
                record.model.kind if not isinstance(record.model, Collection) else "collection",
                record.model.id,
            ),
        )
        return self._strip_visibility_blocks(rewritten, note_path).rstrip()

    def _load_exercise_solution(
        self,
        record: IndexedObject,
        *,
        include_solution: bool,
    ) -> str:
        if not isinstance(record.model, Exercise):
            return ""

        solution_path = record.solution_path(self.language)
        if not solution_path.exists():
            if include_solution and record.model.solution_visibility == "teacher":
                raise AssemblyError(
                    f"missing solution file for {record.model.id} in {self.language}"
                )
            return ""

        if include_solution and record.model.solution_visibility == "teacher":
            self._register_file(solution_path, role="exercise-solution")
            self.solution_observations.append(
                SolutionObservation(
                    exercise_id=record.model.id,
                    source_path=str(solution_path.relative_to(self.root)),
                    visibility=record.model.solution_visibility,
                    included_in_output=True,
                    reason="teacher-output-includes-solution",
                )
            )
            raw = solution_path.read_text(encoding="utf-8")
            rewritten = rewrite_relative_links(
                raw,
                solution_path.parent,
                self._generated_path(record.model.kind, record.model.id),
            )
            return self._strip_visibility_blocks(rewritten, solution_path).rstrip()

        reason = (
            "private-solution-remains-hidden"
            if record.model.solution_visibility == "private"
            else "student-output-excludes-solution"
        )
        self.solution_observations.append(
            SolutionObservation(
                exercise_id=record.model.id,
                source_path=str(solution_path.relative_to(self.root)),
                visibility=record.model.solution_visibility,
                included_in_output=False,
                reason=reason,
            )
        )
        return ""

    def _strip_visibility_blocks(self, content: str, source_path: Path) -> str:
        teacher_found = len(TEACHER_BLOCK_RE.findall(content))
        student_found = len(STUDENT_BLOCK_RE.findall(content))
        processed = content
        teacher_removed = 0
        student_removed = 0
        if self.audience == "student":
            processed, teacher_removed = TEACHER_BLOCK_RE.subn("\n", processed)
        elif self.audience == "teacher":
            processed, student_removed = STUDENT_BLOCK_RE.subn("\n", processed)

        self.leakage_observations.append(
            LeakageObservation(
                source_path=str(source_path.relative_to(self.root)),
                teacher_blocks_found=teacher_found,
                teacher_blocks_removed=teacher_removed,
                student_blocks_found=student_found,
                student_blocks_removed=student_removed,
            )
        )
        return processed

    def _ensure_visibility(self, visibility: str, identifier: str) -> None:
        if self._exclude_from_audience(visibility):
            raise AssemblyError(f"{identifier} is not {self.audience}-visible")

    def _ensure_language(self, languages: list[str], identifier: str) -> None:
        translation_status: dict[str, str] = {}
        if identifier in self.index.objects:
            translation_status = self.index.objects[identifier].model.translation_status
        if not self._language_available(languages, translation_status, self.language):
            raise AssemblyError(f"{identifier} does not support language {self.language}")

    def _ensure_output_supported(self, outputs: list[str], identifier: str) -> None:
        if self.output_format == "slides-pdf" and "revealjs" in outputs:
            return
        if self.output_format not in outputs:
            raise AssemblyError(f"{identifier} does not support format {self.output_format}")

    def _exclude_from_audience(self, visibility: str) -> bool:
        return self.audience == "student" and visibility in {"private", "teacher"}

    def _is_listable(
        self,
        record: IndexedObject,
        *,
        language: str | None = None,
        require_output_format: str | None = None,
    ) -> bool:
        selected_language = language or self.language
        if self._exclude_from_audience(record.model.visibility):
            return False
        if not self._language_available(
            record.model.languages,
            record.model.translation_status,
            selected_language,
        ):
            return False
        if require_output_format and require_output_format not in record.model.outputs:
            return False
        if isinstance(record.model, Resource):
            if self.audience == "student":
                return resource_student_visibility_decision(
                    record,
                    language=selected_language,
                    require_output_format=require_output_format,
                ).visible_to_student
            return True
        if self.audience != "student":
            return True
        return record.model.status in {"approved", "published"}

    def _language_available(
        self,
        languages: list[str],
        translation_status: dict[str, str],
        language: str,
    ) -> bool:
        return self._language_available_for_audience(
            languages,
            translation_status,
            language,
            audience=self.audience,
        )

    def _language_available_for_audience(
        self,
        languages: list[str],
        translation_status: dict[str, str],
        language: str,
        *,
        audience: str,
    ) -> bool:
        if language not in languages:
            return False
        if audience != "student":
            return True
        if not translation_status:
            return True
        return translation_status.get(language) == "approved"

    def _generated_path(self, output_category: str, identifier: str) -> Path:
        path = (
            generated_dir(self.root)
            / output_category
            / identifier
            / self.audience
            / self.language
            / self.output_format
            / f"{identifier}.qmd"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def _planned_output_path(self, output_category: str, identifier: str) -> Path:
        if self.delivery_output_root:
            base = self.delivery_output_root / self.audience / self.language / self.output_format
            path = (
                base
                / output_category
                / identifier
                / build_output_name(
                    identifier,
                    self.output_format,
                    audience=self.audience,
                )
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            return path
        path = planned_output_path(
            self.root,
            audience=self.audience,
            language=self.language,
            output_format=self.output_format,
            output_category=output_category,
            identifier=identifier,
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def _page_href(
        self,
        *,
        current_output: Path,
        target_kind: str,
        target_id: str,
    ) -> str | None:
        return self._page_href_for_variant(
            current_output=current_output,
            target_kind=target_kind,
            target_id=target_id,
            audience=self.audience,
            language=self.language,
        )

    def _page_href_for_variant(
        self,
        *,
        current_output: Path,
        target_kind: str,
        target_id: str,
        audience: str,
        language: str,
    ) -> str | None:
        if self.output_format != "html":
            return None
        target_output = planned_target_output_path(
            self.root,
            audience=audience,
            language=language,
            output_format="html",
            target_kind=target_kind,
            target_id=target_id,
        )
        relative = os.path.relpath(target_output, current_output.parent)
        return relative.replace(os.sep, "/")

    def _student_home_href(
        self,
        *,
        current_output: Path,
        language: str | None = None,
    ) -> str | None:
        selected_language = language or self.language
        return self._page_href_for_variant(
            current_output=current_output,
            target_kind="home",
            target_id=HOME_TARGET_ID,
            audience="student",
            language=selected_language,
        )

    def _audience_counterpart_href(
        self,
        *,
        target: BuildTargetRef,
        current_output: Path,
        audience: str,
        language: str,
    ) -> str | None:
        if not self._has_html_counterpart(target=target, audience=audience, language=language):
            return None
        return self._page_href_for_variant(
            current_output=current_output,
            target_kind=target.kind,
            target_id=target.identifier,
            audience=audience,
            language=language,
        )

    def _has_html_counterpart(
        self,
        *,
        target: BuildTargetRef,
        audience: str,
        language: str,
    ) -> bool:
        if audience == "teacher":
            return self._has_teacher_html_counterpart(target=target, language=language)
        return self._has_student_html_counterpart(target=target, language=language)

    def _has_teacher_html_counterpart(self, *, target: BuildTargetRef, language: str) -> bool:
        if target.kind in {"home", "topic-listing", "resource-listing"}:
            return False
        if target.kind == "resource-inbox":
            return True
        if target.kind == "course":
            course_record = self.index.courses.get(target.identifier)
            if course_record is None:
                return False
            return (
                course_record.model.visibility not in {"private", "teacher"}
                and course_record.model.status in {"approved", "published"}
                and language in course_record.model.languages
            )
        record = self.index.objects.get(target.identifier)
        if record is None:
            return False
        return (
            record.model.visibility != "private"
            and language in record.model.languages
            and "html" in record.model.outputs
        )

    def _has_student_html_counterpart(self, *, target: BuildTargetRef, language: str) -> bool:
        if target.kind == "home":
            return True
        if target.kind in {"topic-listing", "resource-listing", "resource-inbox"}:
            return False
        if target.kind == "course":
            course_record = self.index.courses.get(target.identifier)
            if course_record is None:
                return False
            return (
                course_record.model.visibility not in {"private", "teacher"}
                and course_record.model.status in {"approved", "published"}
                and language in course_record.model.languages
            )
        record = self.index.objects.get(target.identifier)
        if record is None:
            return False
        if record.model.visibility in {"private", "teacher"}:
            return False
        if "html" not in record.model.outputs:
            return False
        if not self._language_available_for_audience(
            record.model.languages,
            record.model.translation_status,
            language,
            audience="student",
        ):
            return False
        if isinstance(record.model, Resource):
            return resource_student_visibility_decision(
                record,
                language=language,
                require_output_format="html",
            ).visible_to_student
        return record.model.status in {"approved", "published"}

    def _render_link(
        self,
        target_id: str,
        target_kind: str,
        label: str,
        current_output: Path,
    ) -> str:
        href = self._page_href(
            current_output=current_output,
            target_kind=target_kind,
            target_id=target_id,
        )
        return f"[{label}]({href})" if href else label


def build_output_name(identifier: str, output_format: str, *, audience: str) -> str:
    extension = (
        ".pdf" if output_format in {"pdf", "slides-pdf", "handout", "exercise-sheet"} else ".html"
    )
    suffix = ""
    if output_format == "slides-pdf":
        suffix = "-slides"
    elif output_format == "handout":
        suffix = "-handout"
    elif output_format == "exercise-sheet":
        suffix = "-solution-sheet" if audience == "teacher" else "-exercise-sheet"
    return f"{identifier}{suffix}{extension}"


def collect_topics(records: list[IndexedObject]) -> list[str]:
    return sorted({topic for record in records for topic in record.model.topics})


def count_topic_items(records: list[IndexedObject], topic: str) -> int:
    return sum(1 for record in records if topic in record.model.topics)


def localized_count_label(count: int, language: str) -> str:
    if language == "nb":
        return f"{count} innslag"
    return f"{count} items"


def topic_listing_sort_key(record: IndexedObject, *, language: str) -> tuple[int, str, str]:
    kind = record.model.kind if not isinstance(record.model, Collection) else "collection"
    localized_title = record.model.title.get(language)
    if localized_title is None:
        localized_title = next(iter(record.model.title.values()))
    return (KIND_SORT_ORDER.get(kind, 99), localized_title, record.model.id)


def humanize_slug(slug: str) -> str:
    return " ".join(humanize_slug_token(token) for token in slug.split("-"))


def humanize_slug_token(token: str) -> str:
    acronym_labels = {
        "ai": "AI",
        "api": "API",
        "csv": "CSV",
        "evm": "EVM",
        "iv": "IV",
        "knn": "kNN",
        "llm": "LLM",
        "llms": "LLMs",
        "nlp": "NLP",
        "pca": "PCA",
        "rag": "RAG",
        "sql": "SQL",
        "utxo": "UTXO",
    }
    if token in acronym_labels:
        return acronym_labels[token]
    return token.capitalize()


def localized_language_name(language: str, ui_language: str) -> str:
    labels = {
        "en": {
            "en": "English",
            "nb": "Engelsk",
        },
        "nb": {
            "en": "Norwegian",
            "nb": "Norsk",
        },
    }
    return labels[language][ui_language]


def output_category_for_kind(target_kind: str) -> str:
    if target_kind == "home":
        return "home"
    if target_kind in {"concept", "exercise", "figure", "resource"}:
        return target_kind
    if target_kind == "collection":
        return "collection"
    if target_kind == "course":
        return "course"
    if target_kind in {"topic-listing", "resource-listing", "resource-inbox"}:
        return "listing"
    raise AssemblyError(f"unsupported target kind for output category: {target_kind}")


def planned_output_path(
    root: Path,
    *,
    audience: str,
    language: str,
    output_format: str,
    output_category: str,
    identifier: str,
) -> Path:
    base = exports_dir(root) / audience / language / output_format
    if output_category == "home" and output_format == "html":
        return base / "index.html"
    return (
        base
        / output_category
        / identifier
        / build_output_name(
            identifier,
            output_format,
            audience=audience,
        )
    )


def planned_target_output_path(
    root: Path,
    *,
    audience: str,
    language: str,
    output_format: str,
    target_kind: str,
    target_id: str,
) -> Path:
    return planned_output_path(
        root,
        audience=audience,
        language=language,
        output_format=output_format,
        output_category=output_category_for_kind(target_kind),
        identifier=target_id,
    )


def student_search_index_path(root: Path, language: str) -> Path:
    return exports_dir(root) / "student" / language / "html" / "assets" / "search-index.json"


def html_shell_asset_path(root: Path, audience: str, language: str, filename: str) -> Path:
    return exports_dir(root) / audience / language / "html" / "assets" / filename


def student_site_asset_path(root: Path, language: str, filename: str) -> Path:
    return html_shell_asset_path(root, "student", language, filename)


def localized_minutes(minutes: int, language: str) -> str:
    if language == "nb":
        return f"{minutes} minutter"
    return f"{minutes} minutes"


FIGURE_RENDER_STYLE = """
.lf-figure-card {
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.15rem;
  margin: 0 0 1.25rem 0;
  background: #f8fafc;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.lf-figure-surface {
  overflow-x: auto;
}
.lf-figure-svg {
  display: block;
  width: 100%;
  height: auto;
}
.lf-figure-caption,
.lf-figure-explainer {
  margin: 0.85rem 0 0 0;
  font-size: 0.92rem;
  color: #334155;
  line-height: 1.5;
}
.lf-figure-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 0 0 0.85rem 0;
}
.lf-figure-controls button {
  border: 1px solid #cbd5e1;
  border-radius: 999px;
  padding: 0.35rem 0.85rem;
  background: #ffffff;
  font-size: 0.88rem;
  cursor: pointer;
  transition: border-color 0.15s ease, background 0.15s ease;
}
.lf-figure-controls button:hover {
  border-color: #93c5fd;
  background: #eff6ff;
}
.lf-figure-controls button.is-active {
  border-color: #1e40af;
  background: #dbeafe;
  color: #1e40af;
  font-weight: 600;
}
"""


def render_frontmatter(payload: dict[str, str]) -> str:
    return "---\n" + yaml.safe_dump(payload, sort_keys=False, allow_unicode=False).strip() + "\n---"


def rewrite_relative_links(content: str, source_dir: Path, generated_path: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        raw_target = match.group(2)
        if raw_target.startswith(("http://", "https://", "#", "/")):
            return match.group(0)
        target_path = (source_dir / raw_target).resolve()
        if not target_path.exists():
            return match.group(0)
        relative_target = os.path.relpath(target_path, generated_path.parent)
        return f"{match.group(1)}{relative_target}{match.group(3)}"

    return MARKDOWN_LINK_RE.sub(replace, content)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()
