from __future__ import annotations

import os
import subprocess
from pathlib import Path

from textual.app import App

from app.config import LANGUAGES, REPO_ROOT
from app.tui.data import TUIIndex, load_tui_index


class LearnForgeApp(App):
    CSS_PATH = "learnforge.tcss"
    TITLE = "LearnForge"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("question_mark", "help", "Help"),
        ("L", "toggle_language", "Language"),
    ]

    def __init__(self, *, default_language: str = "en") -> None:
        super().__init__()
        self.language: str = default_language
        self.tui_index: TUIIndex = load_tui_index(REPO_ROOT)

    def on_mount(self) -> None:
        self.sub_title = f"lang: {self.language}"
        from app.tui.screens import DashboardScreen

        self.push_screen(DashboardScreen())

    def action_toggle_language(self) -> None:
        languages = list(LANGUAGES)
        idx = languages.index(self.language) if self.language in languages else 0
        self.language = languages[(idx + 1) % len(languages)]
        self.sub_title = f"lang: {self.language}"
        if hasattr(self.screen, "refresh_data"):
            self.screen.refresh_data()

    def action_help(self) -> None:
        self.notify(
            "hjkl: navigate  q: quit  Esc: back  Enter: drill in  Tab: switch panel\n"
            "s: schedule  e: edit note  m: edit meta  L: language",
            title="Keys",
        )

    def edit_file(self, path: Path) -> None:
        """Suspend TUI, open file in editor, reload index on return."""
        editor = os.environ.get("EDITOR", "nvim")
        with self.suspend():
            subprocess.run([editor, str(path)], cwd=REPO_ROOT, check=False)
        self.tui_index = load_tui_index(REPO_ROOT)
        if hasattr(self.screen, "refresh_data"):
            self.screen.refresh_data()

    def resolve_language(self, languages: list[str]) -> str:
        """Pick the app's language if the object supports it, else first available."""
        if self.language in languages:
            return self.language
        return languages[0] if languages else self.language
