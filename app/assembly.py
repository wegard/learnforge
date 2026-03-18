from __future__ import annotations

import hashlib
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

from app.config import REPO_ROOT, exports_dir, generated_dir
from app.indexer import IndexedCourse, IndexedObject, RepositoryIndex
from app.models import Collection, Resource

MARKDOWN_LINK_RE = re.compile(r"(\!?\[[^\]]*\]\()([^)]+)(\))")
TEACHER_BLOCK_RE = re.compile(r"\n?:::\s*\{\.teacher-only\}\n.*?\n:::\s*\n?", re.DOTALL)
STUDENT_BLOCK_RE = re.compile(r"\n?:::\s*\{\.student-only\}\n.*?\n:::\s*\n?", re.DOTALL)

TOPIC_TARGET_PREFIX = "topic-"
RESOURCE_LISTING_PREFIX = "resources-"

KIND_LABELS = {
    "collection": "Lecture",
    "concept": "Concept",
    "course": "Course",
    "exercise": "Exercise",
    "figure": "Figure",
    "resource": "Resource",
    "resource-listing": "Resource listing",
    "topic-listing": "Topic listing",
}

KIND_SORT_ORDER = {
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
class BuildTargetRef:
    identifier: str
    kind: str
    output_category: str
    title: str


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

    def build_manifest_payload(self) -> dict[str, object]:
        return {
            "target": asdict(self.target),
            "audience": self.audience,
            "language": self.language,
            "format": self.output_format,
            "generated_path": str(self.generated_path),
            "planned_output_path": str(self.planned_output_path),
            "file_dependency_count": len(self.file_dependencies),
            "dependency_edge_count": len(self.dependency_edges),
            "related_entries": [asdict(entry) for entry in self.related_entries],
            "listing_entries": [asdict(entry) for entry in self.listing_entries],
            "referenced_listing_targets": self.referenced_listing_targets,
        }

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
) -> AssemblyDocument:
    builder = AssemblyBuilder(
        index=index,
        audience=audience,
        language=language,
        output_format=output_format,
        root=root,
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
    ) -> None:
        self.index = index
        self.audience = audience
        self.language = language
        self.output_format = output_format
        self.root = root
        self.file_dependencies: dict[tuple[str, str], FileDependency] = {}
        self.dependency_edges: list[DependencyEdge] = []
        self.leakage_observations: list[LeakageObservation] = []
        self.referenced_listing_targets: list[str] = []

    def assemble(self, target_id: str) -> AssemblyDocument:
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

    def _assemble_object_page(self, record: IndexedObject) -> AssemblyDocument:
        self._ensure_visibility(record.model.visibility, record.model.id)
        self._ensure_language(record.model.languages, record.model.id)
        self._register_object_files(record, role="primary-object", include_note=True)

        content = self._load_object_note(record)
        related_entries = self._related_entries_for_object(record)
        if related_entries:
            content = (
                content.rstrip()
                + "\n\n"
                + self._render_related_section(
                    title="Related content" if self.language == "en" else "Relatert innhold",
                    entries=related_entries,
                )
            )

        target = BuildTargetRef(
            identifier=record.model.id,
            kind=record.model.kind,
            output_category=record.model.kind,
            title=record.model.title[self.language],
        )
        return self._finalize_document(
            target=target,
            markdown_body=content,
            related_entries=related_entries,
            listing_entries=[],
        )

    def _assemble_collection(self, record: IndexedObject) -> AssemblyDocument:
        self._ensure_visibility(record.model.visibility, record.model.id)
        self._ensure_language(record.model.languages, record.model.id)
        self._register_object_files(record, role="primary-collection", include_note=False)

        parts = [
            f"## {record.model.title[self.language]}",
            "",
        ]
        for item_id in record.model.items:
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
            parts.append(self._load_object_note(item_record))
            parts.append("")

        target = BuildTargetRef(
            identifier=record.model.id,
            kind="collection",
            output_category="collection",
            title=record.model.title[self.language],
        )
        return self._finalize_document(
            target=target,
            markdown_body="\n".join(parts).rstrip(),
            related_entries=[],
            listing_entries=[],
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

        sections = [
            record.model.summary[self.language],
            self._render_listing_section(
                title="Lectures" if self.language == "en" else "Forelesninger",
                entries=lecture_entries,
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
                    if self.output_format == "html"
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
                    if self.output_format == "html"
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
            listing_entries=[*lecture_entries, *topic_entries, *resource_entries],
        )

    def _assemble_topic_listing(self, target_id: str) -> AssemblyDocument:
        if self.output_format != "html":
            raise AssemblyError("topic listing builds currently support html only")

        topic = target_id.removeprefix(TOPIC_TARGET_PREFIX)
        matches = [
            item
            for item in self.index.objects.values()
            if topic in item.model.topics and self._is_listable(item)
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
            for record in sorted(matches, key=topic_listing_sort_key)
        ]
        body = self._render_listing_page(
            title=f"Topic: {humanize_slug(topic)}"
            if self.language == "en"
            else f"Tema: {humanize_slug(topic)}",
            entries=entries,
            group_by_kind=True,
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
        resources = [
            item
            for item in self.index.objects.values()
            if isinstance(item.model, Resource)
            and course_id in item.model.courses
            and self._is_listable(item)
        ]
        if not resources:
            raise AssemblyError(f"no resources found for course {course_id}")

        current_output = self._planned_output_path("listing", target_id)
        entries: list[ListingEntry] = []
        for record in sorted(resources, key=lambda item: item.model.title[self.language]):
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
        body = self._render_listing_page(title=title, entries=entries, group_by_kind=False)
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
        frontmatter = render_frontmatter(
            {
                "title": target.title,
                "lang": self.language,
                "audience": self.audience,
                "language_variant": self.language,
            }
        )
        markdown = frontmatter + "\n" + markdown_body.rstrip() + "\n"
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
        )

    def _course_objects(self, course_id: str) -> list[IndexedObject]:
        return [
            record
            for record in self.index.objects.values()
            if course_id in record.model.courses and self._is_listable(record)
        ]

    def _related_entries_for_object(self, record: IndexedObject) -> list[RelatedEntry]:
        if record.model.kind == "concept":
            return self._related_entries_for_concept(record)
        if record.model.kind == "resource":
            return self._related_entries_for_resource(record)
        return []

    def _related_entries_for_concept(self, record: IndexedObject) -> list[RelatedEntry]:
        entries: list[RelatedEntry] = []
        seen_ids: set[str] = set()
        for related_id in record.model.related:
            related_record = self.index.objects.get(related_id)
            if related_record is None or not self._is_listable(related_record):
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
            and self._is_listable(item)
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

    def _related_entries_for_resource(self, record: IndexedObject) -> list[RelatedEntry]:
        candidates: list[tuple[int, IndexedObject]] = []
        for item in self.index.objects.values():
            if item.model.id == record.model.id or not self._is_listable(item):
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
        lines = [f"## {title}", ""]
        for entry in entries:
            kind_label = KIND_LABELS.get(entry.kind, entry.kind.title())
            target_text = (
                f"[{entry.title}]({entry.href})"
                if self.output_format == "html" and entry.href
                else entry.title
            )
            lines.append(f"- {target_text} [{kind_label.lower()}]")
        return "\n".join(lines)

    def _render_listing_section(
        self,
        *,
        title: str,
        entries: list[ListingEntry],
        suffix: str = "",
    ) -> str:
        lines = [f"## {title}", ""]
        if not entries:
            lines.append("No entries.")
        else:
            for entry in entries:
                target_text = (
                    f"[{entry.title}]({entry.href})"
                    if self.output_format == "html" and entry.href
                    else entry.title
                )
                if entry.description:
                    lines.append(f"- {target_text} - {entry.description}")
                else:
                    lines.append(f"- {target_text}")
        if suffix:
            lines.extend(["", suffix])
        return "\n".join(lines)

    def _render_listing_page(
        self,
        *,
        title: str,
        entries: list[ListingEntry],
        group_by_kind: bool,
    ) -> str:
        lines = [title, ""]
        if group_by_kind:
            grouped: dict[str, list[ListingEntry]] = {}
            for entry in entries:
                grouped.setdefault(entry.kind, []).append(entry)
            for kind in sorted(grouped, key=lambda item: KIND_SORT_ORDER.get(item, 99)):
                lines.append(f"## {KIND_LABELS.get(kind, kind.title())}s")
                lines.append("")
                for entry in grouped[kind]:
                    target_text = (
                        f"[{entry.title}]({entry.href})"
                        if self.output_format == "html" and entry.href
                        else entry.title
                    )
                    if entry.description:
                        lines.append(f"- {target_text} - {entry.description}")
                    else:
                        lines.append(f"- {target_text}")
                lines.append("")
            return "\n".join(lines).rstrip()

        for entry in entries:
            target_text = (
                f"[{entry.title}]({entry.href})"
                if self.output_format == "html" and entry.href
                else entry.title
            )
            lines.append(f"- {target_text} - {entry.description}")
        return "\n".join(lines).rstrip()

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
        if self.language not in languages:
            raise AssemblyError(f"{identifier} does not support language {self.language}")

    def _exclude_from_audience(self, visibility: str) -> bool:
        return self.audience == "student" and visibility in {"private", "teacher"}

    def _is_listable(self, record: IndexedObject) -> bool:
        if self._exclude_from_audience(record.model.visibility):
            return False
        if self.language not in record.model.languages:
            return False
        return record.model.status in {"approved", "published"}

    def _generated_path(self, output_category: str, identifier: str) -> Path:
        path = (
            generated_dir(self.root)
            / output_category
            / identifier
            / self.audience
            / self.language
            / f"{identifier}.{self.output_format}.qmd"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def _planned_output_path(self, output_category: str, identifier: str) -> Path:
        output_dir = (
            exports_dir(self.root)
            / self.audience
            / self.language
            / self.output_format
            / output_category
            / identifier
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / build_output_name(identifier, self.output_format)

    def _page_href(
        self,
        *,
        current_output: Path,
        target_kind: str,
        target_id: str,
    ) -> str | None:
        if self.output_format != "html":
            return None
        output_category = output_category_for_kind(target_kind)
        target_output = (
            exports_dir(self.root)
            / self.audience
            / self.language
            / "html"
            / output_category
            / target_id
            / build_output_name(target_id, "html")
        )
        relative = os.path.relpath(target_output, current_output.parent)
        return relative.replace(os.sep, "/")

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


def build_output_name(identifier: str, output_format: str) -> str:
    extension = ".pdf" if output_format in {"pdf", "handout", "exercise-sheet"} else ".html"
    suffix = ""
    if output_format == "handout":
        suffix = "-handout"
    elif output_format == "exercise-sheet":
        suffix = "-exercise-sheet"
    return f"{identifier}{suffix}{extension}"


def collect_topics(records: list[IndexedObject]) -> list[str]:
    return sorted({topic for record in records for topic in record.model.topics})


def count_topic_items(records: list[IndexedObject], topic: str) -> int:
    return sum(1 for record in records if topic in record.model.topics)


def localized_count_label(count: int, language: str) -> str:
    if language == "nb":
        return f"{count} innslag"
    return f"{count} items"


def topic_listing_sort_key(record: IndexedObject) -> tuple[int, str, str]:
    kind = record.model.kind if not isinstance(record.model, Collection) else "collection"
    return (KIND_SORT_ORDER.get(kind, 99), record.model.title["en"], record.model.id)


def humanize_slug(slug: str) -> str:
    return slug.replace("-", " ").title()


def output_category_for_kind(target_kind: str) -> str:
    if target_kind in {"concept", "exercise", "figure", "resource"}:
        return target_kind
    if target_kind == "collection":
        return "collection"
    if target_kind == "course":
        return "course"
    if target_kind in {"topic-listing", "resource-listing"}:
        return "listing"
    raise AssemblyError(f"unsupported target kind for output category: {target_kind}")


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
