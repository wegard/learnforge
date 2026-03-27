from __future__ import annotations

import datetime

from rich.text import Text
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Label, ListView, Static

from app.models import Collection, Concept, Exercise, Figure, Resource
from app.tui.schedule import (
    _SCHEDULE_TEMPLATE,
    FlatEvent,
    flatten_schedule,
    load_schedule,
    schedule_path,
)
from app.tui.teaching import (
    _TEACHING_TEMPLATE,
    load_teaching,
    teaching_path,
)
from app.tui.widgets import (
    AttentionListItem,
    CollectionListItem,
    CourseListItem,
    SectionHeaderItem,
)

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
        Binding("s", "schedule", "Schedule"),
        Binding("t", "edit_teaching", "Teaching"),
        Binding("tab", "app.focus_next", "Switch panel"),
        Binding("shift+tab", "app.focus_previous", "Switch panel", show=False),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("l", "select", "Drill in", show=False),
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
        self.query_one("#course-list").focus()

    def _populate(self) -> None:
        idx = self.app.tui_index
        teaching, _ = load_teaching()

        # Partition courses by teaching status
        active: list[tuple[str, str, int]] = []
        upcoming: list[tuple[str, str, int]] = []
        discontinued: list[tuple[str, str, int]] = []
        other: list[tuple[str, str, int]] = []

        for course in idx.active_courses:
            cid = course.model.id
            count = idx.course_attention_counts.get(cid, 0)
            entry = (cid, course.model.status, count)
            ct = teaching.courses.get(cid)
            if ct is None:
                other.append(entry)
            elif ct.teaching_status == "active":
                active.append(entry)
            elif ct.teaching_status == "upcoming":
                upcoming.append(entry)
            elif ct.teaching_status == "discontinued":
                discontinued.append(entry)
            else:
                other.append(entry)

        course_lv = self.query_one("#course-list", ListView)
        course_lv.clear()

        has_teaching = bool(teaching.courses)

        if has_teaching:
            sections: list[tuple[str, list[tuple[str, str, int]]]] = []
            if active:
                sections.append(("ACTIVE", active))
            if upcoming:
                sections.append(("UPCOMING", upcoming))
            if other:
                sections.append(("OTHER", other))
            if discontinued:
                sections.append(("DISCONTINUED", discontinued))

            for section_label, courses in sections:
                course_lv.append(SectionHeaderItem(section_label))
                for cid, status, count in courses:
                    course_lv.append(CourseListItem(cid, status, count))
        else:
            for course in idx.active_courses:
                count = idx.course_attention_counts.get(course.model.id, 0)
                course_lv.append(CourseListItem(course.model.id, course.model.status, count))

        attn_lv = self.query_one("#attention-list", ListView)
        attn_lv.clear()
        for item in sorted(idx.attention_items.values(), key=lambda a: a.object_id):
            attn_lv.append(AttentionListItem(item.object_id, item.kind, item.reasons))

        total_objects = len(idx.repo_index.objects)
        total_attention = len(idx.attention_items)

        next_up = ""
        schedule, _ = load_schedule()
        if schedule.courses:
            flat = flatten_schedule(schedule, idx.repo_index, self.app.language, future_only=True)
            if flat:
                ev = flat[0]
                delta = (ev.date - datetime.date.today()).days
                if delta == 0:
                    when = "today"
                elif delta == 1:
                    when = "tomorrow"
                else:
                    when = f"in {delta}d"
                next_up = f" · next: {ev.course_id} {ev.event_type} {when}"

        parts = []
        if active:
            parts.append(f"{len(active)} active")
        if upcoming:
            parts.append(f"{len(upcoming)} upcoming")
        parts.append(f"{total_objects} objects")
        parts.append(f"{total_attention} need attention")
        stats = self.query_one("#dashboard-footer-stats", Static)
        stats.update(f"  {' · '.join(parts)}{next_up}")

    def refresh_data(self) -> None:
        self._populate()

    def action_schedule(self) -> None:
        self.app.push_screen(ScheduleScreen())

    def action_edit_teaching(self) -> None:
        path = teaching_path()
        if not path.exists():
            path.write_text(_TEACHING_TEMPLATE, encoding="utf-8")
        self.app.edit_file(path)

    def action_select(self) -> None:
        focused = self.focused
        if isinstance(focused, ListView):
            focused.action_select_cursor()

    def action_cursor_down(self) -> None:
        focused = self.focused
        if isinstance(focused, ListView):
            focused.action_cursor_down()

    def action_cursor_up(self) -> None:
        focused = self.focused
        if isinstance(focused, ListView):
            focused.action_cursor_up()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if isinstance(item, CourseListItem):
            self.app.push_screen(CourseScreen(item.course_id))
        elif isinstance(item, AttentionListItem):
            self.app.push_screen(ObjectDetailScreen(item.object_id))


# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------

_EVENT_TYPE_STYLES: dict[str, str] = {
    "lecture": "",
    "exam": "bold red",
    "exam-upload-deadline": "yellow",
    "grading-deadline": "yellow",
    "assignment-deadline": "yellow",
    "other": "dim",
}

_EVENT_TYPE_SHORT: dict[str, str] = {
    "lecture": "lecture",
    "exam": "exam",
    "exam-upload-deadline": "deadline",
    "grading-deadline": "deadline",
    "assignment-deadline": "deadline",
    "other": "other",
}


class ScheduleScreen(Screen):
    BINDINGS = [
        Binding("enter", "drill_in", "Material", show=True),
        Binding("e", "edit_schedule", "Edit schedule"),
        Binding("f", "toggle_filter", "All/Future"),
        Binding("escape", "pop", "Back", priority=True),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("l", "drill_in", "Material", show=False),
        Binding("h", "pop", "Back", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._future_only = True
        self._flat_events: list[FlatEvent] = []
        self._schedule_error: str | None = None

    def compose(self):
        yield Header()
        yield Label("Teaching Schedule", id="schedule-title")
        yield DataTable(id="schedule-table")
        yield Static(id="schedule-footer-stats")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#schedule-table", DataTable)
        table.cursor_type = "row"
        table.add_columns("Date", "Time", "Course", "Type", "What", "Room")
        self._populate()

    def _populate(self) -> None:
        schedule, error = load_schedule()
        self._schedule_error = error

        if error:
            self.notify(
                "Schedule file has errors — press e to fix",
                severity="warning",
            )

        idx = self.app.tui_index
        self._flat_events = flatten_schedule(
            schedule,
            idx.repo_index,
            self.app.language,
            future_only=self._future_only,
        )

        table = self.query_one("#schedule-table", DataTable)
        table.clear()

        for i, ev in enumerate(self._flat_events):
            date_str = ev.date.strftime("%Y-%m-%d")
            time_str = ev.time.strftime("%H:%M") if ev.time else ""
            type_style = _EVENT_TYPE_STYLES.get(ev.event_type, "")
            type_label = _EVENT_TYPE_SHORT.get(ev.event_type, ev.event_type)

            table.add_row(
                date_str,
                time_str,
                ev.course_id,
                Text(type_label, style=type_style),
                ev.display_label,
                ev.room or "",
                key=str(i),
            )

        courses_seen = {ev.course_id for ev in self._flat_events}
        filter_label = "upcoming" if self._future_only else "all"
        stats = self.query_one("#schedule-footer-stats", Static)
        stats.update(
            f"  {len(self._flat_events)} {filter_label} events"
            f" across {len(courses_seen)} course{'s' if len(courses_seen) != 1 else ''}"
        )

    def refresh_data(self) -> None:
        self._populate()

    def action_cursor_down(self) -> None:
        self.query_one("#schedule-table", DataTable).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one("#schedule-table", DataTable).action_cursor_up()

    def action_drill_in(self) -> None:
        table = self.query_one("#schedule-table", DataTable)
        if table.row_count == 0:
            return
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        idx = int(row_key.value)
        ev = self._flat_events[idx]
        if ev.collection_id:
            self.app.push_screen(CollectionScreen(ev.collection_id))
        else:
            self.notify("No linked material for this event", severity="information")

    def action_edit_schedule(self) -> None:
        path = schedule_path()
        if not path.exists():
            path.write_text(_SCHEDULE_TEMPLATE, encoding="utf-8")
        self.app.edit_file(path)

    def action_toggle_filter(self) -> None:
        self._future_only = not self._future_only
        self._populate()

    def action_pop(self) -> None:
        self.app.pop_screen()


# ---------------------------------------------------------------------------
# Course
# ---------------------------------------------------------------------------


class CourseScreen(Screen):
    BINDINGS = [
        Binding("enter", "select", "Drill in", show=True),
        Binding("e", "edit_syllabus", "Edit syllabus"),
        Binding("escape", "pop", "Back", priority=True),
        Binding("tab", "app.focus_next", "Switch panel"),
        Binding("shift+tab", "app.focus_previous", "Switch panel", show=False),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("l", "select", "Drill in", show=False),
        Binding("h", "pop", "Back", show=False),
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
        self.query_one("#lecture-list").focus()

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

    def action_select(self) -> None:
        focused = self.focused
        if isinstance(focused, ListView):
            focused.action_select_cursor()

    def action_cursor_down(self) -> None:
        focused = self.focused
        if isinstance(focused, ListView):
            focused.action_cursor_down()

    def action_cursor_up(self) -> None:
        focused = self.focused
        if isinstance(focused, ListView):
            focused.action_cursor_up()

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
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("l", "select_row", "Details", show=False),
        Binding("h", "pop", "Back", show=False),
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

    def action_cursor_down(self) -> None:
        self.query_one("#items-table", DataTable).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one("#items-table", DataTable).action_cursor_up()

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
        Binding("e", "edit_note", "Edit note", priority=True),
        Binding("m", "edit_meta", "Edit meta.yml", priority=True),
        Binding("s", "edit_solution", "Edit solution", priority=True),
        Binding("escape", "pop", "Back", priority=True),
        Binding("j", "scroll_down", "Down", show=False, priority=True),
        Binding("k", "scroll_up", "Up", show=False, priority=True),
        Binding("h", "pop", "Back", show=False, priority=True),
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

        # File actions
        container.mount(Static(""))
        container.mount(Static("  Actions:", classes="panel-title"))
        lang = self.app.resolve_language(m.languages)
        note = obj.note_path(lang)
        note_label = note.name if note.exists() else f"note.{lang}.qmd (missing)"
        container.mount(Static(f"    [e]  Edit {note_label}"))
        container.mount(Static("    [m]  Edit meta.yml"))
        if isinstance(m, Exercise):
            sol = obj.solution_path(lang)
            sol_label = sol.name if sol.exists() else f"solution.{lang}.qmd (missing)"
            container.mount(Static(f"    [s]  Edit {sol_label}"))
        if len(m.languages) > 1:
            container.mount(Static(f"    [L]  Switch language (current: {lang})"))

    def action_scroll_down(self) -> None:
        self.query_one("#detail-body", VerticalScroll).scroll_down()

    def action_scroll_up(self) -> None:
        self.query_one("#detail-body", VerticalScroll).scroll_up()

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
