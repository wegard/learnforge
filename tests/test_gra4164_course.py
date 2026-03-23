from __future__ import annotations

import json

from app.assembly import assemble_target
from app.build import build_target
from app.config import REPO_ROOT
from app.indexer import load_repository


def test_gra4164_course_is_indexed_with_current_canonical_slices() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)

    course = index.courses["gra4164"]

    assert course.model.id == "gra4164"
    assert course.model.languages == ["en"]
    assert course.plan.lectures == [
        "gra4164-lecture-01",
        "gra4164-lecture-02",
        "gra4164-lecture-03",
        "gra4164-lecture-04",
        "gra4164-lecture-05",
        "gra4164-lecture-06",
        "gra4164-lecture-07",
        "gra4164-lecture-08",
        "gra4164-lecture-09",
        "gra4164-lecture-10",
        "gra4164-lecture-11",
    ]
    assert course.plan.assignments == [
        "gra4164-assignment-01",
        "gra4164-assignment-02",
        "gra4164-assignment-03",
        "gra4164-assignment-04",
    ]


def test_gra4164_assignment_collections_are_indexed_with_current_packaging() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)

    assignment_01 = index.objects["gra4164-assignment-01"].model
    assignment_02 = index.objects["gra4164-assignment-02"].model
    assignment_03 = index.objects["gra4164-assignment-03"].model
    assignment_04 = index.objects["gra4164-assignment-04"].model

    assert assignment_01.items == ["sotu-boolean-search-topic-modeling"]
    assert assignment_02.items == ["word-embeddings-sotu-analysis"]
    assert assignment_03.items == ["bert-finetuning-text-classification"]
    assert assignment_04.items == ["prompt-engineering-reflection"]


def test_gra4164_course_assembles_with_current_practical_day_slice() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "gra4164",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    listing_ids = [entry.identifier for entry in assembly.listing_entries]

    assert assembly.target.kind == "course"
    assert assembly.target.identifier == "gra4164"
    assert listing_ids[:11] == [
        "gra4164-lecture-01",
        "gra4164-lecture-02",
        "gra4164-lecture-03",
        "gra4164-lecture-04",
        "gra4164-lecture-05",
        "gra4164-lecture-06",
        "gra4164-lecture-07",
        "gra4164-lecture-08",
        "gra4164-lecture-09",
        "gra4164-lecture-10",
        "gra4164-lecture-11",
    ]
    assert "sotu-boolean-search-topic-modeling" in listing_ids
    assert "bow-tfidf-shakespeare-lab" in listing_ids
    assert "bigram-language-model-lab" in listing_ids
    assert "word-embeddings-sotu-analysis" in listing_ids
    assert "prompt-engineering-reflection" in listing_ids
    assert "gra4164-assignment-01" in listing_ids
    assert "gra4164-assignment-02" in listing_ids
    assert "gra4164-assignment-03" in listing_ids
    assert "gra4164-assignment-04" in listing_ids
    assert "topic-language-models" in listing_ids
    assert "GRA 4164 - Text as Data" in assembly.markdown
    assert "Lecture 4 - N-gram language models" in assembly.markdown
    assert "Lecture 5 - Practical day 1" in assembly.markdown
    assert "Lecture 6 - Word embeddings" in assembly.markdown
    assert "Lecture 7 - LLMs and tokenization" in assembly.markdown
    assert "Lecture 8 - Attention and transformers" in assembly.markdown
    assert "Lecture 9 - LLM architecture and training" in assembly.markdown
    assert "Lecture 10 - Practical day 2" in assembly.markdown
    assert "Lecture 11 - Prompt engineering" in assembly.markdown
    assert "State of the Union - Boolean search and topic modelling" in assembly.markdown
    assert "State of the Union - word embeddings and semantic change" in assembly.markdown
    assert "Assignment 1 - Boolean search and topic modelling" in assembly.markdown
    assert "Assignment 2 - Word embeddings and semantic change" in assembly.markdown
    assert "Assignment 3 - BERT fine-tuning for text classification" in assembly.markdown
    assert "Assignment 4 - Prompt engineering and reflection" in assembly.markdown
    assert "Bag-of-words, TF-IDF, and Shakespeare similarity lab" in assembly.markdown
    assert "Bigram language model lab" in assembly.markdown
    assert "Prompt engineering and marketing reflection" in assembly.markdown
    assert "Word embeddings and Word2Vec" in assembly.markdown


def test_ngram_language_models_concept_links_gra4164_sequence() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "ngram-language-models",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## Why sequence matters" in assembly.markdown
    assert "## An n-gram is a short-memory model" in assembly.markdown
    assert "## Bigram probabilities come from counts" in assembly.markdown
    assert "## Smoothing prevents zero-probability dead ends" in assembly.markdown
    assert "## Log likelihood measures model fit" in assembly.markdown
    assert "text-as-data-introduction" in related_ids
    assert "bag-of-words-tfidf-cosine" in related_ids
    assert "boolean-dictionary-methods-nlp" in related_ids
    assert "gra4164-lecture-04" in related_ids
    assert "gra4164" in related_ids


def test_topic_modeling_lsa_lda_concept_links_gra4164_sequence() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "topic-modeling-lsa-lda",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## Discovering latent themes without labels" in assembly.markdown
    assert "## LSA: dimension reduction via SVD" in assembly.markdown
    assert "## LDA: a probabilistic alternative" in assembly.markdown
    assert "## When to use which" in assembly.markdown
    assert "bag-of-words-tfidf-cosine" in related_ids
    assert "boolean-dictionary-methods-nlp" in related_ids
    assert "text-regression-classification" in related_ids
    assert "gra4164-lecture-03" in related_ids
    assert "gra4164" in related_ids


def test_gra4164_lecture_03_assembly_expands_bow_based_methods_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "gra4164-lecture-03",
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
        "boolean-dictionary-methods-nlp",
        "text-regression-classification",
        "topic-modeling-lsa-lda",
    ]
    assert "## The simplest supervised text methods" in assembly.markdown
    assert "## Why standard regression fails with text" in assembly.markdown
    assert "## Discovering latent themes without labels" in assembly.markdown
    assert "## An n-gram is a short-memory model" not in assembly.markdown


def test_gra4164_lecture_04_assembly_expands_ngram_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "gra4164-lecture-04",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == ["ngram-language-models"]
    assert "## An n-gram is a short-memory model" in assembly.markdown
    assert "## Log likelihood measures model fit" in assembly.markdown
    assert "## Topic modelling with LSA and LDA" not in assembly.markdown


def test_bow_tfidf_shakespeare_lab_links_foundations_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "bow-tfidf-shakespeare-lab",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "exercise"
    assert "## Lab brief" in assembly.markdown
    assert "shakespeare.txt" in assembly.markdown
    assert "## Tasks" in assembly.markdown
    assert "## Starter outline" in assembly.markdown
    assert "text-preprocessing-nlp" in related_ids
    assert "bag-of-words-tfidf-cosine" in related_ids
    assert "gra4164-lecture-05" in related_ids
    assert "gra4164" in related_ids


def test_bigram_language_model_lab_links_foundations_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "bigram-language-model-lab",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "exercise"
    assert "## Lab brief" in assembly.markdown
    assert "names.txt" in assembly.markdown
    assert "## Tasks" in assembly.markdown
    assert "## Starter outline" in assembly.markdown
    assert "ngram-language-models" in related_ids
    assert "gra4164-lecture-05" in related_ids
    assert "gra4164" in related_ids


def test_gra4164_lecture_05_assembly_expands_practical_day_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "gra4164-lecture-05",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == ["bow-tfidf-shakespeare-lab", "bigram-language-model-lab"]
    assert "## Lab brief" in assembly.markdown
    assert "## Suggested approach" not in assembly.markdown
    assert "shakespeare.txt" in assembly.markdown
    assert "names.txt" in assembly.markdown


def test_word_embeddings_word2vec_concept_links_gra4164_sequence() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "word-embeddings-word2vec",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## From sparse counts to dense meaning" in assembly.markdown
    assert "## Co-occurrence and PMI give one route to embeddings" in assembly.markdown
    assert "## PPMI and SVD turn co-occurrence into dense vectors" in assembly.markdown
    assert "## Word2Vec uses prediction instead of matrix factorization" in assembly.markdown
    assert "## Negative sampling makes training practical" in assembly.markdown
    assert "text-as-data-introduction" in related_ids
    assert "bag-of-words-tfidf-cosine" in related_ids
    assert "ngram-language-models" in related_ids
    assert "gra4164-lecture-06" in related_ids
    assert "gra4164" in related_ids


def test_gra4164_lecture_06_assembly_expands_word_embeddings_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "gra4164-lecture-06",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == ["word-embeddings-word2vec"]
    assert "## Co-occurrence and PMI give one route to embeddings" in assembly.markdown
    assert "## Negative sampling makes training practical" in assembly.markdown
    assert "## Lab brief" not in assembly.markdown


def test_llm_introduction_tokenization_concept_links_gra4164_sequence() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "llm-introduction-tokenization",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## What a large language model is" in assembly.markdown
    assert "## LLMs still learn through self-supervision" in assembly.markdown
    assert "## Tokens are not the same as words" in assembly.markdown
    assert "## Byte-pair encoding explains modern subword tokenizers" in assembly.markdown
    assert "## Why tokenization affects model behaviour" in assembly.markdown
    assert "text-preprocessing-nlp" in related_ids
    assert "ngram-language-models" in related_ids
    assert "word-embeddings-word2vec" in related_ids
    assert "gra4164-lecture-07" in related_ids
    assert "gra4164" in related_ids


def test_gra4164_lecture_07_assembly_expands_llm_tokenization_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "gra4164-lecture-07",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == ["llm-introduction-tokenization"]
    assert "## Tokens are not the same as words" in assembly.markdown
    assert "## Byte-pair encoding explains modern subword tokenizers" in assembly.markdown
    assert "## Lab brief" not in assembly.markdown


def test_attention_and_transformers_concept_links_gra4164_sequence() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "attention-and-transformers",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## Why transformers changed NLP" in assembly.markdown
    assert "## Self-attention is the core mechanism" in assembly.markdown
    assert "## Query, key, and value" in assembly.markdown
    assert "## Causal and bidirectional attention are different choices" in assembly.markdown
    assert "## Multi-head attention learns several relevance patterns at once" in assembly.markdown
    assert "ngram-language-models" in related_ids
    assert "word-embeddings-word2vec" in related_ids
    assert "llm-introduction-tokenization" in related_ids
    assert "gra4164-lecture-08" in related_ids
    assert "gra4164" in related_ids


def test_gra4164_lecture_08_assembly_expands_attention_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "gra4164-lecture-08",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == ["attention-and-transformers"]
    assert "## Query, key, and value" in assembly.markdown
    assert "## A transformer block is more than attention" in assembly.markdown
    assert "## Lab brief" not in assembly.markdown


def test_llm_input_output_architecture_concept_links_gra4164_sequence() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "llm-input-output-architecture",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## From tokens to model input" in assembly.markdown
    assert "## Positional information has to be added explicitly" in assembly.markdown
    assert (
        "## The model head turns hidden states into next-token probabilities" in assembly.markdown
    )
    assert "## Output generation is a sampling problem" in assembly.markdown
    assert "## Encoding and decoding refer to different transformer roles" in assembly.markdown
    assert "word-embeddings-word2vec" in related_ids
    assert "llm-introduction-tokenization" in related_ids
    assert "attention-and-transformers" in related_ids
    assert "gra4164-lecture-09" in related_ids
    assert "gra4164" in related_ids


def test_llm_training_and_finetuning_concept_links_gra4164_sequence() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "llm-training-and-finetuning",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## What training is optimizing" in assembly.markdown
    assert "## Gradient descent and backpropagation do the learning" in assembly.markdown
    assert "## Mini-batches, epochs, and teacher forcing" in assembly.markdown
    assert "## Pretraining is broad; fine-tuning is targeted" in assembly.markdown
    assert "## Fine-tuning changes what the model becomes good at" in assembly.markdown
    assert "llm-introduction-tokenization" in related_ids
    assert "attention-and-transformers" in related_ids
    assert "llm-input-output-architecture" in related_ids
    assert "gra4164-lecture-09" in related_ids
    assert "gra4164" in related_ids


def test_gra4164_lecture_09_assembly_expands_llm_architecture_training_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "gra4164-lecture-09",
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
        "llm-input-output-architecture",
        "llm-training-and-finetuning",
    ]
    assert (
        "## The model head turns hidden states into next-token probabilities" in assembly.markdown
    )
    assert "## Pretraining is broad; fine-tuning is targeted" in assembly.markdown
    assert "## Lab brief" not in assembly.markdown


def test_gra4164_lecture_10_assembly_expands_practical_day_2_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "gra4164-lecture-10",
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
        "word-embeddings-sotu-analysis",
        "bert-finetuning-text-classification",
    ]
    assert "## Lab brief" in assembly.markdown
    assert "semantic change over time" in assembly.markdown
    assert "## Part 1: Benchmark fine-tuning task" in assembly.markdown


def test_prompt_engineering_for_nlp_concept_links_gra4164_sequence() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "prompt-engineering-for-nlp",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## Why prompt engineering matters" in assembly.markdown
    assert "## Better prompts give the model a better problem" in assembly.markdown
    assert "## Zero-shot, one-shot, and few-shot prompting" in assembly.markdown
    assert "## Chain-of-thought style prompting" in assembly.markdown
    assert (
        "## Alignment explains why chatbot behaviour differs from raw prediction"
        in assembly.markdown
    )
    assert "llm-introduction-tokenization" in related_ids
    assert "attention-and-transformers" in related_ids
    assert "llm-training-and-finetuning" in related_ids
    assert "gra4164-lecture-11" in related_ids
    assert "gra4164" in related_ids


def test_gra4164_lecture_11_assembly_expands_prompt_engineering_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "gra4164-lecture-11",
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
        "prompt-engineering-for-nlp",
        "prompt-engineering-reflection",
    ]
    assert "## Zero-shot, one-shot, and few-shot prompting" in assembly.markdown
    assert (
        "## Alignment explains why chatbot behaviour differs from raw prediction"
        in assembly.markdown
    )
    assert "## Exercise brief" in assembly.markdown


def test_prompt_engineering_reflection_links_prompting_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "prompt-engineering-reflection",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "exercise"
    assert "## Exercise brief" in assembly.markdown
    assert "## Part 1: Prompt engineering experiment" in assembly.markdown
    assert "## Part 2: Marketing strategy reflection" in assembly.markdown
    assert "approved classroom LLM interface" in assembly.markdown
    assert "prompt-engineering-for-nlp" in related_ids
    assert "llm-training-and-finetuning" in related_ids
    assert "gra4164-assignment-04" in related_ids
    assert "gra4164-lecture-11" in related_ids
    assert "gra4164" in related_ids


def test_word_embeddings_sotu_analysis_links_embeddings_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "word-embeddings-sotu-analysis",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "exercise"
    assert "## Lab brief" in assembly.markdown
    assert "State of the Union speeches" in assembly.markdown
    assert "## Tasks" in assembly.markdown
    assert "## Starter outline" in assembly.markdown
    assert "semantic change over time" in assembly.markdown
    assert "text-preprocessing-nlp" in related_ids
    assert "word-embeddings-word2vec" in related_ids
    assert "gra4164-assignment-02" in related_ids
    assert "gra4164-lecture-10" in related_ids
    assert "gra4164" in related_ids


def test_bert_finetuning_text_classification_links_llm_pipeline_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "bert-finetuning-text-classification",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "exercise"
    assert "## Lab brief" in assembly.markdown
    assert "## Part 1: Benchmark fine-tuning task" in assembly.markdown
    assert "## Part 2: Course-specific labeled dataset" in assembly.markdown
    assert "yelp_review_full" in assembly.markdown
    assert "google-bert/bert-base-cased" in assembly.markdown
    assert "GPU access is strongly recommended" in assembly.markdown
    assert "text-regression-classification" in related_ids
    assert "llm-introduction-tokenization" in related_ids
    assert "llm-input-output-architecture" in related_ids
    assert "llm-training-and-finetuning" in related_ids
    assert "gra4164-assignment-03" in related_ids
    assert "gra4164-lecture-10" in related_ids
    assert "gra4164" in related_ids


def test_gra4164_assignment_01_html_assembly_links_course_and_concepts() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "gra4164-assignment-01",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "collection"
    assert "## Assignment details" in assembly.markdown
    assert "<h2>Included exercises</h2>" in assembly.markdown
    assert "Course context" in assembly.markdown
    assert "gra4164" in related_ids
    assert "boolean-dictionary-methods-nlp" in related_ids
    assert "text-regression-classification" in related_ids
    assert "topic-modeling-lsa-lda" in related_ids


def test_gra4164_assignment_03_html_assembly_links_course_and_concepts() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "gra4164-assignment-03",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "collection"
    assert "## Assignment details" in assembly.markdown
    assert "<h2>Included exercises</h2>" in assembly.markdown
    assert "Course context" in assembly.markdown
    assert "gra4164" in related_ids
    assert "text-regression-classification" in related_ids
    assert "llm-input-output-architecture" in related_ids
    assert "llm-training-and-finetuning" in related_ids


def test_gra4164_assignment_01_student_sheet_excludes_solution_content() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "gra4164-assignment-01",
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
    assert edge_targets == ["sotu-boolean-search-topic-modeling"]
    assert (
        "## Exercise 1: State of the Union - Boolean search and topic modelling"
        in assembly.markdown
    )
    assert (
        "The safest teacher solution follows the assignment notebook closely"
        not in assembly.markdown
    )
    assert all(not item.included_in_output for item in assembly.solution_observations)


def test_gra4164_assignment_03_student_sheet_excludes_solution_content() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "gra4164-assignment-03",
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
    assert edge_targets == ["bert-finetuning-text-classification"]
    assert "## Exercise 1: BERT fine-tuning for text classification" in assembly.markdown
    assert (
        "A strong teacher solution should frame this as a workflow and evaluation exercise"
        not in assembly.markdown
    )
    assert all(not item.included_in_output for item in assembly.solution_observations)


def test_bow_tfidf_shakespeare_lab_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "bow-tfidf-shakespeare-lab",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Bag-of-words, TF-IDF, and Shakespeare similarity lab" in html
    assert "shakespeare.txt" in html
    assert "The safest teacher solution is a transparent workflow" not in html
    assert build_manifest["target"]["identifier"] == "bow-tfidf-shakespeare-lab"
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 0


def test_bow_tfidf_shakespeare_lab_teacher_page_builds_with_solution() -> None:
    artifact = build_target(
        "bow-tfidf-shakespeare-lab",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Bag-of-words, TF-IDF, and Shakespeare similarity lab" in html
    assert "The safest teacher solution is a transparent workflow" in html
    assert build_manifest["target"]["identifier"] == "bow-tfidf-shakespeare-lab"
    assert leakage_report["status"] == "not_applicable"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 1


def test_bigram_language_model_lab_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "bigram-language-model-lab",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Bigram language model lab" in html
    assert "names.txt" in html
    assert "The teacher solution should keep the count-based model explicit" not in html
    assert build_manifest["target"]["identifier"] == "bigram-language-model-lab"
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 0


def test_bigram_language_model_lab_teacher_page_builds_with_solution() -> None:
    artifact = build_target(
        "bigram-language-model-lab",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Bigram language model lab" in html
    assert "The teacher solution should keep the count-based model explicit" in html
    assert build_manifest["target"]["identifier"] == "bigram-language-model-lab"
    assert leakage_report["status"] == "not_applicable"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 1


def test_prompt_engineering_reflection_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "prompt-engineering-reflection",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Prompt engineering and marketing reflection" in html
    assert "Part 1: Prompt engineering experiment" in html
    assert (
        "A strong teacher solution should compare prompt variations in a disciplined way"
        not in html
    )
    assert build_manifest["target"]["identifier"] == "prompt-engineering-reflection"
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 0


def test_prompt_engineering_reflection_teacher_page_builds_with_solution() -> None:
    artifact = build_target(
        "prompt-engineering-reflection",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Prompt engineering and marketing reflection" in html
    assert "A strong teacher solution should compare prompt variations in a disciplined way" in html
    assert build_manifest["target"]["identifier"] == "prompt-engineering-reflection"
    assert leakage_report["status"] == "not_applicable"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 1


def test_gra4164_assignment_01_student_page_builds_cleanly() -> None:
    build_target(
        "gra4164-assignment-01",
        audience="student",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )
    artifact = build_target(
        "gra4164-assignment-01",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Assignment 1 - Boolean search and topic modelling" in html
    assert "Included exercises" in html
    assert "gra4164-assignment-01-exercise-sheet.pdf" in html
    assert "gra4164-assignment-01-solution-sheet.pdf" not in html
    assert build_manifest["target"]["identifier"] == "gra4164-assignment-01"
    assert build_manifest["assignment"]["included_exercise_ids"] == [
        "sotu-boolean-search-topic-modeling"
    ]
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 0


def test_gra4164_assignment_01_teacher_page_shows_teacher_export_only() -> None:
    build_target(
        "gra4164-assignment-01",
        audience="teacher",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )
    artifact = build_target(
        "gra4164-assignment-01",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))

    assert "gra4164-assignment-01-solution-sheet.pdf" in html
    assert "gra4164-assignment-01-exercise-sheet.pdf" not in html
    assert build_manifest["assignment"]["included_exercise_ids"] == [
        "sotu-boolean-search-topic-modeling"
    ]


def test_word_embeddings_sotu_analysis_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "word-embeddings-sotu-analysis",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "State of the Union - word embeddings and semantic change" in html
    assert "Analyse semantic change over time." in html
    assert "The teacher solution should treat the assignment as a comparison exercise" not in html
    assert build_manifest["target"]["identifier"] == "word-embeddings-sotu-analysis"
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 0


def test_word_embeddings_sotu_analysis_teacher_page_builds_with_solution() -> None:
    artifact = build_target(
        "word-embeddings-sotu-analysis",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "State of the Union - word embeddings and semantic change" in html
    assert "The teacher solution should treat the assignment as a comparison exercise" in html
    assert build_manifest["target"]["identifier"] == "word-embeddings-sotu-analysis"
    assert leakage_report["status"] == "not_applicable"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 1


def test_bert_finetuning_text_classification_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "bert-finetuning-text-classification",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "BERT fine-tuning for text classification" in html
    assert "Part 1: Benchmark fine-tuning task" in html
    assert (
        "A strong teacher solution should frame this as a workflow and evaluation exercise"
        not in html
    )
    assert build_manifest["target"]["identifier"] == "bert-finetuning-text-classification"
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 0


def test_bert_finetuning_text_classification_teacher_page_builds_with_solution() -> None:
    artifact = build_target(
        "bert-finetuning-text-classification",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "BERT fine-tuning for text classification" in html
    assert (
        "A strong teacher solution should frame this as a workflow and evaluation exercise" in html
    )
    assert build_manifest["target"]["identifier"] == "bert-finetuning-text-classification"
    assert leakage_report["status"] == "not_applicable"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 1


def test_gra4164_course_student_page_builds_with_practical_day_lecture() -> None:
    artifact = build_target(
        "gra4164",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Lecture 4 - N-gram language models" in html
    assert "Lecture 5 - Practical day 1" in html
    assert "Lecture 6 - Word embeddings" in html
    assert "Lecture 7 - LLMs and tokenization" in html
    assert "Lecture 8 - Attention and transformers" in html
    assert "Lecture 9 - LLM architecture and training" in html
    assert "Lecture 10 - Practical day 2" in html
    assert "Lecture 11 - Prompt engineering" in html
    assert "State of the Union - Boolean search and topic modelling" in html
    assert "State of the Union - word embeddings and semantic change" in html
    assert "Assignment 1 - Boolean search and topic modelling" in html
    assert "Assignment 2 - Word embeddings and semantic change" in html
    assert "Assignment 3 - BERT fine-tuning for text classification" in html
    assert "Assignment 4 - Prompt engineering and reflection" in html
    assert "Bag-of-words, TF-IDF, and Shakespeare similarity lab" in html
    assert "Bigram language model lab" in html
    assert "N-gram language models" in html
    assert "Word embeddings and Word2Vec" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "gra4164"
    assert leakage_report["status"] == "clean"


def test_gra4164_assignment_03_student_page_builds_cleanly() -> None:
    build_target(
        "gra4164-assignment-03",
        audience="student",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )
    artifact = build_target(
        "gra4164-assignment-03",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Assignment 3 - BERT fine-tuning for text classification" in html
    assert "Included exercises" in html
    assert "gra4164-assignment-03-exercise-sheet.pdf" in html
    assert "gra4164-assignment-03-solution-sheet.pdf" not in html
    assert build_manifest["target"]["identifier"] == "gra4164-assignment-03"
    assert build_manifest["assignment"]["included_exercise_ids"] == [
        "bert-finetuning-text-classification"
    ]
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 0


def test_gra4164_assignment_03_teacher_page_shows_teacher_export_only() -> None:
    build_target(
        "gra4164-assignment-03",
        audience="teacher",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )
    artifact = build_target(
        "gra4164-assignment-03",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))

    assert "gra4164-assignment-03-solution-sheet.pdf" in html
    assert "gra4164-assignment-03-exercise-sheet.pdf" not in html
    assert build_manifest["assignment"]["included_exercise_ids"] == [
        "bert-finetuning-text-classification"
    ]


def test_logistic_regression_classification_is_indexed_with_both_courses() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)

    obj = index.objects["logistic-regression-classification"]

    assert "tem0052" in obj.model.courses
    assert "gra4164" in obj.model.courses
    assert "gra4150" in obj.model.courses
    assert len(obj.model.courses) == 3


def test_text_regression_classification_assembly_includes_cross_course_related_links() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "text-regression-classification",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert "logistic-regression-classification" in related_ids
    assert "linear-regression-prediction" in related_ids
