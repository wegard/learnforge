# BIK2550 Migration Inventory

This file tracks the migration of legacy material from
`course-inbox/BIK2550/` into LearnForge's canonical course/object structure.

## Locked Decisions

- Canonical course id: `bik2550`
- Course language at migration start: `nb` only
- Content creates **separate introductory-level concepts** rather than reusing
  tem0052 concepts (different audience, depth, and language)
- Lecture naming convention: `bik2550-m1d1` (module/day structure)
- Legacy notebooks are instructor demonstrations → convert to concept objects
  with exposition in `.qmd`; only graded student output notebooks become exercises
- Module 2 is deferred entirely — no structured source material exists
- The project brief is modeled canonically as an assignment collection with
  conceptual exercises; grading guidance can remain deferred
- No promotion of editor files, checkpoint folders, compiled LaTeX artifacts,
  branding assets, or the nested legacy git repository

## Migration Buckets

### Promote First (Module 1 — all 3 days)

| Legacy source | Target kind | Proposed target id | Status |
| --- | --- | --- | --- |
| `modul_1/dag1/Hva_er_AI.tex` (AI section) | concept | `what-is-ai-overview` | **promoted** |
| `modul_1/dag1/AI_utvikling.tex` | concept | `ai-history-timeline` | **promoted** |
| `modul_1/dag1/Hva_er_AI.tex` (finance frames) | concept | `ai-in-finance-landscape` | **promoted** |
| `modul_1/dag1/Hva_er_AI.tex` (GenAI section) | concept | `generative-ai-introduction` | **promoted** |
| `modul_1/ressurser/Introduksjon_til_Python_og_Jupyter_notebooks.ipynb` | concept | `python-jupyter-introduction` | **promoted** |
| `modul_1/ressurser/Dataanalyse_med_jupyter_notebooks.ipynb` | concept | `data-analysis-with-jupyter` | **promoted** |
| `modul_1/dag2/Hva_er_maskinlæring.tex` (supervised) | concept | `ml-supervised-learning-overview` | **promoted** |
| `modul_1/dag2/Hva_er_maskinlæring.tex` (unsupervised) | concept | `ml-unsupervised-learning-overview` | **promoted** |
| `modul_1/dag2/Hva_er_maskinlæring.tex` (evaluation) | concept | `ml-model-evaluation-overview` | **promoted** |
| `modul_1/ressurser/Maskinlæring_for_finans.ipynb` | concept | `ml-finance-demo` | **promoted** |
| `modul_1/dag3/Nevrale_nettverk_og_dyp_læring.tex` (NN basics) | concept | `neural-networks-introduction` | **promoted** |
| `modul_1/dag3/Nevrale_nettverk_og_dyp_læring.tex` (architectures) | concept | `deep-learning-architectures-overview` | **promoted** |
| `modul_1/dag3/Nevrale_nettverk_og_dyp_læring.tex` (LLM section) | concept | `llms-and-next-token-prediction` | **promoted** |
| `modul_1/ressurser/Predikere_mislighold_kredittkort_NN.ipynb` | exercise | `credit-default-prediction-nn` | **promoted** |
| `modul_1/ressurser/svindeloppdagelse.ipynb` | exercise | `fraud-detection-exercise` | **promoted** |

### Promote Second (Module 3)

| Legacy source | Target kind | Proposed target id | Status |
| --- | --- | --- | --- |
| `modul_3/dag1/Store_språkmodeller_og_NLP.tex` | concept | `nlp-text-data-finance` | **promoted** |
| `modul_3/dag1/llms.tex` | concept | `llms-deep-dive` | **promoted** |
| `modul_3/dag2/Multimodalitet_i_Finans.tex` | concept | `multimodality-in-finance` | **promoted** |
| `modul_3/dag3/Oppsumering_AI_finans.tex` + `Anvendelser.tex` | concept | `ai-applications-finance-summary` | **promoted** |
| `modul_3/ressurser/Predict_the_next_token_part1.ipynb` | exercise | `next-token-prediction-exercise` | **promoted** |

### Rewrite Fresh

| Topic | Canonical coverage | Status |
| --- | --- | --- |
| Exam project brief + case studies | `bik2550-project-brief` + project exercises | draft |

### Out of Scope

| Topic | Reason |
| --- | --- |
| Module 2 ethics concepts | Delivered by guest lecturers; not owned by this course maintainer |
| Module 2 regulation concepts (EU AI Act, GDPR) | Delivered by guest lecturers; not owned by this course maintainer |

### Defer

| Legacy source | Reason for deferral |
| --- | --- |
| `modul_1/ressurser/gjenkjenning_av_siffer.ipynb` | Digit recognition demo, not core content |
| `modul_1/ressurser/create_figures.ipynb` | Figure generation utility, not teaching content |
| `modul_3/ressurser/Predict_the_next_token_part2_nn.ipynb` | Advanced next-token part, defer to later wave |
| `modul_3/ressurser/Predict_the_next_token_part3_mpl.ipynb` | Advanced next-token part, defer to later wave |
| `modul_3/ressurser/Predikere_neste_bokstav.ipynb` | Older version of next-token notebook |
| `modul_3/ressurser/Predikere_neste_bokstav_ver2.ipynb` | Older version of next-token notebook |
| `modul_3/ressurser/bigram_nb_no.ipynb` | Bigram notebook, superseded by Predict_the_next_token |
| `modul_1/ressurser/micrograd/` | Micrograd module, not core content |
| `Course_plan/` older versions | Historical reference only |
| `Vurderingsveiledning BIK2550.docx` | Keep grading rubric in the inbox until the assessment language is stabilized |

### Drop or Archive

| Legacy source | Reason |
| --- | --- |
| `*.nav`, `*.snm`, `*.log`, `*.synctex.gz`, compiled PDFs | Build artifacts |
| `beamerthemebi/`, `beamerthemebi.sty`, `beamerthemeexample.sty` | BI Beamer theme files |
| `logo.png`, `title_page_background.jpg` (in theme dirs) | Branding assets |
| `modul_1/dag1/archive/` | Archived older slide versions |
| `modul_1/ressurser/archive/` | Archived older notebooks |
| `.virtual_documents/` | Editor artifacts |
| `.docx` files | Word documents (guest lecture materials) |
| `.git/` (if nested) | Tooling noise |

## Instructor Review Checklist

Tasks that require instructor judgement and cannot be automated.

- [ ] Review all `.qmd` concept notes for accuracy and tone (17 concepts)
      — content was rewritten from LaTeX slides, check that finance examples
      and level match what you actually teach
- [ ] Review exercise briefs and solutions (6 exercises)
      — verify datasets, expected outputs, and time estimates are realistic
- [ ] Decide lecture item ordering within each lecture collection
      — current order follows the original slide deck sequence
- [ ] Recreate key figures as SVG for promotion to figure objects
      — the raster images in `course-inbox/BIK2550/images/` cannot be imported
      directly (figure objects require SVG + PDF). Candidates worth recreating:

      | Image | Concept it supports | Status |
      |---|---|---|
      | `bias_variance_tradeoff_4.png` | `ml-model-evaluation-overview` | candidate |
      | `confusion_matrix.png` | `ml-model-evaluation-overview` | **promoted** |
      | `training_and_test_error.png` | `ml-model-evaluation-overview` | **promoted** |
      | `my_activation_functions.png` | `neural-networks-introduction` | **promoted** |
      | `gradient_descent.png` | `ml-model-evaluation-overview` | **promoted** |
      | `regression_example.png` | `ml-supervised-learning-overview` | candidate |
      | `sigmoid.png` | `ml-supervised-learning-overview` | candidate |
      | `dt_kreditt.png` | `ml-supervised-learning-overview` | candidate |

      Most other images are external diagrams with attribution, screenshots,
      or decorative stock images — not suitable for figure objects.
- [x] Design the exam/assignment object from `exam/` folder
      — first canonical project brief now lives in `bik2550-project-brief`
- [ ] Promote reviewed content from `status: draft` to `status: review`
      then `status: approved` (Claude can apply the YAML changes)

## Promoted in the Current Checkpoint

- Concept: `what-is-ai-overview`
- Concept: `ai-history-timeline`
- Concept: `ai-in-finance-landscape`
- Concept: `generative-ai-introduction`
- Concept: `python-jupyter-introduction`
- Concept: `data-analysis-with-jupyter`
- Concept: `ml-supervised-learning-overview`
- Concept: `ml-unsupervised-learning-overview`
- Concept: `ml-model-evaluation-overview`
- Concept: `ml-finance-demo`
- Concept: `neural-networks-introduction`
- Concept: `deep-learning-architectures-overview`
- Concept: `llms-and-next-token-prediction`
- Exercise: `credit-default-prediction-nn`
- Exercise: `fraud-detection-exercise`
- Lecture collection: `bik2550-m1d1`
- Lecture collection: `bik2550-m1d2`
- Lecture collection: `bik2550-m1d3`
- Concept: `nlp-text-data-finance`
- Concept: `llms-deep-dive`
- Concept: `multimodality-in-finance`
- Concept: `ai-applications-finance-summary`
- Exercise: `next-token-prediction-exercise`
- Lecture collection: `bik2550-m3d1`
- Lecture collection: `bik2550-m3d2`
- Lecture collection: `bik2550-m3d3`
- Exercise: `ai-finance-project-scope`
- Exercise: `ai-finance-solution-blueprint`
- Exercise: `ai-finance-individual-reflection`
- Assignment collection: `bik2550-project-brief`
- Figure: `confusion-matrix-figure`
- Figure: `training-test-error-figure`
- Figure: `gradient-descent-figure`
- Figure: `activation-functions-figure`
