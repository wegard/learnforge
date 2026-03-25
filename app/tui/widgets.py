from __future__ import annotations

from textual.widgets import ListItem, Static


class CourseListItem(ListItem):
    """A row in the Dashboard course list."""

    def __init__(self, course_id: str, status: str, attention_count: int) -> None:
        self.course_id = course_id
        self._status = status
        self._attention_count = attention_count
        super().__init__()

    def compose(self):
        badge = f"  ({self._attention_count}!)" if self._attention_count > 0 else ""
        yield Static(f"  {self.course_id:<12} {self._status:<10}{badge}")


class CollectionListItem(ListItem):
    """A row in the Course lectures/assignments list."""

    def __init__(self, collection_id: str, attention_count: int) -> None:
        self.collection_id = collection_id
        self._attention_count = attention_count
        super().__init__()

    def compose(self):
        badge = f"  ({self._attention_count}!)" if self._attention_count > 0 else ""
        yield Static(f"  {self.collection_id}{badge}")


class AttentionListItem(ListItem):
    """A row in the Dashboard attention panel."""

    def __init__(self, object_id: str, kind: str, reasons: list[str]) -> None:
        self.object_id = object_id
        self._kind = kind
        self._reasons = reasons
        super().__init__()

    def compose(self):
        reason_text = ", ".join(self._reasons)
        yield Static(f"  ! {self.object_id}")
        yield Static(f"    {self._kind} — {reason_text}", classes="attention-reason")
