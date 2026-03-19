# GRA4164 Migration Inventory

This file tracks the migration of legacy material from
`course-inbox/nlp-for-business/` into LearnForge's canonical course/object
structure.

## Locked Decisions

- Canonical course id: `gra4164`
- Course language at migration start: `en` only
- Legacy notebooks and LaTeX slides are reference material, not source of truth
- New teaching material should prefer:
  - exposition in `.qmd`
  - exercises in LearnForge `exercise` objects
  - solutions in `solution.en.qmd`
- No bulk import of the legacy `data/` folder (SOTU corpus, shakespeare.txt, GDP.csv)
- No promotion of LaTeX build artifacts, beamer themes, compiled PDFs, or the
  nested legacy git repository
- Owners: vegard + leif

## Migration Buckets

### Promote First

These items map well to the course structure and can be turned into reusable
concepts and exercises with moderate rewriting.

| Legacy source | Action | Target kind | Proposed target id |
| --- | --- | --- | --- |
| Lecture 1 tex + `Working_with_text_data.ipynb` | Rewrite into NLP foundations exposition | concept | `text-as-data-introduction` |
| Lecture 2 tex + `cleaningpreparation/` module | Rewrite around tokenization, cleaning, stemming | concept | `text-preprocessing-nlp` |
| Lecture 2 tex + `nlp_methods_tfidf.tex` + `nlp_methods_cosine.tex` + `Bow_tfidf_cosine_similarity.ipynb` | Rewrite BoW/TF-IDF/cosine exposition | concept | `bag-of-words-tfidf-cosine` |
| Lecture 3 tex + `nlp_methods_countboolean.tex` | Rewrite Boolean/dictionary text methods | concept | `boolean-dictionary-methods-nlp` |
| Lecture 3 tex + `nlp_methods_olsregularization.tex` + `nlp_methods_naivebayes.tex` | Rewrite text regression and Naive Bayes | concept | `text-regression-classification` |
| Lecture 3 tex + `nlp_methods_pcalda.tex` | Rewrite LSA/LDA topic modelling | concept | `topic-modeling-lsa-lda` |
| Lecture 4 tex (`N_gram_language_model.tex`) + `Predict_the_next_token_part1.ipynb` | Rewrite n-gram language models | concept | `ngram-language-models` |
| Lecture 6 tex + `nlp_methods_word2vec.tex` | Rewrite word embeddings / Word2Vec | concept | `word-embeddings-word2vec` |
| Lecture 7 tex + `nlp_llms_intro.tex` + `llm_tokenizers.ipynb` | Rewrite LLM intro and tokenization | concept | `llm-introduction-tokenization` |
| Lecture 8 tex + `nlp_llms_transformer.tex` | Rewrite attention and transformers | concept | `attention-and-transformers` |
| Lecture 9 tex + `nlp_llms_inputoutput.tex` | Rewrite LLM I/O architecture | concept | `llm-input-output-architecture` |
| Lecture 9 tex + `nlp_llms_trainingandfinetuning.tex` | Rewrite LLM training and fine-tuning | concept | `llm-training-and-finetuning` |
| Lecture 11 tex + `nlp_llms_promptengineering.tex` | Rewrite prompt engineering | concept | `prompt-engineering-for-nlp` |
| `Bow_tfidf_cosine_similarity.ipynb` | Convert to guided lab exercise | exercise | `bow-tfidf-shakespeare-lab` |
| `Predict_the_next_token_part1.ipynb` + `part2_nn.ipynb` | Convert to bigram model lab | exercise | `bigram-language-model-lab` |
| `assignment1.ipynb` | Convert to exercise + teacher solution | exercise | `sotu-boolean-search-topic-modeling` |
| `assignment2.ipynb` | Convert to exercise + teacher solution | exercise | `word-embeddings-sotu-analysis` |
| `assignment3.ipynb` | Convert to exercise + teacher solution | exercise | `bert-finetuning-text-classification` |
| `assignment4.ipynb` | Convert to exercise + teacher solution | exercise | `prompt-engineering-reflection` |

### Rewrite Fresh

These topics need fresh authoring rather than direct migration from legacy material.

| Topic | Reason | Planned target kind |
| --- | --- | --- |
| Web scraping / data extraction | `Extracting_data_from_the_web.ipynb` is tooling-heavy and needs fresh treatment | concept or resource |
| Sentiment analysis | Currently embedded in assignment 1 only; standalone concept would make it reusable | concept |
| Named Entity Recognition | Mentioned in `Working_with_text_data.ipynb` (spaCy NER) but not a lecture topic | concept |

### Defer

These can stay in the inbox until the core NLP content is migrated.

| Legacy source | Reason for deferral |
| --- | --- |
| `Predict_the_next_token_part3_mpl.ipynb` | MLP language model; more implementation-heavy than initially needed |
| `Extracting_data_from_the_web.ipynb` | Tooling notebook, not core NLP content |
| `inspect_data.ipynb` | Data exploration helper, not standalone teaching content |
| `FinalExam/` | Exam material; handle separately |
| Misc tex files (course outlines, old lecture variants) | Reference only |

### Drop Or Archive

| Legacy source | Reason |
| --- | --- |
| `.git/` inside course-inbox | Nested repo noise |
| `beamerthemebi/` and `beamerthemebi.sty` (duplicated across folders) | Theme files, not content |
| `*.bbl`, `*.blg`, `*.brf`, `*.nav`, `*.snm`, `*.synctex.gz`, `*.toc`, `*.dep`, `*.vrb` | LaTeX build artifacts |
| Compiled PDFs in lecture dirs | Build outputs, not source |
| `.virtual_documents/` | Jupyter virtual document artifacts |
| `neural_network*.png/pdf`, `word2vec_state_of_union.model` | Generated artifacts |
| `GRA4164 Assignments Evaluation Guidelines.docx/pdf` | Administrative docs |
| `sotu.zip` | Compressed copy of data already in `sotu/` |

## Proposed Lecture Collections

| Collection id | Title | Planned items |
| --- | --- | --- |
| `gra4164-lecture-01` | Introduction to Text as Data | `text-as-data-introduction` |
| `gra4164-lecture-02` | BoW, TF-IDF, Cosine Similarity | `text-preprocessing-nlp`, `bag-of-words-tfidf-cosine` |
| `gra4164-lecture-03` | BoW-Based Methods | `boolean-dictionary-methods-nlp`, `text-regression-classification`, `topic-modeling-lsa-lda` |
| `gra4164-lecture-04` | N-gram Language Models | `ngram-language-models` |
| `gra4164-lecture-05` | Practical Day 1 | `bow-tfidf-shakespeare-lab`, `bigram-language-model-lab` |
| `gra4164-lecture-06` | Word Embeddings | `word-embeddings-word2vec` |
| `gra4164-lecture-07` | LLMs and Tokenization | `llm-introduction-tokenization` |
| `gra4164-lecture-08` | Attention and Transformers | `attention-and-transformers` |
| `gra4164-lecture-09` | LLM Architecture and Training | `llm-input-output-architecture`, `llm-training-and-finetuning` |
| `gra4164-lecture-10` | Practical Day 2 | `word-embeddings-sotu-analysis`, `bert-finetuning-text-classification` |
| `gra4164-lecture-11` | Prompt Engineering | `prompt-engineering-for-nlp`, `prompt-engineering-reflection` |

## Proposed Assignment Collections

| Collection id | Title | Planned items |
| --- | --- | --- |
| `gra4164-assignment-01` | Assignment 1 - Boolean search and topic modelling | `sotu-boolean-search-topic-modeling` |
| `gra4164-assignment-02` | Assignment 2 - Word embeddings and semantic change | `word-embeddings-sotu-analysis` |
| `gra4164-assignment-03` | Assignment 3 - BERT fine-tuning for text classification | `bert-finetuning-text-classification` |
| `gra4164-assignment-04` | Assignment 4 - Prompt engineering and reflection | `prompt-engineering-reflection` |

## Cross-Course References

Content objects should list relevant concepts from other courses in `related:`:

- `text-regression-classification` → related: `logistic-regression-classification` (tem0052), `linear-regression-prediction` (tem0052)
- `topic-modeling-lsa-lda` → related: `principal-component-analysis` (tem0052, when promoted)

## Notes

- **Image licensing**: Several images in `tex/modules/llms/` are sourced from
  Jurafsky's textbook (filenames like `jurafsky101`, `jurafsky105`). These cannot
  be directly included in LearnForge objects — replace or attribute properly.
- **Data assets**: The SOTU corpus (228 speeches), shakespeare.txt, and GDP.csv
  should be referenced via resource objects or exercise setup instructions, not
  bulk-imported.
- **Computational requirements**: Assignment 3 (BERT fine-tuning) is documented as
  GPU-recommended, with smaller-model and smaller-subset fallbacks for limited
  hardware.

## Promoted in the current checkpoint

- Concept: `text-as-data-introduction`
- Concept: `text-preprocessing-nlp`
- Concept: `bag-of-words-tfidf-cosine`
- Concept: `boolean-dictionary-methods-nlp`
- Concept: `text-regression-classification`
- Concept: `topic-modeling-lsa-lda`
- Concept: `ngram-language-models`
- Concept: `word-embeddings-word2vec`
- Concept: `llm-introduction-tokenization`
- Concept: `attention-and-transformers`
- Concept: `llm-input-output-architecture`
- Concept: `llm-training-and-finetuning`
- Concept: `prompt-engineering-for-nlp`
- Exercise: `sotu-boolean-search-topic-modeling`
- Exercise: `bow-tfidf-shakespeare-lab`
- Exercise: `bigram-language-model-lab`
- Exercise: `word-embeddings-sotu-analysis`
- Exercise: `bert-finetuning-text-classification`
- Exercise: `prompt-engineering-reflection`
- Assignment collection: `gra4164-assignment-01`
- Assignment collection: `gra4164-assignment-02`
- Assignment collection: `gra4164-assignment-03`
- Assignment collection: `gra4164-assignment-04`
- Lecture collection: `gra4164-lecture-01`
- Lecture collection: `gra4164-lecture-02`
- Lecture collection: `gra4164-lecture-03`
- Lecture collection: `gra4164-lecture-04`
- Lecture collection: `gra4164-lecture-05`
- Lecture collection: `gra4164-lecture-06`
- Lecture collection: `gra4164-lecture-07`
- Lecture collection: `gra4164-lecture-08`
- Lecture collection: `gra4164-lecture-09`
- Lecture collection: `gra4164-lecture-10`
- Lecture collection: `gra4164-lecture-11`

## Next Migration Actions

1. Decide whether the final presentation session should be represented as a
   canonical collection or remain syllabus-only course structure.
2. Add a representative `gra4164` target to `representative-targets.yml` so the
   course is protected by repo-level representative builds as well as its dedicated
   test file.
3. Leave all remaining legacy files in the inbox until explicitly promoted.
