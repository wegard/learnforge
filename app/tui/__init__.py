from __future__ import annotations


def launch(*, default_language: str = "en") -> None:
    from app.tui.app import LearnForgeApp

    app = LearnForgeApp(default_language=default_language)
    app.run()
