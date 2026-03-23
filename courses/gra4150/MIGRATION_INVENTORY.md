# GRA4150 Migration Inventory

This file tracks the migration of legacy material from
`course-inbox/GRA4150_2024/` into LearnForge's canonical course/object structure.

## Locked Decisions

- Canonical course id: `gra4150`
- Course language at migration start: `en` only
- Legacy LaTeX slides and Jupyter notebooks are reference material, not source of truth
- New canonical material should prefer:
  - exposition in `.qmd`
  - exercises as LearnForge `exercise` objects
  - solutions in `solution.en.qmd`
- Lecture numbering preserves the original course numbering (gaps at 6, 9, 10
  reflect sessions without structured source material)
- No bulk import of legacy datasets (Ames, Iris, MNIST stay external)
- No promotion of LaTeX build artifacts, beamer themes, compiled PDFs, exam
  student submissions, or the `preamble.tex` files
- Owners: vegard
- Instructor of record: Silvia Lavagnini
- Textbook: Machine Learning with PyTorch and Scikit-Learn (Raschka, Liu, Mirjalili)

## Cross-Link Existing Objects

These approved English objects already exist in LearnForge and should be
wired into `gra4150` by adding the course to their `courses:` list.

### Concepts (from tem0052)

| Existing object id | Lecture mapping | Current courses |
| --- | --- | --- |
| `linear-regression-prediction` | L3 | tem0052, gra4164, gra4150 | **cross-linked** |
| `penalized-linear-models` | L3–4 | tem0052, gra4150 | **cross-linked** |
| `logistic-regression-classification` | L5 | tem0052, gra4164, gra4150 | **cross-linked** |
| `bias-variance-tradeoff` | L4 | tem0052, gra4150 | **cross-linked** |
| `model-selection-cross-validation` | L4 | tem0052, gra4150 | **cross-linked** |
| `ml-preprocessing-pipelines` | L2 | tem0052, gra4150 | **cross-linked** |
| `principal-component-analysis` | L8 (unsupervised context) | tem0052, gra4164, gra4150 | **cross-linked** |
| `k-means-clustering` | L8 (unsupervised context) | tem0052, gra4150 | **cross-linked** |

### Exercises (from tem0052)

| Existing object id | Lecture mapping | Current courses |
| --- | --- | --- |
| `house-prices-regression` | L3 | tem0052, gra4150 | **cross-linked** |
| `titanic-data-preprocessing` | L2 | tem0052, gra4150 | **cross-linked** |

## Migration Buckets

### Promote First — New Concepts

| Legacy source | Target kind | Proposed target id | Lecture | Status |
| --- | --- | --- | --- | --- |
| `GRA4150_Lecture1/GRA4150_Lecture1.tex` | concept | `ai-and-ml-introduction` | L1 | **promoted** |
| `GRA4150_Lecture3/GRA4150_Lecture3.tex` (gradient descent section) | concept | `gradient-descent-optimization` | L3 | **promoted** |
| `GRA4150_Lecture4/GRA4150_Lecture4.tex` + `Adaline.ipynb` | concept | `adaline-and-perceptron` | L4 | **promoted** |
| `GRA4150_Lecture7/GRA4150_Lecture7.tex` | concept | `multi-layer-perceptron` | L7 | **promoted** |
| `GRA4150_Lecture8/GRA4150_Lecture8.tex` | concept | `ai-ethics-bias-explainability` | L8 | **promoted** |
| `GRA4150_Lecture11/GRA4150_Lecture11.tex` | concept | `convolutional-neural-networks` | L11 | **promoted** |

### Promote First — New Exercises

| Legacy source | Target kind | Proposed target id | Lecture | Status |
| --- | --- | --- | --- | --- |
| `GRA4150_Lecture4/GRA4150_Adaline.ipynb` | exercise | `adaline-iris-classification` | L4 | **promoted** |
| `GRA4150_Lecture7/GRA4150_MultiLayerPerceptron.ipynb` | exercise | `mlp-classification-lab` | L7 | **promoted** |
| `Exercises/GRA4150_Exercise2/` | exercise | `ai-fairness-face-recognition` | L8 | **promoted** |
| `GRA4150_Lecture11/GRA4150_CNN.ipynb` | exercise | `cnn-image-classification` | L11 | **promoted** |
| `Exercises/GRA4150_Exercise1/` Section 7 | exercise | `sklearn-logistic-regression-lab` | L5 | **promoted** |
| `Exercises/GRA4150_Exercise1/` Section 8 | exercise | `wine-regularization-tuning` | L5 | **promoted** |

### Lecture Collection Assembly

| Collection id | Title | Items (concepts + exercises) |
| --- | --- | --- |
| `gra4150-lecture-01` | Introduction to AI and Machine Learning | `ai-and-ml-introduction` |
| `gra4150-lecture-02` | ML Fundamentals and Data Preprocessing | `ml-preprocessing-pipelines`, `titanic-data-preprocessing` |
| `gra4150-lecture-03` | Regression and Gradient Descent | `linear-regression-prediction`, `gradient-descent-optimization`, `penalized-linear-models`, `house-prices-regression` |
| `gra4150-lecture-04` | Bias-Variance Tradeoff and Adaline | `bias-variance-tradeoff`, `model-selection-cross-validation`, `adaline-and-perceptron`, `adaline-iris-classification` |
| `gra4150-lecture-05` | Logistic Regression and Multi-class Classification | `logistic-regression-classification` |
| `gra4150-lecture-07` | Multi-Layer Perceptrons | `multi-layer-perceptron`, `mlp-classification-lab` |
| `gra4150-lecture-08` | AI Ethics, Bias and Explainability | `ai-ethics-bias-explainability`, `ai-fairness-face-recognition` |
| `gra4150-lecture-11` | Convolutional Neural Networks | `convolutional-neural-networks`, `cnn-image-classification` |

### Defer

| Legacy source | Reason for deferral |
| --- | --- |
| `GRA4150_Lecture9_SamsonEsayas.pdf` | Guest lecture — not owned by course maintainer |
| Lectures 6, 10 | No structured source material in inbox |
| `Exercises/GRA4150_Exercise1/` Sections 1–6 | Overlap with existing exercises or theory-only (no solution notebooks); Sections 5/6 covered by `house-prices-regression` and `adaline-iris-classification` |
| `Mock_exam/` | Exam material, defer until assessment workflow is designed |
| `Exam_spring2024/`, `Exam_spring2025/` | Exam papers and student submissions, not teaching content |
| `GRA4150_Lecture3/GRA4150_RegressionAnalysis_wRegularization.ipynb` | Supplementary regularization notebook, covered by `penalized-linear-models` concept |
| `GRA4150_Lecture7/GRA4150_MLPcode.ipynb` | Supplementary code notebook, content folded into `mlp-classification-lab` |
| `GRA4150_Lecture11/MNIST/` | Raw dataset files, not teaching content |
| `Results_2024.xlsx` | Administrative grading data |

### Drop or Archive

| Legacy source | Reason |
| --- | --- |
| `*.aux`, `*.log`, `*.nav`, `*.snm`, `*.synctex.gz`, `*.toc` | LaTeX build artifacts |
| `*.pdf` (compiled lecture slides) | Compiled output, not source |
| `preamble.tex` (in Lecture11) | LaTeX formatting, not content |
| `GRA4150_Lecture11/Figures/conv/` (50+ PDF figures) | Convolution step-by-step visualizations — recreate as SVG figures if needed |
| Student exam PDFs in `Exam_spring2024/`, `Exam_spring2025/` | Student work, not course content |

## Instructor Review Checklist

Tasks that require instructor judgement and cannot be automated.

- [ ] Review cross-linked concept scope — confirm that the tem0052 versions of
      linear regression, logistic regression, etc. match GRA4150's depth and focus
- [ ] Review new concept `.qmd` files for accuracy and tone (6 new concepts)
- [ ] Review exercise briefs and solutions (4 new exercises)
- [ ] Decide lecture item ordering within each lecture collection
- [ ] Decide whether unsupervised learning topics (PCA, k-means) warrant their
      own lecture or fold into existing lectures
- [ ] Promote reviewed content from `status: draft` to `status: approved`
