from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from app.assembly import AssemblyError, assemble_target
from app.config import REPO_ROOT
from app.indexer import load_repository


def test_collection_assembly_expands_items_from_ids() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "lecture-04",
        index=index,
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert assembly.target.kind == "collection"
    assert edge_targets == [
        "iv-intuition",
        "iv-dag-figure",
        "ex-iv-concept-check",
        "angrist-podcast-iv",
    ]
    assert "## Why IV shows up at all" in assembly.markdown
    assert 'data-figure-id="iv-dag-figure"' in assembly.markdown
    assert "## Why this resource is on the list" in assembly.markdown


def test_collection_assembly_updates_when_object_changes(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)

    index, _ = load_repository(tmp_path, collect_errors=False)
    original = assemble_target(
        "lecture-04",
        index=index,
        audience="teacher",
        language="en",
        output_format="html",
        root=tmp_path,
    )

    concept_note = tmp_path / "content" / "concepts" / "iv-intuition" / "note.en.qmd"
    concept_note.write_text(
        concept_note.read_text(encoding="utf-8").replace(
            "An instrument gives you variation in treatment",
            "A revised instrument explanation gives you variation in treatment",
        ),
        encoding="utf-8",
    )

    refreshed_index, _ = load_repository(tmp_path, collect_errors=False)
    refreshed = assemble_target(
        "lecture-04",
        index=refreshed_index,
        audience="teacher",
        language="en",
        output_format="html",
        root=tmp_path,
    )

    assert "A revised instrument explanation" not in original.markdown
    assert "A revised instrument explanation" in refreshed.markdown


def test_tem0052_lecture_assembly_expands_only_promoted_objects() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "tem0052-lecture-05",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == [
        "model-selection-cross-validation",
        "bias-variance-tradeoff",
        "model-assessment-lab",
    ]
    assert "## Model selection is a workflow choice" in assembly.markdown
    assert "## Why the trade-off matters" in assembly.markdown
    assert "## Lab brief" in assembly.markdown
    assert "iv-intuition" not in assembly.markdown


def test_tem0052_lecture_02_assembly_expands_regression_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "tem0052-lecture-02",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == [
        "linear-regression-prediction",
        "penalized-linear-models",
        "house-prices-regression",
    ]
    assert "## Linear regression is the first serious baseline" in assembly.markdown
    assert "## Why we penalize a linear model" in assembly.markdown
    assert "## Lab brief" in assembly.markdown
    assert "model-assessment-lab" not in assembly.markdown


def test_tem0052_lecture_03_assembly_expands_classification_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "tem0052-lecture-03",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == [
        "knn-supervised-learning",
        "logistic-regression-classification",
        "naive-bayes-classification",
        "spam-filtering-naive-bayes",
    ]
    assert "## Why k-nearest neighbors belongs early in the course" in assembly.markdown
    assert "## Logistic regression is a classifier, not a ranking trick" in assembly.markdown
    assert "## Naive Bayes is a useful simplification, not a claim about reality" in (
        assembly.markdown
    )
    assert "## Lab brief" in assembly.markdown
    assert "house-prices-regression" not in assembly.markdown


def test_tem0052_lecture_07_assembly_expands_tree_ensemble_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "tem0052-lecture-07",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == [
        "decision-tree-learning",
        "ensemble-methods-introduction",
        "random-forests",
    ]
    assert "## Decision trees turn prediction into a sequence of splits" in assembly.markdown
    assert (
        "## Ensemble methods combine weak or unstable models into a stronger workflow"
        in assembly.markdown
    )
    assert "## Random forests make trees less fragile" in assembly.markdown
    assert "model-assessment-lab" not in assembly.markdown


def test_assignment_assembly_compiles_multiple_exercises_without_student_solutions() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "assignment-01",
        index=index,
        audience="student",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id
        for edge in assembly.dependency_edges
        if edge.relationship == "assignment-item"
    ]

    assert assembly.target.kind == "collection"
    assert edge_targets == ["ex-iv-concept-check", "ex-iv-assumption-sort"]
    assert "## Exercise 1: IV intuition check" in assembly.markdown
    assert "## Exercise 2: IV assumption sort" in assembly.markdown
    assert "teacher-output-includes-solution" not in assembly.markdown
    assert "lf-solution-block" not in assembly.markdown
    assert all(not item.included_in_output for item in assembly.solution_observations)


def test_assignment_student_sheet_matches_snapshot() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "assignment-01",
        index=index,
        audience="student",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )
    snapshot = (
        REPO_ROOT / "tests" / "snapshots" / "assignment-01.student.en.exercise-sheet.qmd"
    ).read_text(encoding="utf-8").rstrip()

    assert assignment_snapshot_fragment(assembly.markdown) == snapshot


def test_teacher_assignment_assembly_includes_solution_sections() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "assignment-01",
        index=index,
        audience="teacher",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )

    assert "Teacher Solution Sheet" in assembly.markdown
    assert "lf-solution-block" in assembly.markdown
    assert "strong first stage" in assembly.markdown
    assert all(item.included_in_output for item in assembly.solution_observations)


def test_assignment_html_assembly_includes_course_concepts_and_resources() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "assignment-01",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert "## Assignment details" in assembly.markdown
    assert "## Included exercises" in assembly.markdown
    assert "## Linked concepts" in assembly.markdown
    assert "## Related resources" in assembly.markdown
    assert "Course context" in assembly.markdown
    assert "iv-intuition" in related_ids
    assert "angrist-podcast-iv" in related_ids
    assert "ec202" in related_ids
    assert len(assembly.solution_observations) == 2
    assert all(not item.included_in_output for item in assembly.solution_observations)


def test_topic_listing_matches_snapshot() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "topic-causal-inference",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    snapshot = (
        REPO_ROOT / "tests" / "snapshots" / "topic-causal-inference.student.en.html.qmd"
    ).read_text(encoding="utf-8").rstrip()

    assert topic_snapshot_fragment(assembly.markdown) == snapshot


def test_resource_page_generates_related_content() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "angrist-podcast-iv",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert "iv-intuition" in related_ids
    assert "lecture-04" in related_ids
    assert "## Related links" in assembly.markdown


def test_teacher_resource_inbox_assembly_surfaces_candidate_reviewed_and_stale_resources() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "resource-inbox",
        index=index,
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    listed_ids = [entry.identifier for entry in assembly.listing_entries]

    assert assembly.target.kind == "resource-inbox"
    assert "## Workflow summary" in assembly.markdown
    assert "## Candidate resources" in assembly.markdown
    assert "## Reviewed resources" in assembly.markdown
    assert "## Stale resources" in assembly.markdown
    assert "iv-candidate-newsletter" in listed_ids
    assert "iv-reviewed-primer" in listed_ids
    assert "iv-policy-brief-stale" in listed_ids
    assert assembly.resource_workflow_summary["status_counts"]["candidate"] == 1


def test_student_cannot_assemble_candidate_resource_page() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)

    with pytest.raises(AssemblyError):
        assemble_target(
            "iv-candidate-newsletter",
            index=index,
            audience="student",
            language="en",
            output_format="html",
            root=REPO_ROOT,
        )


def test_concept_page_includes_assignment_context() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "iv-intuition",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    assert "## Used in assignments" in assembly.markdown
    assert "assignment-01/assignment-01.html" in assembly.markdown


def test_tem0052_concept_page_links_promoted_exercise() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "bias-variance-tradeoff",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert "knn-supervised-learning" in related_ids
    assert "naive-bayes-classification" in related_ids
    assert "linear-regression-prediction" in related_ids
    assert "penalized-linear-models" in related_ids
    assert "logistic-regression-classification" in related_ids
    assert "model-assessment-lab" in related_ids
    assert "house-prices-regression" in related_ids
    assert "spam-filtering-naive-bayes" in related_ids
    assert "tem0052" in [entry.identifier for entry in assembly.related_entries]
    assert "## Related links" in assembly.markdown


def test_model_selection_concept_links_related_tem0052_content() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "model-selection-cross-validation",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert "bias-variance-tradeoff" in related_ids
    assert "knn-supervised-learning" in related_ids
    assert "naive-bayes-classification" in related_ids
    assert "linear-regression-prediction" in related_ids
    assert "penalized-linear-models" in related_ids
    assert "logistic-regression-classification" in related_ids
    assert "model-assessment-lab" in related_ids
    assert "house-prices-regression" in related_ids
    assert "spam-filtering-naive-bayes" in related_ids
    assert "tem0052" in related_ids
    assert "## Related links" in assembly.markdown


def test_linear_regression_concept_links_house_prices_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "linear-regression-prediction",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert "house-prices-regression" in related_ids
    assert "model-selection-cross-validation" in related_ids
    assert "bias-variance-tradeoff" in related_ids
    assert "penalized-linear-models" in related_ids
    assert "tem0052" in related_ids
    assert "## Related links" in assembly.markdown


def test_penalized_models_concept_links_tem0052_regression_content() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "penalized-linear-models",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert "linear-regression-prediction" in related_ids
    assert "house-prices-regression" in related_ids
    assert "model-selection-cross-validation" in related_ids
    assert "bias-variance-tradeoff" in related_ids
    assert "tem0052" in related_ids
    assert "## Related links" in assembly.markdown


def test_logistic_regression_concept_links_tem0052_classification_content() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "logistic-regression-classification",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert "knn-supervised-learning" in related_ids
    assert "naive-bayes-classification" in related_ids
    assert "linear-regression-prediction" in related_ids
    assert "model-selection-cross-validation" in related_ids
    assert "bias-variance-tradeoff" in related_ids
    assert "model-assessment-lab" in related_ids
    assert "spam-filtering-naive-bayes" in related_ids
    assert "tem0052" in related_ids
    assert "## Related links" in assembly.markdown


def test_knn_concept_links_tem0052_classification_content() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "knn-supervised-learning",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert "logistic-regression-classification" in related_ids
    assert "naive-bayes-classification" in related_ids
    assert "model-selection-cross-validation" in related_ids
    assert "bias-variance-tradeoff" in related_ids
    assert "model-assessment-lab" in related_ids
    assert "spam-filtering-naive-bayes" in related_ids
    assert "tem0052" in related_ids
    assert "## Related links" in assembly.markdown


def test_house_prices_exercise_links_tem0052_concepts_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "house-prices-regression",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert "linear-regression-prediction" in related_ids
    assert "penalized-linear-models" in related_ids
    assert "bias-variance-tradeoff" in related_ids
    assert "model-selection-cross-validation" in related_ids
    assert "tem0052" in related_ids
    assert "## Related links" in assembly.markdown


def test_model_assessment_exercise_links_tem0052_classification_concepts() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "model-assessment-lab",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert "bias-variance-tradeoff" in related_ids
    assert "knn-supervised-learning" in related_ids
    assert "model-selection-cross-validation" in related_ids
    assert "logistic-regression-classification" in related_ids
    assert "tem0052" in related_ids
    assert "## Related links" in assembly.markdown


def test_spam_filtering_exercise_links_tem0052_classification_concepts() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "spam-filtering-naive-bayes",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert "bias-variance-tradeoff" in related_ids
    assert "knn-supervised-learning" in related_ids
    assert "naive-bayes-classification" in related_ids
    assert "model-selection-cross-validation" in related_ids
    assert "logistic-regression-classification" in related_ids
    assert "tem0052" in related_ids
    assert "## Related links" in assembly.markdown


def test_naive_bayes_concept_links_tem0052_classification_content() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "naive-bayes-classification",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert "knn-supervised-learning" in related_ids
    assert "logistic-regression-classification" in related_ids
    assert "model-selection-cross-validation" in related_ids
    assert "bias-variance-tradeoff" in related_ids
    assert "spam-filtering-naive-bayes" in related_ids
    assert "tem0052" in related_ids
    assert "## Related links" in assembly.markdown


def test_concept_page_embeds_reusable_figure_with_interactive_html_path() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "iv-intuition",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    assert "## Figures" in assembly.markdown
    assert "### IV DAG" in assembly.markdown
    assert 'data-figure-id="iv-dag-figure"' in assembly.markdown
    assert "Highlight relevance" in assembly.markdown
    assert any(
        item.figure_id == "iv-dag-figure"
        and item.context_target_id == "iv-intuition"
        and item.interactive_included
        for item in assembly.figure_observations
    )


def test_student_figure_page_matches_snapshot() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "iv-dag-figure",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    snapshot = (
        REPO_ROOT / "tests" / "snapshots" / "iv-dag-figure.student.en.html.qmd"
    ).read_text(encoding="utf-8").rstrip()

    assert figure_snapshot_fragment(assembly.markdown) == snapshot


def test_home_page_assembly_includes_course_and_topic_navigation() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "home",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    assert assembly.target.kind == "home"
    assert "## Browse by Course" in assembly.markdown
    assert "## Browse by Topic" in assembly.markdown
    assert "course/ec202/ec202.html" in assembly.markdown
    assert "listing/topic-causal-inference/topic-causal-inference.html" in assembly.markdown


def test_language_switch_falls_back_when_counterpart_is_not_approved(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    meta_path = tmp_path / "content" / "resources" / "angrist-podcast-iv" / "meta.yml"
    meta_path.write_text(
        meta_path.read_text(encoding="utf-8").replace("nb: approved", "nb: machine_draft", 1),
        encoding="utf-8",
    )

    index, _ = load_repository(tmp_path, collect_errors=False)
    assembly = assemble_target(
        "angrist-podcast-iv",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=tmp_path,
    )

    assert "Norsk home" in assembly.markdown
    assert "build/exports/student/nb/html/resource/angrist-podcast-iv" not in assembly.markdown

    with pytest.raises(AssemblyError):
        assemble_target(
            "angrist-podcast-iv",
            index=index,
            audience="student",
            language="nb",
            output_format="html",
            root=tmp_path,
        )


def copy_repo_subset(target_root: Path) -> None:
    for relative_path in ("content", "collections", "courses"):
        shutil.copytree(REPO_ROOT / relative_path, target_root / relative_path)


def topic_snapshot_fragment(markdown: str) -> str:
    start = markdown.index("Topic: Causal Inference")
    end = markdown.index('<footer class="lf-page-footer">')
    return markdown[start:end].rstrip()


def assignment_snapshot_fragment(markdown: str) -> str:
    start = markdown.index("## Exercise sheet")
    end = markdown.index("## Exercise 2: IV assumption sort")
    end = markdown.index("this month.", end) + len("this month.")
    return markdown[start:end].rstrip()


def figure_snapshot_fragment(markdown: str) -> str:
    start = markdown.index("## Figure details")
    end = markdown.index("## Used in these courses")
    return markdown[start:end].rstrip()
