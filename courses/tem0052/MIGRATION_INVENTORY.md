# TEM0052 Migration Inventory

This file tracks the migration of legacy material from
`course-inbox/predictive-modelling-with-machine-learning/` into LearnForge's canonical
course/object structure.

## Locked Decisions

- Canonical course id: `tem0052`
- Course language at migration start: `en` only
- Legacy notebooks are reference material, not source of truth
- New teaching material should prefer:
  - exposition in `.qmd`
  - reusable code in plain `.py`
  - exercises in LearnForge `exercise` objects
  - solutions in `solution.en.qmd`
- No bulk import of the legacy `data/` folder
- No promotion of editor files, checkpoint folders, compiled LaTeX artifacts, or the
  nested legacy git repository

## Migration Buckets

### Promote First

These items line up well with the new course description and can be turned into
reusable concepts, figures, and exercises with moderate rewriting.

| Legacy source | Action | Target kind | Proposed target id |
| --- | --- | --- | --- |
| `notebooks/01_Working_with_data_in_jupyter_notebooks.ipynb` | Rewrite around leakage-safe preprocessing, scaling, and reusable pipelines | concept | `ml-preprocessing-pipelines` |
| `notebooks/02_OLS.ipynb` | Rewrite into reusable exposition | concept | `linear-regression-prediction` |
| `notebooks/03_Supervised_learning_with_kNN.ipynb` | Rewrite and trim notebook-specific workflow | concept | `knn-supervised-learning` |
| `notebooks/05_Regularised_regressions.ipynb` | Rewrite around ridge/lasso/elastic-net | concept | `penalized-linear-models` |
| `notebooks/06_Logistic_regression.ipynb` | Rewrite with cleaner classification framing | concept | `logistic-regression-classification` |
| `notebooks/07_Decision_trees.ipynb` | Rewrite and extract reusable visuals | concept + figure | `decision-tree-learning` |
| `notebooks/08_Information_criteria_and_cross_validation.ipynb` | Split into assessment concepts | concept | `model-selection-cross-validation` |
| `notebooks/09_Bias_variance_tradeoff.ipynb` | Rewrite and extract figure(s) | concept + figure | `bias-variance-tradeoff` |
| `notebooks/10_PCA.ipynb` | Rewrite | concept | `principal-component-analysis` |
| `notebooks/11_K_means.ipynb` | Rewrite | concept | `k-means-clustering` |
| `notebooks/12_Introducing_ensemble_methods.ipynb` | Rewrite | concept | `ensemble-methods-introduction` |
| `notebooks/13_Random_forests.ipynb` | Rewrite | concept | `random-forests` |
| `tex2026/figures/kFold_validation.png` | Promote as a reusable resampling figure | figure | `k-fold-cross-validation-figure` |
| `exercises/to_students/01_Data_preprocessing_titanic.ipynb` | Convert into a reproducible preprocessing and baseline-model lab | exercise | `titanic-data-preprocessing` |
| `exercises/to_students/02_Spam_filtering_with_naive_bayes.ipynb` | Convert to student exercise + teacher solution | exercise | `spam-filtering-naive-bayes` |
| `exercises/to_students/03_Predicting_house_prices.ipynb` | Convert to student exercise + teacher solution | exercise | `house-prices-regression` |
| `exercises/to_students/05_Model_selection_evaluation_and_assessment.ipynb` | Convert and simplify | exercise | `model-assessment-lab` |
| `exercises/to_students/07_Predicting_income.ipynb` | Convert after ensemble-method cleanup | exercise | `income-classification-ensemble` |

### Rewrite Fresh

These topics are in the new course description but need fresh authoring or major
restructuring rather than direct migration.

| Topic | Reason | Planned target kind |
| --- | --- | --- |
| ~~Support Vector Machines~~ | ~~Promoted as `support-vector-machines` concept + `svm-classification-lab` exercise + `tem0052-lecture-08` collection (draft)~~ | ~~done~~ |
| Gradient Boosting / XGBoost framing | Legacy material hints at boosting but the new course needs a cleaner dedicated treatment | concept + exercise later |
| Hierarchical clustering | New description calls for stronger unsupervised coverage than the legacy course appears to provide | concept |
| Responsible ML | Fairness, privacy, transparency, and reproducibility should be new canonical content | concept + curated resources |
| Semester project brief | New course uses an individual semester project, unlike the older group mini-project setup | assignment / course material |
| AI workflow guidance | New course description explicitly encourages AI tools and needs fresh policy text and curated resources | syllabus + resources |

### Defer

These can stay in the inbox until the classical-ML core is migrated.

| Legacy source | Reason for deferral |
| --- | --- |
| `notebooks/17_Neural_nets_basics.ipynb` | Neural-network bridge is only a late, light course component |
| `notebooks/18_NN_with_PyTorch.ipynb` | Useful later, but not part of the first migration wave |
| `notebooks/19_Build_a_NN.ipynb` | More implementation-heavy than the new bridge likely needs |
| `notebooks/19_Multilayer_neural_networks.ipynb` | Likely too detailed for the new scope |
| `notebooks/20_Convolutional_neural_networks.ipynb` | Outside the stated “brief bridge” emphasis |
| `exercises/to_students/09_Neural_networks_with_Keras_I.ipynb` | Tied to a workflow you plan to move away from |
| `exercises/to_students/10_Neural_networks_with_Keras_II.ipynb` | Tied to a workflow you plan to move away from |
| `tex2025/` and `tex2026/` full slide decks | Valuable as reference, but not canonical source material |

### Drop Or Archive

| Legacy source | Reason |
| --- | --- |
| `.git/` and `.idea/` | Tooling noise |
| `.ipynb_checkpoints/` | Generated notebook artifacts |
| `*.log`, `*.nav`, `*.snm`, `*.synctex.gz`, generated PDFs | Build artifacts, not source |
| `exercises/to_students/Untitled.ipynb` | Unnamed scratch material |
| `data/tmp/` | Temporary processed output |
| `notebooks/archive/` and `exercises/archive/` | Keep only as fallback reference in the inbox |

## Proposed First Canonical Slice

Build the first LearnForge checkpoint for `tem0052` around the classical-ML core.

### Promoted in the current checkpoint

- Concept: `bias-variance-tradeoff`
- Concept: `model-selection-cross-validation`
- Concept: `ml-preprocessing-pipelines`
- Concept: `knn-supervised-learning`
- Concept: `naive-bayes-classification`
- Concept: `decision-tree-learning`
- Concept: `ensemble-methods-introduction`
- Concept: `random-forests`
- Concept: `linear-regression-prediction`
- Concept: `penalized-linear-models`
- Concept: `logistic-regression-classification`
- Concept: `principal-component-analysis`
- Concept: `k-means-clustering`
- Figure: `k-fold-cross-validation-figure`
- Exercise: `model-assessment-lab`
- Exercise: `titanic-data-preprocessing`
- Exercise: `house-prices-regression`
- Exercise: `spam-filtering-naive-bayes`
- Exercise: `income-classification-ensemble`
- Lecture collection: `tem0052-lecture-01`
- Lecture collection: `tem0052-lecture-02`
- Lecture collection: `tem0052-lecture-03`
- Lecture collection: `tem0052-lecture-04`
- Lecture collection: `tem0052-lecture-05`
- Lecture collection: `tem0052-lecture-06`
- Lecture collection: `tem0052-lecture-07`
- Concept: `support-vector-machines`
- Exercise: `svm-classification-lab`
- Lecture collection: `tem0052-lecture-08`

### First concept candidates

- `bias-variance-tradeoff`
- `ml-preprocessing-pipelines`
- `linear-regression-prediction`
- `penalized-linear-models`
- `logistic-regression-classification`
- `naive-bayes-classification`
- `decision-tree-learning`
- `ensemble-methods-introduction`
- `principal-component-analysis`
- `k-means-clustering`
- `model-selection-cross-validation`
- `random-forests`

### First exercise candidates

- `titanic-data-preprocessing`
- `spam-filtering-naive-bayes`
- `model-assessment-lab`

### First lecture candidates

- `tem0052-lecture-01` foundations + preprocessing
- `tem0052-lecture-02` linear prediction + regularisation
- `tem0052-lecture-03` classification methods
- `tem0052-lecture-04` model assessment + bias-variance
- `tem0052-lecture-06` unsupervised learning with PCA + k-means
- `tem0052-lecture-07` ensemble methods + random forests

## Next Migration Actions

1. Extract 1 more reusable figure from the remaining legacy notebooks or slide decks,
   especially if the unsupervised block needs a better visual explanation.
2. Draft the next fresh-authored concept from the redesign-only queue, likely
   gradient boosting or hierarchical clustering.
3. Leave the neural-network bridge material in the inbox until the classical-ML core
   is more complete.
