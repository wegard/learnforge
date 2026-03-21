from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

import app.build as build_module
from app.build import build_target, write_student_site_search_index
from app.config import REPO_ROOT
from app.indexer import load_repository


def test_student_build_writes_manifests_and_clean_leakage_report() -> None:
    artifact = build_target(
        "iv-intuition",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    student_html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    dependency_manifest = json.loads(artifact.dependency_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert artifact.output_path.exists()
    assert artifact.build_manifest_path.exists()
    assert artifact.dependency_manifest_path.exists()
    assert artifact.leakage_report_path.exists()
    assert artifact.search_index_path is not None
    assert artifact.search_index_path.exists()
    assert "Prompt the room" not in student_html
    assert "Related links" in student_html
    assert "Search LearnForge" in student_html
    assert "Language:" in student_html
    assert build_manifest["target"]["identifier"] == "iv-intuition"
    assert build_manifest["figure_observation_count"] == 1
    assert build_manifest["figure_uses"][0]["figure_id"] == "iv-dag-figure"
    assert build_manifest["figure_uses"][0]["interactive_included"] is True
    assert (
        build_manifest["search_index_path"]
        == "build/exports/student/en/html/assets/search-index.json"
    )
    assert any(
        edge["target_id"] == "lecture-04" for edge in dependency_manifest["dependency_edges"]
    )
    assert leakage_report["status"] == "clean"
    assert leakage_report["teacher_blocks_found"] == 1
    assert leakage_report["teacher_blocks_removed"] == 1


def test_course_page_build_contains_generated_listings() -> None:
    artifact = build_target(
        "ec202",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))

    assert "Topics" in html
    assert "Exercises" in html
    assert "Assignments" in html
    assert "Resources" in html
    assert "Search LearnForge" in html
    assert "Breadcrumbs:" in html
    assert 'data-page-style="explore"' in html
    assert 'class="lf-shell-toggle"' in html
    assert 'class="lf-card-grid"' in html
    assert "../../collection/assignment-01/assignment-01.html" in html
    assert "../../listing/topic-causal-inference/topic-causal-inference.html" in html
    assert "../../listing/resources-ec202/resources-ec202.html" in html
    assert "../../exercise/ex-iv-concept-check/ex-iv-concept-check.html" in html
    assert 'class="lf-view-switch"' in html
    assert "../../../../../teacher/en/html/course/ec202/ec202.html" in html
    assert "topic-causal-inference" in build_manifest["referenced_listing_targets"]
    assert "resources-ec202" in build_manifest["referenced_listing_targets"]
    assert "../../assets/learnforge-shell.css" in html
    assert "../../assets/learnforge-shell.js" in html


def test_student_build_writes_shell_assets_and_home_uses_root_relative_paths() -> None:
    course_artifact = build_target(
        "ec202",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    home_artifact = build_target(
        "home",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    asset_dir = course_artifact.output_path.parents[2] / "assets"
    css_path = asset_dir / "learnforge-shell.css"
    js_path = asset_dir / "learnforge-shell.js"
    home_html = home_artifact.output_path.read_text(encoding="utf-8")

    assert css_path.exists()
    assert js_path.exists()
    assert css_path.read_text(encoding="utf-8")
    assert js_path.read_text(encoding="utf-8")
    assert "assets/learnforge-shell.css" in home_html
    assert "assets/learnforge-shell.js" in home_html
    assert 'class="lf-view-switch"' not in home_html


def test_teacher_build_writes_shell_assets_and_page_uses_review_shell() -> None:
    build_target(
        "assignment-01",
        audience="teacher",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )
    artifact = build_target(
        "assignment-01",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    asset_dir = artifact.output_path.parents[2] / "assets"
    css_path = asset_dir / "learnforge-shell.css"
    js_path = asset_dir / "learnforge-shell.js"

    assert css_path.exists()
    assert js_path.exists()
    assert "../../assets/learnforge-shell.css" in html
    assert "../../assets/learnforge-shell.js" in html
    assert 'data-audience="teacher"' in html
    assert 'class="lf-preview-notice"' in html
    assert "Instructor preview only." in html
    assert 'class="lf-review-panel lf-meta-panel"' in html
    assert 'class="lf-view-switch"' in html
    assert "../../../../../student/en/html/collection/assignment-01/assignment-01.html" in html
    assert 'class="lf-search-form"' not in html


def test_tem0052_course_page_builds_with_first_promoted_lecture_and_exercise() -> None:
    artifact = build_target(
        "tem0052",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")

    assert "TEM 0052 - Predictive Modelling with Machine Learning" in html
    assert "Browse by Course" not in html
    assert "Course Overview" in html
    assert "../../collection/tem0052-lecture-01/tem0052-lecture-01.html" in html
    assert "../../collection/tem0052-lecture-02/tem0052-lecture-02.html" in html
    assert "../../collection/tem0052-lecture-03/tem0052-lecture-03.html" in html
    assert "../../collection/tem0052-lecture-04/tem0052-lecture-04.html" in html
    assert "../../collection/tem0052-lecture-05/tem0052-lecture-05.html" in html
    assert "../../collection/tem0052-lecture-06/tem0052-lecture-06.html" in html
    assert "../../collection/tem0052-lecture-07/tem0052-lecture-07.html" in html
    assert "../../exercise/titanic-data-preprocessing/titanic-data-preprocessing.html" in html
    assert "../../exercise/model-assessment-lab/model-assessment-lab.html" in html
    assert "../../exercise/house-prices-regression/house-prices-regression.html" in html
    assert "../../exercise/spam-filtering-naive-bayes/spam-filtering-naive-bayes.html" in html
    assert (
        "../../exercise/income-classification-ensemble/income-classification-ensemble.html" in html
    )
    assert "../../exercise/unsupervised-learning-lab/unsupervised-learning-lab.html" in html
    assert "Lecture 1 - Foundations and preprocessing pipelines" in html
    assert "Lecture 2 - Linear prediction and regularization" in html
    assert "Lecture 3 - Classification methods" in html
    assert "Lecture 4 - Model assessment and the bias-variance trade-off" in html
    assert "Lecture 5 - Model selection, evaluation, and assessment" in html
    assert "Lecture 6 - Unsupervised learning with PCA and k-means" in html
    assert "Lecture 7 - Ensemble methods and random forests" in html
    assert "Titanic data preprocessing lab" in html
    assert "Model assessment lab" in html
    assert "House-price prediction" in html
    assert "Spam filtering with naive Bayes" in html
    assert "Income classification with ensembles" in html
    assert "Unsupervised learning with PCA and k-means" in html
    assert "No entries." in html
    assert "resources-tem0052" not in html
    assert "Search LearnForge" in html


def test_bik2551_course_page_builds_in_english() -> None:
    artifact = build_target(
        "bik2551",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")

    assert "BIK 2551 - Artificial Intelligence for Increased Productivity" in html
    assert "Lectures" in html
    assert "Assignments" in html
    assert "Resources" in html
    assert "../../collection/bik2551-day-01/bik2551-day-01.html" in html
    assert "../../collection/bik2551-day-04/bik2551-day-04.html" in html
    assert "../../collection/bik2551-project-brief/bik2551-project-brief.html" in html
    assert "Day 4 - Strategy, Leadership, and the Future of Work" in html
    assert "NotebookLM for source-grounded work" in html
    assert "Project brief - project assignment and mini-experiment" in html
    assert "Kursoversikt" not in html


def test_bik2550_teacher_course_page_builds_with_project_assignment() -> None:
    artifact = build_target(
        "bik2550",
        audience="teacher",
        language="nb",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")

    assert "BIK 2550 - AI i finansnæringen" in html
    assert "Forelesninger" in html
    assert "Oppgaveark" in html
    assert 'class="lf-preview-notice"' in html
    assert "../../collection/bik2550-m1d1/bik2550-m1d1.html" in html
    assert "../../collection/bik2550-project-brief/bik2550-project-brief.html" in html
    assert "Oppgaveark - prosjektoppgave og refleksjon i AI for finans" in html


def test_bik2550_teacher_assignment_page_builds_in_norwegian() -> None:
    build_target(
        "bik2550-project-brief",
        audience="teacher",
        language="nb",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )
    artifact = build_target(
        "bik2550-project-brief",
        audience="teacher",
        language="nb",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))

    assert "Oppgavearkdetaljer" in html
    assert "Inkluderte oppgaver" in html
    assert "Kurskontekst" in html
    assert "Knyttede begreper" in html
    assert "../../course/bik2550/bik2550.html" in html
    assert "bik2550-project-brief-solution-sheet.pdf" in html
    assert "Relaterte ressurser" not in html
    assert 'class="lf-preview-notice"' in html
    assert build_manifest["assignment"]["included_exercise_ids"] == [
        "ai-finance-individual-reflection",
        "ai-finance-project-scope",
        "ai-finance-solution-blueprint",
    ]
    assert build_manifest["assignment"]["course_context_ids"] == ["bik2550"]
    assert build_manifest["assignment"]["linked_concept_ids"] == [
        "ai-applications-finance-summary",
        "ai-in-finance-landscape",
        "llms-deep-dive",
        "ml-finance-demo",
        "ml-supervised-learning-overview",
        "ml-unsupervised-learning-overview",
        "multimodality-in-finance",
        "neural-networks-introduction",
        "nlp-text-data-finance",
    ]
    assert build_manifest["assignment"]["linked_resource_ids"] == []
    assert build_manifest["assignment"]["included_solution_files"] == []


def test_bik2550_teacher_concept_page_builds_with_migrated_evaluation_figures() -> None:
    artifact = build_target(
        "ml-model-evaluation-overview",
        audience="teacher",
        language="nb",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))

    assert "Evaluering av maskinlæringsmodeller" in html
    assert "Figurer" in html
    assert "../../figure/confusion-matrix-figure/confusion-matrix-figure.html" in html
    assert "../../figure/training-test-error-figure/training-test-error-figure.html" in html
    assert "../../figure/gradient-descent-figure/gradient-descent-figure.html" in html
    assert "Konfusjonsmatrise" in html
    assert "Trenings- og testfeil" in html
    assert "Gradientnedstigning" in html
    assert 'class="lf-preview-notice"' in html
    assert build_manifest["figure_observation_count"] == 3
    assert {entry["figure_id"] for entry in build_manifest["figure_uses"]} == {
        "confusion-matrix-figure",
        "training-test-error-figure",
        "gradient-descent-figure",
    }
    assert all(entry["interactive_included"] is False for entry in build_manifest["figure_uses"])


def test_bik2550_teacher_figure_page_builds_in_norwegian() -> None:
    artifact = build_target(
        "confusion-matrix-figure",
        audience="teacher",
        language="nb",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Figurdetaljer" in html
    assert 'data-figure-id="confusion-matrix-figure"' in html
    assert "Konfusjonsmatrise" in html
    assert "ml-model-evaluation-overview/ml-model-evaluation-overview.html" in html
    assert "Interaktiv modus" in html
    assert "kun statisk" in html
    assert 'class="lf-preview-notice"' in html
    assert build_manifest["figure_observation_count"] == 1
    assert build_manifest["figure_uses"][0]["figure_id"] == "confusion-matrix-figure"
    assert build_manifest["figure_uses"][0]["interactive_included"] is False
    assert build_manifest["figure_uses"][0]["fallback_asset_path"].endswith("figure.svg")
    assert leakage_report["status"] == "not_applicable"


def test_bik2550_teacher_training_test_error_figure_page_builds_in_norwegian() -> None:
    artifact = build_target(
        "training-test-error-figure",
        audience="teacher",
        language="nb",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Figurdetaljer" in html
    assert 'data-figure-id="training-test-error-figure"' in html
    assert "Trenings- og testfeil" in html
    assert "ml-model-evaluation-overview/ml-model-evaluation-overview.html" in html
    assert "Interaktiv modus" in html
    assert "kun statisk" in html
    assert 'class="lf-preview-notice"' in html
    assert build_manifest["figure_observation_count"] == 1
    assert build_manifest["figure_uses"][0]["figure_id"] == "training-test-error-figure"
    assert build_manifest["figure_uses"][0]["interactive_included"] is False
    assert build_manifest["figure_uses"][0]["fallback_asset_path"].endswith("figure.svg")
    assert leakage_report["status"] == "not_applicable"


def test_bik2550_teacher_gradient_descent_figure_page_builds_in_norwegian() -> None:
    artifact = build_target(
        "gradient-descent-figure",
        audience="teacher",
        language="nb",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Figurdetaljer" in html
    assert 'data-figure-id="gradient-descent-figure"' in html
    assert "Gradientnedstigning" in html
    assert "ml-model-evaluation-overview/ml-model-evaluation-overview.html" in html
    assert "Interaktiv modus" in html
    assert "kun statisk" in html
    assert 'class="lf-preview-notice"' in html
    assert build_manifest["figure_observation_count"] == 1
    assert build_manifest["figure_uses"][0]["figure_id"] == "gradient-descent-figure"
    assert build_manifest["figure_uses"][0]["interactive_included"] is False
    assert build_manifest["figure_uses"][0]["fallback_asset_path"].endswith("figure.svg")
    assert leakage_report["status"] == "not_applicable"


def test_tem0052_concept_and_exercise_student_pages_build_cleanly() -> None:
    preprocessing_concept_artifact = build_target(
        "ml-preprocessing-pipelines",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    concept_artifact = build_target(
        "bias-variance-tradeoff",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    second_concept_artifact = build_target(
        "model-selection-cross-validation",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    third_concept_artifact = build_target(
        "linear-regression-prediction",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    fourth_concept_artifact = build_target(
        "penalized-linear-models",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    fifth_concept_artifact = build_target(
        "logistic-regression-classification",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    sixth_concept_artifact = build_target(
        "knn-supervised-learning",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    seventh_concept_artifact = build_target(
        "naive-bayes-classification",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    eighth_concept_artifact = build_target(
        "decision-tree-learning",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    ninth_concept_artifact = build_target(
        "random-forests",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    tenth_concept_artifact = build_target(
        "ensemble-methods-introduction",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    preprocessing_exercise_artifact = build_target(
        "titanic-data-preprocessing",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    exercise_artifact = build_target(
        "model-assessment-lab",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    second_exercise_artifact = build_target(
        "house-prices-regression",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    third_exercise_artifact = build_target(
        "spam-filtering-naive-bayes",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    fourth_exercise_artifact = build_target(
        "income-classification-ensemble",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    fifth_exercise_artifact = build_target(
        "unsupervised-learning-lab",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    preprocessing_concept_html = preprocessing_concept_artifact.output_path.read_text(
        encoding="utf-8"
    )
    concept_html = concept_artifact.output_path.read_text(encoding="utf-8")
    second_concept_html = second_concept_artifact.output_path.read_text(encoding="utf-8")
    third_concept_html = third_concept_artifact.output_path.read_text(encoding="utf-8")
    fourth_concept_html = fourth_concept_artifact.output_path.read_text(encoding="utf-8")
    fifth_concept_html = fifth_concept_artifact.output_path.read_text(encoding="utf-8")
    sixth_concept_html = sixth_concept_artifact.output_path.read_text(encoding="utf-8")
    seventh_concept_html = seventh_concept_artifact.output_path.read_text(encoding="utf-8")
    eighth_concept_html = eighth_concept_artifact.output_path.read_text(encoding="utf-8")
    ninth_concept_html = ninth_concept_artifact.output_path.read_text(encoding="utf-8")
    tenth_concept_html = tenth_concept_artifact.output_path.read_text(encoding="utf-8")
    preprocessing_exercise_html = preprocessing_exercise_artifact.output_path.read_text(
        encoding="utf-8"
    )
    exercise_html = exercise_artifact.output_path.read_text(encoding="utf-8")
    second_exercise_html = second_exercise_artifact.output_path.read_text(encoding="utf-8")
    third_exercise_html = third_exercise_artifact.output_path.read_text(encoding="utf-8")
    fourth_exercise_html = fourth_exercise_artifact.output_path.read_text(encoding="utf-8")
    fifth_exercise_html = fifth_exercise_artifact.output_path.read_text(encoding="utf-8")

    assert "Preprocessing pipelines for machine learning" in preprocessing_concept_html
    assert (
        "../../exercise/titanic-data-preprocessing/titanic-data-preprocessing.html"
        in preprocessing_concept_html
    )
    assert "../../course/tem0052/tem0052.html" in preprocessing_concept_html
    assert "teacher-only" not in preprocessing_concept_html

    assert "Bias-variance trade-off" in concept_html
    assert 'data-figure-id="bias-variance-tradeoff-figure"' in concept_html
    assert "../../exercise/model-assessment-lab/model-assessment-lab.html" in concept_html
    assert "../knn-supervised-learning/knn-supervised-learning.html" in concept_html
    assert "../linear-regression-prediction/linear-regression-prediction.html" in concept_html
    assert "../penalized-linear-models/penalized-linear-models.html" in concept_html
    assert (
        "../logistic-regression-classification/logistic-regression-classification.html"
        in concept_html
    )
    assert "../../course/tem0052/tem0052.html" in concept_html
    assert "teacher-only" not in concept_html
    assert (
        "../../exercise/spam-filtering-naive-bayes/spam-filtering-naive-bayes.html" in concept_html
    )

    assert "Model selection and cross-validation" in second_concept_html
    assert 'data-figure-id="k-fold-cross-validation-figure"' in second_concept_html
    assert "../bias-variance-tradeoff/bias-variance-tradeoff.html" in second_concept_html
    assert "../knn-supervised-learning/knn-supervised-learning.html" in second_concept_html
    assert (
        "../linear-regression-prediction/linear-regression-prediction.html" in second_concept_html
    )
    assert "../penalized-linear-models/penalized-linear-models.html" in second_concept_html
    assert (
        "../logistic-regression-classification/logistic-regression-classification.html"
        in second_concept_html
    )
    assert "../../exercise/model-assessment-lab/model-assessment-lab.html" in second_concept_html
    assert (
        "../../exercise/spam-filtering-naive-bayes/spam-filtering-naive-bayes.html"
        in second_concept_html
    )
    assert "teacher-only" not in second_concept_html

    assert "Linear regression for prediction" in third_concept_html
    assert (
        "../../exercise/house-prices-regression/house-prices-regression.html" in third_concept_html
    )
    assert "../penalized-linear-models/penalized-linear-models.html" in third_concept_html
    assert (
        "../model-selection-cross-validation/model-selection-cross-validation.html"
        in third_concept_html
    )
    assert "../../course/tem0052/tem0052.html" in third_concept_html
    assert "teacher-only" not in third_concept_html

    assert "Penalized linear models" in fourth_concept_html
    assert (
        "../../exercise/house-prices-regression/house-prices-regression.html" in fourth_concept_html
    )
    assert (
        "../linear-regression-prediction/linear-regression-prediction.html" in fourth_concept_html
    )
    assert (
        "../model-selection-cross-validation/model-selection-cross-validation.html"
        in fourth_concept_html
    )
    assert "../../course/tem0052/tem0052.html" in fourth_concept_html
    assert "teacher-only" not in fourth_concept_html

    assert "Logistic regression for classification" in fifth_concept_html
    assert "../../exercise/model-assessment-lab/model-assessment-lab.html" in fifth_concept_html
    assert (
        "../../exercise/spam-filtering-naive-bayes/spam-filtering-naive-bayes.html"
        in fifth_concept_html
    )
    assert "../naive-bayes-classification/naive-bayes-classification.html" in fifth_concept_html
    assert "../knn-supervised-learning/knn-supervised-learning.html" in fifth_concept_html
    assert "../linear-regression-prediction/linear-regression-prediction.html" in fifth_concept_html
    assert (
        "../model-selection-cross-validation/model-selection-cross-validation.html"
        in fifth_concept_html
    )
    assert "../../course/tem0052/tem0052.html" in fifth_concept_html
    assert "teacher-only" not in fifth_concept_html

    assert "k-nearest neighbors for supervised learning" in sixth_concept_html
    assert "../../exercise/model-assessment-lab/model-assessment-lab.html" in sixth_concept_html
    assert (
        "../../exercise/spam-filtering-naive-bayes/spam-filtering-naive-bayes.html"
        in sixth_concept_html
    )
    assert "../naive-bayes-classification/naive-bayes-classification.html" in sixth_concept_html
    assert "../decision-tree-learning/decision-tree-learning.html" in sixth_concept_html
    assert (
        "../logistic-regression-classification/logistic-regression-classification.html"
        in sixth_concept_html
    )
    assert (
        "../model-selection-cross-validation/model-selection-cross-validation.html"
        in sixth_concept_html
    )
    assert "../../course/tem0052/tem0052.html" in sixth_concept_html
    assert "teacher-only" not in sixth_concept_html

    assert "Naive Bayes for classification" in seventh_concept_html
    assert (
        "../../exercise/spam-filtering-naive-bayes/spam-filtering-naive-bayes.html"
        in seventh_concept_html
    )
    assert "../knn-supervised-learning/knn-supervised-learning.html" in seventh_concept_html
    assert (
        "../logistic-regression-classification/logistic-regression-classification.html"
        in seventh_concept_html
    )
    assert (
        "../model-selection-cross-validation/model-selection-cross-validation.html"
        in seventh_concept_html
    )
    assert "../../course/tem0052/tem0052.html" in seventh_concept_html
    assert "teacher-only" not in seventh_concept_html

    assert "Decision tree learning" in eighth_concept_html
    assert "../../exercise/model-assessment-lab/model-assessment-lab.html" in eighth_concept_html
    assert "../knn-supervised-learning/knn-supervised-learning.html" in eighth_concept_html
    assert (
        "../ensemble-methods-introduction/ensemble-methods-introduction.html" in eighth_concept_html
    )
    assert "../random-forests/random-forests.html" in eighth_concept_html
    assert (
        "../logistic-regression-classification/logistic-regression-classification.html"
        in eighth_concept_html
    )
    assert (
        "../model-selection-cross-validation/model-selection-cross-validation.html"
        in eighth_concept_html
    )
    assert "../../course/tem0052/tem0052.html" in eighth_concept_html
    assert "teacher-only" not in eighth_concept_html

    assert "Random forests" in ninth_concept_html
    assert (
        "../ensemble-methods-introduction/ensemble-methods-introduction.html" in ninth_concept_html
    )
    assert "../decision-tree-learning/decision-tree-learning.html" in ninth_concept_html
    assert "../bias-variance-tradeoff/bias-variance-tradeoff.html" in ninth_concept_html
    assert (
        "../model-selection-cross-validation/model-selection-cross-validation.html"
        in ninth_concept_html
    )
    assert (
        "../logistic-regression-classification/logistic-regression-classification.html"
        in ninth_concept_html
    )
    assert "../../course/tem0052/tem0052.html" in ninth_concept_html
    assert "teacher-only" not in ninth_concept_html

    assert "Introduction to ensemble methods" in tenth_concept_html
    assert "../random-forests/random-forests.html" in tenth_concept_html
    assert "../decision-tree-learning/decision-tree-learning.html" in tenth_concept_html
    assert "../bias-variance-tradeoff/bias-variance-tradeoff.html" in tenth_concept_html
    assert (
        "../model-selection-cross-validation/model-selection-cross-validation.html"
        in tenth_concept_html
    )
    assert "../../course/tem0052/tem0052.html" in tenth_concept_html
    assert "teacher-only" not in tenth_concept_html

    assert "Titanic data preprocessing lab" in preprocessing_exercise_html
    assert "Preprocessing pipelines for machine learning" in preprocessing_exercise_html
    assert "Logistic regression for classification" in preprocessing_exercise_html
    assert "k-nearest neighbors for supervised learning" in preprocessing_exercise_html
    assert "The safest teacher solution" not in preprocessing_exercise_html
    assert "lf-solution-block" not in preprocessing_exercise_html

    assert "Model assessment lab" in exercise_html
    assert "Bias-variance trade-off" in exercise_html
    assert "k-nearest neighbors for supervised learning" in exercise_html
    assert "Decision tree learning" in exercise_html
    assert "Model selection and cross-validation" in exercise_html
    assert "Logistic regression for classification" in exercise_html
    assert "The point of the lab is not the exact winning score." not in exercise_html
    assert "lf-solution-block" not in exercise_html

    assert "House-price prediction" in second_exercise_html
    assert "Linear regression for prediction" in second_exercise_html
    assert "Penalized linear models" in second_exercise_html
    assert "Bias-variance trade-off" in second_exercise_html
    assert "Model selection and cross-validation" in second_exercise_html
    assert "the exact ranking depends on the preprocessing rule" not in second_exercise_html
    assert "lf-solution-block" not in second_exercise_html

    assert "Spam filtering with naive Bayes" in third_exercise_html
    assert "Bias-variance trade-off" in third_exercise_html
    assert "k-nearest neighbors for supervised learning" in third_exercise_html
    assert "Naive Bayes for classification" in third_exercise_html
    assert "Model selection and cross-validation" in third_exercise_html
    assert "Logistic regression for classification" in third_exercise_html
    assert "The safest teacher solution" not in third_exercise_html
    assert "lf-solution-block" not in third_exercise_html

    assert "Income classification with ensembles" in fourth_exercise_html
    assert "Decision tree learning" in fourth_exercise_html
    assert "Introduction to ensemble methods" in fourth_exercise_html
    assert "Random forests" in fourth_exercise_html
    assert "Bias-variance trade-off" in fourth_exercise_html
    assert "The safest teacher solution" not in fourth_exercise_html
    assert "lf-solution-block" not in fourth_exercise_html

    assert "Unsupervised learning with PCA and k-means" in fifth_exercise_html
    assert "Principal component analysis" in fifth_exercise_html
    assert "K-means clustering" in fifth_exercise_html
    assert "The safest teacher solution" not in fifth_exercise_html
    assert "lf-solution-block" not in fifth_exercise_html


def test_tem0052_lecture_page_build_contains_only_promoted_objects() -> None:
    artifact = build_target(
        "tem0052-lecture-05",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(artifact.dependency_manifest_path.read_text(encoding="utf-8"))

    assert "Course context" in html
    assert "This lecture includes" in html
    assert "Model selection and cross-validation" in html
    assert 'data-figure-id="k-fold-cross-validation-figure"' in html
    assert "Bias-variance trade-off" in html
    assert "Model assessment lab" in html
    assert "iv-intuition" not in html
    assert "lecture-04" not in html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == [
        "model-selection-cross-validation",
        "k-fold-cross-validation-figure",
        "bias-variance-tradeoff",
        "model-assessment-lab",
    ]


def test_tem0052_lecture_04_build_contains_assessment_block() -> None:
    student_artifact = build_target(
        "tem0052-lecture-04",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    teacher_artifact = build_target(
        "tem0052-lecture-04",
        audience="teacher",
        language="en",
        output_format="revealjs",
        root=REPO_ROOT,
    )

    student_html = student_artifact.output_path.read_text(encoding="utf-8")
    teacher_html = teacher_artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        student_artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Course context" in student_html
    assert "This lecture includes" in student_html
    assert "Bias-variance trade-off" in student_html
    assert 'data-figure-id="bias-variance-tradeoff-figure"' in student_html
    assert "Model assessment lab" in student_html
    assert "Model selection and cross-validation" not in student_html
    assert "Lecture 4 - Model assessment and the bias-variance trade-off" in teacher_html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == [
        "bias-variance-tradeoff",
        "bias-variance-tradeoff-figure",
        "model-assessment-lab",
    ]


def test_tem0052_lecture_01_build_contains_preprocessing_block() -> None:
    student_artifact = build_target(
        "tem0052-lecture-01",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    teacher_artifact = build_target(
        "tem0052-lecture-01",
        audience="teacher",
        language="en",
        output_format="revealjs",
        root=REPO_ROOT,
    )

    student_html = student_artifact.output_path.read_text(encoding="utf-8")
    teacher_html = teacher_artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        student_artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Course context" in student_html
    assert "This lecture includes" in student_html
    assert "Preprocessing pipelines for machine learning" in student_html
    assert "Titanic data preprocessing lab" in student_html
    assert "Random forests" not in student_html
    assert "Lecture 1 - Foundations and preprocessing pipelines" in teacher_html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == [
        "ml-preprocessing-pipelines",
        "titanic-data-preprocessing",
    ]


def test_tem0052_lecture_02_build_contains_regression_block() -> None:
    student_artifact = build_target(
        "tem0052-lecture-02",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    teacher_artifact = build_target(
        "tem0052-lecture-02",
        audience="teacher",
        language="en",
        output_format="revealjs",
        root=REPO_ROOT,
    )

    student_html = student_artifact.output_path.read_text(encoding="utf-8")
    teacher_html = teacher_artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        student_artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Course context" in student_html
    assert "This lecture includes" in student_html
    assert "Linear regression for prediction" in student_html
    assert "Penalized linear models" in student_html
    assert "House-price prediction" in student_html
    assert "Logistic regression for classification" not in student_html
    assert "Lecture 2 - Linear prediction and regularization" in teacher_html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == [
        "linear-regression-prediction",
        "penalized-linear-models",
        "house-prices-regression",
    ]


def test_tem0052_lecture_03_build_contains_classification_block() -> None:
    student_artifact = build_target(
        "tem0052-lecture-03",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    teacher_artifact = build_target(
        "tem0052-lecture-03",
        audience="teacher",
        language="en",
        output_format="revealjs",
        root=REPO_ROOT,
    )

    student_html = student_artifact.output_path.read_text(encoding="utf-8")
    teacher_html = teacher_artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        student_artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Course context" in student_html
    assert "This lecture includes" in student_html
    assert "k-nearest neighbors for supervised learning" in student_html
    assert "Logistic regression for classification" in student_html
    assert "Naive Bayes for classification" in student_html
    assert "Spam filtering with naive Bayes" in student_html
    assert "Model assessment lab" not in student_html
    assert "House-price prediction" not in student_html
    assert "Lecture 3 - Classification methods" in teacher_html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == [
        "knn-supervised-learning",
        "logistic-regression-classification",
        "naive-bayes-classification",
        "spam-filtering-naive-bayes",
    ]


def test_tem0052_lecture_07_build_contains_tree_ensemble_block() -> None:
    student_artifact = build_target(
        "tem0052-lecture-07",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    teacher_artifact = build_target(
        "tem0052-lecture-07",
        audience="teacher",
        language="en",
        output_format="revealjs",
        root=REPO_ROOT,
    )

    student_html = student_artifact.output_path.read_text(encoding="utf-8")
    teacher_html = teacher_artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        student_artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Course context" in student_html
    assert "This lecture includes" in student_html
    assert "Decision tree learning" in student_html
    assert "Introduction to ensemble methods" in student_html
    assert "Random forests" in student_html
    assert "Income classification with ensembles" in student_html
    assert "Model assessment lab" not in student_html
    assert "Lecture 7 - Ensemble methods and random forests" in teacher_html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == [
        "decision-tree-learning",
        "ensemble-methods-introduction",
        "random-forests",
        "income-classification-ensemble",
    ]


def test_tem0052_lecture_06_build_contains_unsupervised_block() -> None:
    student_artifact = build_target(
        "tem0052-lecture-06",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    teacher_artifact = build_target(
        "tem0052-lecture-06",
        audience="teacher",
        language="en",
        output_format="revealjs",
        root=REPO_ROOT,
    )

    student_html = student_artifact.output_path.read_text(encoding="utf-8")
    teacher_html = teacher_artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        student_artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Course context" in student_html
    assert "This lecture includes" in student_html
    assert "Principal component analysis" in student_html
    assert "K-means clustering" in student_html
    assert "Unsupervised learning with PCA and k-means" in student_html
    assert "Model assessment lab" not in student_html
    assert "Lecture 6 - Unsupervised learning with PCA and k-means" in teacher_html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == [
        "principal-component-analysis",
        "k-means-clustering",
        "unsupervised-learning-lab",
    ]


def test_listing_build_writes_reports() -> None:
    artifact = build_target(
        "topic-causal-inference",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(artifact.dependency_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Causal Inference" in html
    assert "Breadcrumbs:" in html
    assert any(
        edge["relationship"] == "topic-match" for edge in dependency_manifest["dependency_edges"]
    )
    assert leakage_report["status"] == "clean"


def test_student_resource_page_build_is_only_for_published_resource() -> None:
    artifact = build_target(
        "angrist-podcast-iv",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Resource details" in html
    assert "Workflow state" in html
    assert "published" in html
    assert "Instructor note" not in html
    assert build_manifest["resource_workflow"]["resource"]["visible_to_student"] is True
    assert leakage_report["status"] == "clean"


def test_student_resource_listing_excludes_non_approved_and_stale_resources() -> None:
    artifact = build_target(
        "resources-ec202",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "angrist-podcast-iv" in html
    assert "iv-candidate-newsletter" not in html
    assert "iv-reviewed-primer" not in html
    assert "iv-policy-brief-stale" not in html
    assert build_manifest["resource_workflow"]["included_resource_ids"] == ["angrist-podcast-iv"]
    assert {item["id"] for item in build_manifest["resource_workflow"]["excluded_resources"]} == {
        "iv-candidate-newsletter",
        "iv-reviewed-primer",
        "iv-policy-brief-stale",
    }
    assert leakage_report["status"] == "clean"


def test_teacher_resource_inbox_build_surfaces_candidate_reviewed_and_stale_resources() -> None:
    artifact = build_target(
        "resource-inbox",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))

    assert "Resource Inbox" in html
    assert "Candidate resources" in html
    assert "Reviewed resources" in html
    assert "Stale resources" in html
    assert 'data-audience="teacher"' in html
    assert 'data-page-style="explore"' in html
    assert 'class="lf-preview-notice"' in html
    assert 'class="lf-review-panel lf-meta-panel"' in html
    assert 'class="lf-view-switch"' not in html
    assert 'class="lf-search-form"' not in html
    assert "iv-candidate-newsletter" in html
    assert "iv-reviewed-primer" in html
    assert "iv-policy-brief-stale" in html
    workflow = build_manifest["resource_workflow"]["status_counts"]
    assert workflow["candidate"] >= 1
    assert workflow["reviewed"] >= 1
    assert workflow["approved"] >= 1
    assert workflow["published"] >= 1


def test_home_page_build_contains_navigation_and_search() -> None:
    artifact = build_target(
        "home",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    search_index = json.loads(artifact.search_index_path.read_text(encoding="utf-8"))

    assert artifact.output_path.name == "index.html"
    assert "Browse by Course" in html
    assert "Browse by Topic" in html
    assert "Featured Resources" in html
    assert "Search LearnForge" in html
    assert 'href="course/ec202/ec202.html"' in html
    assert 'data-page-style="explore"' in html
    assert 'class="lf-shell-toggle"' in html
    assert 'id="lf-shell-nav"' in html
    assert 'id="lf-shell-search"' in html
    assert any(entry["id"] == "home" for entry in search_index["entries"])
    assert any(entry["id"] == "ec202" for entry in search_index["entries"])
    assert any(entry["id"] == "assignment-01" for entry in search_index["entries"])


def test_student_lecture_page_has_course_context_breadcrumbs_and_export_links() -> None:
    build_target(
        "lecture-04",
        audience="student",
        language="en",
        output_format="revealjs",
        root=REPO_ROOT,
    )
    build_target(
        "lecture-04",
        audience="student",
        language="en",
        output_format="pdf",
        root=REPO_ROOT,
    )
    artifact = build_target(
        "lecture-04",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")

    assert "Course context" in html
    assert "EC202 - Applied Econometrics" in html
    assert "Breadcrumbs:" in html
    assert "Slides" in html
    assert "PDF" in html
    assert 'data-figure-id="iv-dag-figure"' in html
    assert "Highlight relevance" in html


def test_student_lecture_page_shows_slide_pdf_export_when_available(monkeypatch) -> None:
    def fake_export(*, revealjs_output_path: Path, output_path: Path, root: Path) -> list[str]:
        assert revealjs_output_path.name == "lecture-04.html"
        assert revealjs_output_path.exists()
        output_path.write_bytes(b"%PDF-1.4\n% slide pdf test\n")
        return ["fake-browser", f"--print-to-pdf={output_path}"]

    monkeypatch.setattr(build_module, "export_revealjs_pdf", fake_export)

    slides_artifact = build_target(
        "lecture-04",
        audience="student",
        language="en",
        output_format="slides-pdf",
        root=REPO_ROOT,
    )
    html_artifact = build_target(
        "lecture-04",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = html_artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(slides_artifact.build_manifest_path.read_text(encoding="utf-8"))

    assert slides_artifact.output_path.exists()
    assert slides_artifact.output_path.name == "lecture-04-slides.pdf"
    assert "../../slides-pdf/collection/lecture-04/lecture-04-slides.pdf" in html
    assert "Slide PDF" in html
    assert build_manifest["output_path"] == (
        "build/exports/student/en/slides-pdf/collection/lecture-04/lecture-04-slides.pdf"
    )
    assert {item["format"] for item in build_manifest["generated_artifacts"]} >= {
        "slides-pdf",
    }
    assert len(build_manifest["commands"]) == 2


def test_teacher_lecture_reveal_build_reports_static_figure_fallback() -> None:
    artifact = build_target(
        "lecture-04",
        audience="teacher",
        language="nb",
        output_format="revealjs",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))

    assert 'data-figure-id="iv-dag-figure"' in html
    assert "Highlight relevance" not in html
    assert build_manifest["figure_observation_count"] == 1
    assert build_manifest["figure_uses"][0]["interactive_included"] is False
    assert build_manifest["figure_uses"][0]["fallback_asset_path"].endswith("figure.svg")


def test_student_exercise_page_has_language_switch_and_related_links() -> None:
    artifact = build_target(
        "ex-iv-concept-check",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")

    assert "Exercise details" in html
    assert "Related links" in html
    assert "Used in assignments" in html
    assert "Language:" in html
    assert "Norwegian" in html
    assert "Sjekk av IV-intuisjon" not in html
    assert "strong first stage" not in html
    assert 'class="lf-view-switch"' in html
    assert (
        "../../../../../teacher/en/html/exercise/ex-iv-concept-check/"
        "ex-iv-concept-check.html" in html
    )
    assert "../../collection/assignment-01/assignment-01.html" in html


def test_student_assignment_page_build_has_navigation_exports_and_clean_leakage() -> None:
    build_target(
        "assignment-01",
        audience="student",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )
    artifact = build_target(
        "assignment-01",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Assignment details" in html
    assert "Included exercises" in html
    assert "Course context" in html
    assert "Related resources" in html
    assert "Search LearnForge" in html
    assert "Breadcrumbs:" in html
    assert "../../course/ec202/ec202.html" in html
    assert "assignment-01-exercise-sheet.pdf" in html
    assert "assignment-01-solution-sheet.pdf" not in html
    assert build_manifest["assignment"]["included_exercise_ids"] == [
        "ex-iv-assumption-sort",
        "ex-iv-concept-check",
    ]
    assert build_manifest["assignment"]["course_context_ids"] == ["ec202"]
    assert build_manifest["assignment"]["linked_concept_ids"] == ["iv-intuition"]
    assert build_manifest["assignment"]["linked_resource_ids"] == ["angrist-podcast-iv"]
    assert build_manifest["assignment"]["included_solution_files"] == []
    assert {item["format"] for item in build_manifest["generated_artifacts"]} >= {
        "html",
        "exercise-sheet",
    }
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 2
    assert leakage_report["solution_files_included"] == 0


def test_student_figure_page_build_has_interactive_markup_and_manifest() -> None:
    artifact = build_target(
        "iv-dag-figure",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Figure details" in html
    assert 'data-figure-id="iv-dag-figure"' in html
    assert "Highlight relevance" in html
    assert build_manifest["figure_observation_count"] == 1
    assert build_manifest["figure_uses"][0]["interactive_included"] is True
    assert build_manifest["figure_uses"][0]["fallback_asset_path"].endswith("figure.svg")
    assert leakage_report["status"] == "clean"


def test_student_tem0052_figure_page_build_has_static_markup_and_manifest() -> None:
    artifact = build_target(
        "k-fold-cross-validation-figure",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Figure details" in html
    assert 'data-figure-id="k-fold-cross-validation-figure"' in html
    assert "K-fold cross-validation" in html
    assert "Highlight relevance" not in html
    assert build_manifest["figure_observation_count"] == 1
    assert build_manifest["figure_uses"][0]["interactive_included"] is False
    assert build_manifest["figure_uses"][0]["fallback_asset_path"].endswith("figure.svg")
    assert leakage_report["status"] == "clean"


def test_teacher_figure_pdf_build_uses_pdf_fallback() -> None:
    artifact = build_target(
        "iv-dag-figure",
        audience="teacher",
        language="en",
        output_format="pdf",
        root=REPO_ROOT,
    )

    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))

    assert artifact.output_path.exists()
    assert artifact.output_path.name == "iv-dag-figure.pdf"
    assert build_manifest["figure_observation_count"] == 1
    assert build_manifest["figure_uses"][0]["interactive_included"] is False
    assert build_manifest["figure_uses"][0]["fallback_asset_path"].endswith("figure.pdf")


def test_teacher_tem0052_figure_pdf_build_uses_pdf_fallback() -> None:
    artifact = build_target(
        "k-fold-cross-validation-figure",
        audience="teacher",
        language="en",
        output_format="pdf",
        root=REPO_ROOT,
    )

    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))

    assert artifact.output_path.exists()
    assert artifact.output_path.name == "k-fold-cross-validation-figure.pdf"
    assert build_manifest["figure_observation_count"] == 1
    assert build_manifest["figure_uses"][0]["interactive_included"] is False
    assert build_manifest["figure_uses"][0]["fallback_asset_path"].endswith("figure.pdf")


def test_teacher_assignment_page_shows_teacher_export_only() -> None:
    build_target(
        "assignment-01",
        audience="teacher",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )
    artifact = build_target(
        "assignment-01",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))

    assert "Available outputs" in html
    assert "assignment-01-solution-sheet.pdf" in html
    assert "assignment-01-exercise-sheet.pdf" not in html
    assert 'class="lf-preview-notice"' in html
    assert 'class="lf-review-panel lf-meta-panel"' in html
    assert "../../../../../student/en/html/collection/assignment-01/assignment-01.html" in html
    assert build_manifest["assignment"]["included_solution_files"] == []
    assert {item["format"] for item in build_manifest["generated_artifacts"]} >= {
        "html",
        "exercise-sheet",
    }


def test_student_assignment_sheet_build_excludes_solution_content_and_reports_clean() -> None:
    artifact = build_target(
        "assignment-01",
        audience="student",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )

    generated = artifact.source_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    dependency_manifest = json.loads(artifact.dependency_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert artifact.output_path.exists()
    assert artifact.output_path.name == "assignment-01-exercise-sheet.pdf"
    assert "## Exercise sheet" in generated
    assert "strong first stage" not in generated
    assert "lf-solution-block" not in generated
    assert build_manifest["target"]["identifier"] == "assignment-01"
    assert build_manifest["output_path"] == (
        "build/exports/student/en/exercise-sheet/collection/assignment-01/"
        "assignment-01-exercise-sheet.pdf"
    )
    assert any(
        edge["relationship"] == "assignment-item" and edge["target_id"] == "ex-iv-assumption-sort"
        for edge in dependency_manifest["dependency_edges"]
    )
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 2
    assert leakage_report["solution_files_included"] == 0
    assert not leakage_report["generated_source_contains_solution_marker"]
    assert all(not item["included_in_output"] for item in leakage_report["solution_details"])


def test_teacher_solution_sheet_build_includes_solution_content() -> None:
    artifact = build_target(
        "assignment-01",
        audience="teacher",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )

    generated = artifact.source_path.read_text(encoding="utf-8")
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert artifact.output_path.exists()
    assert artifact.output_path.name == "assignment-01-solution-sheet.pdf"
    assert "Teacher solution sheet" in generated
    assert "strong first stage" in generated
    assert "lf-solution-block" in generated
    assert leakage_report["status"] == "not_applicable"
    assert leakage_report["solution_files_found"] == 2
    assert leakage_report["solution_files_included"] == 2


def test_building_nb_home_search_index_excludes_unapproved_translation(tmp_path) -> None:
    copy_repo_subset(tmp_path)
    meta_path = tmp_path / "content" / "resources" / "angrist-podcast-iv" / "meta.yml"
    meta_path.write_text(
        meta_path.read_text(encoding="utf-8").replace("nb: approved", "nb: machine_draft", 1),
        encoding="utf-8",
    )

    index, _ = load_repository(tmp_path, collect_errors=False)
    search_index_path = write_student_site_search_index(index=index, language="nb", root=tmp_path)
    payload = json.loads(search_index_path.read_text(encoding="utf-8"))

    assert all(entry["id"] != "angrist-podcast-iv" for entry in payload["entries"])
    assert all(entry["id"] != "iv-candidate-newsletter" for entry in payload["entries"])


def test_student_build_rejects_stale_resource_page() -> None:
    from app.build import BuildError

    with pytest.raises(BuildError):
        build_target(
            "iv-policy-brief-stale",
            audience="student",
            language="en",
            output_format="html",
            root=REPO_ROOT,
        )


def test_d3_figure_student_html_build_includes_interactive_d3() -> None:
    artifact = build_target(
        "bias-variance-tradeoff-figure",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))

    assert 'data-figure-id="bias-variance-tradeoff-figure"' in html
    assert "// @learnforge:requires d3" in html
    assert ".select(surface)" in html
    assert "// https://d3js.org" in html
    assert build_manifest["figure_uses"][0]["figure_id"] == "bias-variance-tradeoff-figure"
    assert build_manifest["figure_uses"][0]["interactive_included"] is True
    assert build_manifest["figure_uses"][0]["d3_included"] is True


def test_d3_figure_pdf_build_uses_static_fallback() -> None:
    artifact = build_target(
        "bias-variance-tradeoff-figure",
        audience="student",
        language="en",
        output_format="pdf",
        root=REPO_ROOT,
    )

    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))

    assert build_manifest["figure_uses"][0]["figure_id"] == "bias-variance-tradeoff-figure"
    assert build_manifest["figure_uses"][0]["interactive_included"] is False
    assert build_manifest["figure_uses"][0]["d3_included"] is False


def copy_repo_subset(target_root: Path) -> None:
    for relative_path in ("content", "collections", "courses"):
        shutil.copytree(REPO_ROOT / relative_path, target_root / relative_path)
