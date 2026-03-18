from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.config import REPO_ROOT
from app.indexer import RepositoryIndex, load_repository, write_search_index


@dataclass(slots=True)
class SearchResult:
    identifier: str
    kind: str
    title: str
    path: str
    score: int


def _match_score(query_tokens: list[str], haystack: str) -> int:
    lowered = haystack.lower()
    return sum(1 for token in query_tokens if token in lowered)


def search_repository(query: str, root: Path = REPO_ROOT) -> tuple[list[SearchResult], Path]:
    index, errors = load_repository(root, collect_errors=False)
    if errors:
        raise ValueError("repository index contains load errors")

    search_index_path = write_search_index(index, root)
    tokens = [token for token in query.lower().split() if token]
    if not tokens:
        return [], search_index_path

    results: list[SearchResult] = []
    _search_objects(tokens, index, results, root)
    _search_courses(tokens, index, results, root)
    results.sort(key=lambda item: (-item.score, item.identifier))
    return results, search_index_path


def _search_objects(
    tokens: list[str],
    index: RepositoryIndex,
    results: list[SearchResult],
    root: Path,
) -> None:
    for record in index.objects.values():
        model = record.model
        haystack = " ".join(
            [
                model.id,
                " ".join(model.title.values()),
                " ".join(model.tags),
                " ".join(model.topics),
                " ".join(model.courses),
            ]
        )
        score = _match_score(tokens, haystack)
        if score:
            results.append(
                SearchResult(
                    identifier=model.id,
                    kind=model.kind,
                    title=model.title.get("en") or next(iter(model.title.values())),
                    path=str(record.directory.relative_to(root)),
                    score=score,
                )
            )


def _search_courses(
    tokens: list[str],
    index: RepositoryIndex,
    results: list[SearchResult],
    root: Path,
) -> None:
    for record in index.courses.values():
        model = record.model
        haystack = " ".join(
            [
                model.id,
                " ".join(model.title.values()),
                " ".join(model.summary.values()),
            ]
        )
        score = _match_score(tokens, haystack)
        if score:
            results.append(
                SearchResult(
                    identifier=model.id,
                    kind="course",
                    title=model.title.get("en") or next(iter(model.title.values())),
                    path=str(record.directory.relative_to(root)),
                    score=score,
                )
            )
