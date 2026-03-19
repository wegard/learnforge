# Plan: Promote GRA4164 Lecture 3 Slice + First Exercise

## Context

Lectures 1-2 are promoted (3 concepts, 2 lecture collections). The migration inventory's next actions call for the Lecture 3 concepts and the first assignment exercise. Lecture 3 ("Bag-of-words-based methods") is the densest lecture in the classical NLP arc — it covers three distinct method families. Promoting it alongside the first assignment creates a complete teach-and-practice slice.

## Scope

Promote **3 concepts** + **1 exercise** + create **1 lecture collection** + update plan.yml and inventory:

| Object | Kind | Purpose |
|---|---|---|
| `boolean-dictionary-methods-nlp` | concept | Boolean search, sentiment dictionaries |
| `text-regression-classification` | concept | Text regression (OLS/Lasso) + Naive Bayes classification |
| `topic-modeling-lsa-lda` | concept | LSA/PCA and LDA topic models |
| `sotu-boolean-search-topic-modeling` | exercise | Assignment 1: SOTU analysis with boolean search, LDA, sentiment |
| `gra4164-lecture-03` | collection (lecture) | Assembles the 3 concepts above |

## Concept Details

### 1. `boolean-dictionary-methods-nlp`

**Sources:** `nlp_methods_countboolean.tex` + Lecture 3 tex (lines 143-267)

**Content to cover (~350 words):**
- What Boolean/dictionary methods are and when they apply
- Sentiment dictionaries (General Inquirer, Loughran-McDonald for finance)
- Boolean operators: counting terms matching AND/OR/NOT queries
- Real-world examples: Baker et al. policy uncertainty index, Tetlock sentiment-market studies
- Limitations: subjectivity in dictionary construction, polysemy, synonymy
- Teacher-only: ask students how they would design a dictionary for their business domain
- What to report section

**meta.yml:**
- `courses: [gra4164]`
- `topics: [natural-language-processing, text-analysis, text-classification]`
- `tags: [boolean-search, sentiment-dictionary, text-classification]`
- `level: introductory`
- `prerequisites: [bag-of-words-tfidf-cosine]`
- `related: [text-regression-classification, topic-modeling-lsa-lda, text-preprocessing-nlp]`
- `owners: [vegard, leif]`

### 2. `text-regression-classification`

**Sources:** `nlp_methods_olsregularization.tex` + `nlp_methods_naivebayes.tex` + Lecture 3 tex

**Content to cover (~450 words):**
- Why standard OLS fails with text (n << p, high dimensionality)
- Penalised regression (Lasso/Ridge) as natural solution for sparse text features
- Naive Bayes classification: Bayes rule, conditional independence, Laplace smoothing
- The intuition: prior × likelihood → posterior, then pick the most probable class
- Key formula: $P(v_k | d) \propto P(v_k) \prod_j P(c_j | v_k)$
- Practical framing: spam filtering, sentiment classification, document categorisation
- Teacher-only: ask why the "naive" independence assumption works well despite being wrong
- What to report section
- Cross-reference to `logistic-regression-classification` (tem0052) and `linear-regression-prediction` (tem0052) in `related:`

**meta.yml:**
- `topics: [natural-language-processing, text-analysis, classification, regression]`
- `tags: [naive-bayes, text-regression, lasso, penalized-regression, text-classification]`
- `level: intermediate`
- `prerequisites: [bag-of-words-tfidf-cosine]`
- `related: [boolean-dictionary-methods-nlp, topic-modeling-lsa-lda, logistic-regression-classification, linear-regression-prediction]`

### 3. `topic-modeling-lsa-lda`

**Sources:** `nlp_methods_pcalda.tex` (432 lines) + Lecture 3 tex

**Content to cover (~450 words):**
- Motivation: discovering latent themes without labels (unsupervised)
- LSA via truncated SVD: $C \approx U_K S_K V_K'$, factor matrix F = document prevalence, loading matrix L = word importance
- LDA as a probabilistic alternative: documents as mixtures of topics, topics as distributions over words
- Dirichlet priors and sparsity control
- When to use which: LSA is faster and simpler; LDA gives interpretable probability distributions
- Extensions worth knowing: dynamic topic models, correlated topic models
- Teacher-only: show word cloud examples and ask students to label topics before revealing ground truth
- What to report section
- Cross-reference to `principal-component-analysis` (tem0052, planned) in `related:`

**meta.yml:**
- `topics: [natural-language-processing, text-analysis, topic-modeling, unsupervised-learning]`
- `tags: [lsa, lda, topic-modeling, svd, dimensionality-reduction]`
- `level: intermediate`
- `prerequisites: [bag-of-words-tfidf-cosine]`
- `related: [boolean-dictionary-methods-nlp, text-regression-classification]`

## Exercise Details

### `sotu-boolean-search-topic-modeling`

**Source:** `assignment1.ipynb` (~1500 lines)

**Exercise type:** coding, difficulty: medium, estimated_time: 120 min

**note.en.qmd (~55 lines):**
- Lab brief: analyse State of the Union speeches (1980-2017) to test whether presidential language predicts economic outcomes
- Background: 39 speeches, matched with annual GDP growth data
- Numbered tasks (8-9 items):
  1. Describe the Boolean search approach and its strengths/weaknesses
  2. Implement at least 5 Boolean search specifications with different term sets
  3. Run text regressions with GDP growth as outcome; interpret coefficients
  4. Assess sensitivity across specifications
  5. Fit an LDA topic model; justify number of topics
  6. Visualise topics with word clouds
  7. Analyse topic prevalence across presidents
  8. Correlate topic weights with GDP growth
  9. Compare Boolean search vs topic model results
- Starter code outline: data loading, CountVectorizer setup, LDA from sklearn
- Note on data: SOTU corpus is publicly available (link/instructions)

**solution.en.qmd (~50 lines):**
- Suggested approach: 7-8 steps covering the full pipeline
- What students should find: Boolean R² ~0.15, topic model R² ~0.47, sensitivity to term choice in Boolean, topic interpretability challenges
- Teaching emphasis: method comparison matters more than exact numbers; sensitivity analysis reveals how arbitrary Boolean search is vs data-driven topic modelling

**meta.yml:**
- `exercise_type: coding`
- `difficulty: medium`
- `estimated_time_minutes: 120`
- `concepts: [boolean-dictionary-methods-nlp, topic-modeling-lsa-lda, text-regression-classification]`
- `courses: [gra4164]`
- `topics: [natural-language-processing, text-analysis, topic-modeling, text-classification]`
- `tags: [exercise, boolean-search, lda, sentiment-analysis, sotu]`
- `outputs: [html, pdf, exercise-sheet]`
- `solution_storage: separate-file`
- `solution_visibility: teacher`

## Lecture Collection

### `gra4164-lecture-03`

```yaml
id: gra4164-lecture-03
kind: collection
collection_kind: lecture
items:
  - boolean-dictionary-methods-nlp
  - text-regression-classification
  - topic-modeling-lsa-lda
```

Note: the exercise is not included in the lecture collection — it will be assembled into an assignment collection later, following the tem0052 pattern.

## Files to Create/Modify

**Create (12 new files):**
- `content/concepts/boolean-dictionary-methods-nlp/meta.yml`
- `content/concepts/boolean-dictionary-methods-nlp/note.en.qmd`
- `content/concepts/text-regression-classification/meta.yml`
- `content/concepts/text-regression-classification/note.en.qmd`
- `content/concepts/topic-modeling-lsa-lda/meta.yml`
- `content/concepts/topic-modeling-lsa-lda/note.en.qmd`
- `content/exercises/sotu-boolean-search-topic-modeling/meta.yml`
- `content/exercises/sotu-boolean-search-topic-modeling/note.en.qmd`
- `content/exercises/sotu-boolean-search-topic-modeling/solution.en.qmd`
- `collections/lectures/gra4164-lecture-03/meta.yml`

**Modify (2 files):**
- `courses/gra4164/plan.yml` — add `gra4164-lecture-03` to lectures list
- `courses/gra4164/MIGRATION_INVENTORY.md` — update promoted checkpoint and next actions

## Source Files to Read During Implementation

- `course-inbox/nlp-for-business/tex/modules/methods/nlp_methods_countboolean.tex`
- `course-inbox/nlp-for-business/tex/modules/methods/nlp_methods_olsregularization.tex`
- `course-inbox/nlp-for-business/tex/modules/methods/nlp_methods_naivebayes.tex`
- `course-inbox/nlp-for-business/tex/modules/methods/nlp_methods_pcalda.tex`
- `course-inbox/nlp-for-business/tex/courses/GRA4164_Text_as_Data/Lecture_3_bow_based_methods/Lecture_bow_based_methods.tex`
- `course-inbox/nlp-for-business/notebooks/GRA4164/assignment1.ipynb`

## Reference Files

- `content/concepts/bag-of-words-tfidf-cosine/note.en.qmd` — gra4164 concept style
- `content/concepts/bag-of-words-tfidf-cosine/meta.yml` — gra4164 concept metadata
- `content/exercises/spam-filtering-naive-bayes/note.en.qmd` — exercise note format
- `content/exercises/spam-filtering-naive-bayes/solution.en.qmd` — solution format
- `collections/lectures/gra4164-lecture-02/meta.yml` — gra4164 lecture collection format

## Commit Strategy

One commit per object (following tem0052 pattern):
1. "Promote gra4164 concept: boolean-dictionary-methods-nlp"
2. "Promote gra4164 concept: text-regression-classification"
3. "Promote gra4164 concept: topic-modeling-lsa-lda"
4. "Promote gra4164 exercise: sotu-boolean-search-topic-modeling"
5. "Assemble gra4164 lecture 3 and update inventory" (lecture collection + plan.yml + inventory)

## Verification

1. `teach validate` — 0 errors after each step
2. `teach build gra4164-lecture-03 --audience student --lang en --format html` — renders
3. `teach build sotu-boolean-search-topic-modeling --audience student --lang en --format html` — renders
4. `teach build sotu-boolean-search-topic-modeling --audience teacher --lang en --format exercise-sheet` — renders with solution
5. `pytest tests/test_schema.py` — all pass
