from __future__ import annotations

from rich.text import Text
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Label, ListView, Static

from app.models import Collection, Concept, Exercise, Figure, Resource
from app.tui.widgets import AttentionListItem, CollectionListItem, CourseListItem

# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------

_STATUS_STYLES: dict[str, str] = {
    "approved": "green",
    "published": "green",
    "draft": "yellow",
    "review": "rgb(85,153,255)",
    "candidate": "yellow",
    "reviewed": "yellow",
    "archived": "dim",
}


def _styled_status(status: str) -> Text:
    style = _STATUS_STYLES.get(status, "")
    return Text(status, style=style)


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


class DashboardScreen(Screen):
    BINDINGS = [
        Binding("enter", "select", "Drill in", show=True),
        Binding("escape", "app.quit", "Quit", priority=True),
        Binding("tab", "focus_next", "Switch panel"),
    ]

    def compose(self):
        yield Header()
        with Horizontal(id="dashboard-panels"):
            with Vertical(id="courses-panel", classes="panel"):
                yield Label("COURSES", classes="panel-title")
                yield ListView(id="course-list")
            with Vertical(id="attention-panel", classes="panel"):
                yield Label("NEEDS ATTENTION", classes="panel-title")
                yield ListView(id="attention-list")
        yield Static(id="dashboard-footer-stats")
        yield Footer()

    def on_mount(self) -> None:
        self._populate()

    def _populate(self) -> None:
        idx = self.app.tui_index

        course_lv = self.query_one("#course-list", ListView)
        course_lv.clear()
        for course in idx.active_courses:
            count = idx.course_attention_counts.get(course.model.id, 0)
            course_lv.append(CourseListItem(course.model.id, course.model.status, count))

        attn_lv = self.query_one("#attention-list", ListView)
        attn_lv.clear()
        for item in sorted(idx.attention_items.values(), key=lambda a: a.object_id):
            attn_lv.append(AttentionListItem(item.object_id, item.kind, item.reasons))

        total_objects = len(idx.repo_index.objects)
        total_attention = len(idx.attention_items)
        total_courses = len(idx.active_courses)
        stats = self.query_one("#dashboard-footer-stats", Static)
        stats.update(
            f"  {total_courses} courses · {total_objects} objects · "
            f"{total_attention} need attention       lang: {self.app.language}"
        )

    def refresh_data(self) -> None:
        self._populate()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if isinstance(item, CourseListItem):
            self.app.push_screen(CourseScreen(item.course_id))
        elif isinstance(item, AttentionListItem):
            self.app.push_screen(ObjectDetailScreen(item.object_id))


# ---------------------------------------------------------------------------
# Course
# ---------------------------------------------------------------------------


class CourseScreen(Screen):
    BINDINGS = [
        Binding("enter", "select", "Drill in", show=True),
        Binding("e", "edit_syllabus", "Edit syllabus"),
        Binding("escape", "pop", "Back", priority=True),
        Binding("tab", "focus_next", "Switch panel"),
    ]

    def __init__(self, course_id: str) -> None:
        super().__init__()
        self.course_id = course_id

    def compose(self):
        course = self.app.tui_index.repo_index.courses[self.course_id]
        lang = self.app.resolve_language(course.model.languages)
        title_text = course.model.title.get(lang, self.course_id)

        yield Header()
        yield Label(
            f"Course: {self.course_id} — {title_text}",
            id="course-title",
        )
        with Horizontal(id="course-panels"):
            with Vertical(id="lectures-panel", classes="panel"):
                yield Label(
                    f"LECTURES ({len(course.plan.lectures)})",
                    classes="panel-title",
                )
                yield ListView(id="lecture-list")
            with Vertical(id="assignments-panel", classes="panel"):
                yield Label(
                    f"ASSIGNMENTS ({len(course.plan.assignments)})",
                    classes="panel-title",
                )
                yield ListView(id="assignment-list")
        yield Static(id="course-footer-stats")
        yield Footer()

    def on_mount(self) -> None:
        self._populate()

    def _populate(self) -> None:
        idx = self.app.tui_index
        course = idx.repo_index.courses[self.course_id]

        lec_lv = self.query_one("#lecture-list", ListView)
        lec_lv.clear()
        for coll_id in course.plan.lectures:
            count = idx.collection_attention_counts.get(coll_id, 0)
            lec_lv.append(CollectionListItem(coll_id, count))

        asn_lv = self.query_one("#assignment-list", ListView)
        asn_lv.clear()
        for coll_id in course.plan.assignments:
            count = idx.collection_attention_counts.get(coll_id, 0)
            asn_lv.append(CollectionListItem(coll_id, count))

        stats = self.query_one("#course-footer-stats", Static)
        stats.update(
            f"  {course.model.status} · {len(course.plan.lectures)} lectures · "
            f"{len(course.plan.assignments)} assignments · "
            f"updated {course.model.updated}"
        )

    def refresh_data(self) -> None:
        self._populate()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if isinstance(item, CollectionListItem):
            self.app.push_screen(CollectionScreen(item.collection_id))

    def action_pop(self) -> None:
        self.app.pop_screen()

    def action_edit_syllabus(self) -> None:
        course = self.app.tui_index.repo_index.courses[self.course_id]
        lang = self.app.resolve_language(course.model.languages)
        self.app.edit_file(course.syllabus_path(lang))


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------


class CollectionScreen(Screen):
    BINDINGS = [
        Binding("enter", "select_row", "Details", show=True),
        Binding("e", "edit_meta", "Edit meta.yml"),
        Binding("escape", "pop", "Back", priority=True),
    ]

    def __init__(self, collection_id: str) -> None:
        super().__init__()
        self.collection_id = collection_id

    def compose(self):
        yield Header()
        yield Label(
            f"Collection: {self.collection_id}",
            id="collection-title",
        )
        yield DataTable(id="items-table")
        yield Static(id="collection-footer-stats")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#items-table", DataTable)
        table.cursor_type = "row"
        table.add_columns("ID", "Kind", "Status", "Updated", "!")
        self._populate()

    def _populate(self) -> None:
        idx = self.app.tui_index
        obj = idx.repo_index.objects.get(self.collection_id)

        table = self.query_one("#items-table", DataTable)
        table.clear()

        if obj is None or not isinstance(obj.model, Collection):
            return

        coll = obj.model
        attention_count = 0

        for item_id in coll.items:
            item_obj = idx.repo_index.objects.get(item_id)
            if item_obj is None:
                table.add_row(item_id, "?", Text("missing", style="dim"), "", "", key=item_id)
                continue
            m = item_obj.model
            flag = Text("!", style="bold yellow") if item_id in idx.attention_items else Text("")
            if item_id in idx.attention_items:
                attention_count += 1
            updated_str = m.updated.strftime("%Y-%m") if m.updated else ""
            table.add_row(item_id, m.kind, _styled_status(m.status), updated_str, flag, key=item_id)

        stats = self.query_one("#collection-footer-stats", Static)
        kind = coll.collection_kind
        total = len(coll.items)
        stats.update(
            f"  {kind} · {total} items · "
            f"{attention_count} need{'s' if attention_count == 1 else ''} attention"
        )

    def refresh_data(self) -> None:
        self._populate()

    def action_select_row(self) -> None:
        table = self.query_one("#items-table", DataTable)
        if table.row_count == 0:
            return
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        self.app.push_screen(ObjectDetailScreen(row_key.value))

    def action_pop(self) -> None:
        self.app.pop_screen()

    def action_edit_meta(self) -> None:
        obj = self.app.tui_index.repo_index.objects.get(self.collection_id)
        if obj is not None:
            self.app.edit_file(obj.meta_path)


# ---------------------------------------------------------------------------
# Object Detail
# ---------------------------------------------------------------------------


class ObjectDetailScreen(Screen):
    BINDINGS = [
        Binding("e", "edit_note", "Edit note"),
        Binding("m", "edit_meta", "Edit meta.yml"),
        Binding("s", "edit_solution", "Edit solution"),
        Binding("escape", "pop", "Back", priority=True),
    ]

    def __init__(self, object_id: str) -> None:
        super().__init__()
        self.object_id = object_id

    def compose(self):
        yield Header()
        yield Label(f"Object: {self.object_id}", id="object-title")
        yield VerticalScroll(id="detail-body")
        yield Footer()

    def on_mount(self) -> None:
        self._populate()

    def _populate(self) -> None:
        container = self.query_one("#detail-body", VerticalScroll)
        container.remove_children()

        idx = self.app.tui_index
        obj = idx.repo_index.objects.get(self.object_id)
        if obj is None:
            container.mount(Static(f"  Object '{self.object_id}' not found."))
            return

        m = obj.model
        lang = self.app.resolve_language(m.languages)

        lines: list[tuple[str, str]] = []
        lines.append(("Kind", m.kind))
        lines.append(("Status", m.status))

        if isinstance(m, Concept):
            lines.append(("Level", m.level))
            if m.prerequisites:
                lines.append(("Prerequisites", ", ".join(m.prerequisites)))
            if m.related:
                lines.append(("Related", ", ".join(m.related)))
        elif isinstance(m, Exercise):
            lines.append(("Exercise type", m.exercise_type))
            lines.append(("Difficulty", m.difficulty))
            lines.append(("Est. time", f"{m.estimated_time_minutes} min"))
            if m.concepts:
                lines.append(("Concepts", ", ".join(m.concepts)))
        elif isinstance(m, Figure):
            if m.asset_inventory:
                lines.append(("Assets", ", ".join(m.asset_inventory)))
        elif isinstance(m, Resource):
            lines.append(("Resource kind", m.resource_kind))
            lines.append(("URL", str(m.url)))
            if m.authors:
                lines.append(("Authors", ", ".join(m.authors)))
            lines.append(("Difficulty", m.difficulty))
            lines.append(("Est. time", f"{m.estimated_time_minutes} min"))
            lines.append(("Freshness", m.freshness))
            if m.review_after:
                lines.append(("Review after", str(m.review_after)))
            lines.append(("Stale", "yes" if m.stale_flag else "no"))
            if m.approved_by:
                lines.append(("Approved by", f"{m.approved_by} on {m.approved_on}"))

        lines.append(("Languages", ", ".join(m.languages)))
        lines.append(("Title", m.title.get(lang, "?")))
        lines.append(("Updated", str(m.updated)))
        if m.courses:
            lines.append(("Courses", ", ".join(m.courses)))
        if m.topics:
            lines.append(("Topics", ", ".join(m.topics)))
        if m.owners:
            lines.append(("Owners", ", ".join(m.owners)))
        if m.translation_status:
            ts = ", ".join(f"{k}={v}" for k, v in m.translation_status.items())
            lines.append(("Translation", ts))

        max_label = max(len(label) for label, _ in lines) if lines else 0
        for label, value in lines:
            css_class = f"status-{m.status}" if label == "Status" else ""
            container.mount(Static(f"  {label + ':':<{max_label + 2}} {value}", classes=css_class))

        # File listing
        container.mount(Static(""))
        container.mount(Static("  Files:", classes="panel-title"))
        files = []
        for file_lang in m.languages:
            note = obj.note_path(file_lang)
            if note.exists():
                files.append(note.name)
        files.append("meta.yml")
        if isinstance(m, Exercise):
            for file_lang in m.languages:
                sol = obj.solution_path(file_lang)
                if sol.exists():
                    files.append(sol.name)
        container.mount(Static(f"    {' · '.join(files)}"))

    def refresh_data(self) -> None:
        self._populate()

    def action_pop(self) -> None:
        self.app.pop_screen()

    def action_edit_note(self) -> None:
        obj = self.app.tui_index.repo_index.objects.get(self.object_id)
        if obj is None:
            return
        lang = self.app.resolve_language(obj.model.languages)
        self.app.edit_file(obj.note_path(lang))

    def action_edit_meta(self) -> None:
        obj = self.app.tui_index.repo_index.objects.get(self.object_id)
        if obj is not None:
            self.app.edit_file(obj.meta_path)

    def action_edit_solution(self) -> None:
        obj = self.app.tui_index.repo_index.objects.get(self.object_id)
        if obj is None or not isinstance(obj.model, Exercise):
            self.notify("Solution only available for exercises", severity="warning")
            return
        lang = self.app.resolve_language(obj.model.languages)
        self.app.edit_file(obj.solution_path(lang))
