# TEM00UU Migration Inventory

This file tracks the migration of legacy material from
`course-inbox/Blockchain-foundations/` into LearnForge's canonical course/object
structure.

## Locked Decisions

- Canonical temporary course id: `tem00uu`
- Course language at migration start: `en` only
- The current LaTeX course description is reference material, not source of truth
- Part A is the only migration-ready block in the current sketch
- Part B remains intentionally TBA and stays out of canonical lecture plans for now
- New teaching material should prefer:
  - exposition in `.qmd`
  - reusable Python in plain `.py`
  - coding tasks in LearnForge `exercise` objects
  - teacher guidance in `solution.en.qmd`
- No promotion of compiled LaTeX artifacts, generated PDFs, or nested legacy git
  metadata
- Do not add `tem00uu` representative targets until at least one lecture collection is
  stable enough to act as a regression target

## Migration Buckets

### Promote First

These items are the clearest and most reusable foundation slice in the current course
sketch.

| Legacy source | Action | Target kind | Proposed target id |
| --- | --- | --- | --- |
| `Course_description/course_description.tex` Lecture 1 | Split into reusable foundations on ledgers and hashes | concept + exercise | `distributed-ledgers-and-trust`, `cryptographic-hash-functions`, `hash-avalanche-python` |
| `Course_description/course_description.tex` Lecture 2 | Rewrite around key pairs and signatures | concept + exercise | `public-key-cryptography`, `digital-signatures`, `signature-verification-lab` |
| `Course_description/course_description.tex` Lecture 3 | Rewrite into transaction structure plus UTXO ledger rules | concept + exercise | `cryptocurrency-transactions`, `utxo-transaction-model`, `transaction-validation-lab` |
| `Course_description/course_description.tex` Lecture 4 | Rewrite around block structure and Merkle trees | concept + exercise | `blockchain-data-structures`, `merkle-trees`, `simple-blockchain-lab` |
| `Course_description/course_description.tex` Lecture 5 | Rewrite consensus framing into chain selection, PoW/PoS comparison, and a small PoW coding task | concept + exercise | `blockchain-consensus-and-canonical-chain`, `proof-of-work-and-proof-of-stake`, `proof-of-work-mining-lab` |
| `Course_description/course_description.tex` Lecture 6 | Rewrite networking material into peer-to-peer structure, gossip/discovery, and a lightweight simulation | concept + exercise | `blockchain-peer-to-peer-networks`, `gossip-protocol-and-peer-discovery`, `gossip-protocol-simulation` |
| `Course_description/course_description.tex` Lecture 7 | Rewrite into smart-contract execution, Layer 2 architecture, and a tooling-neutral contract simulation | concept + exercise | `smart-contracts-and-the-evm`, `layer-2-scaling`, `smart-contract-state-machine-lab` |
| `Course_description/course_description.tex` Lecture 8 ethics block | Rewrite into one integrated ethics, regulation, and sustainability concept plus a concept-only lecture collection | concept | `blockchain-ethics-law-and-sustainability`, `tem00uu-lecture-08` |

### Rewrite Fresh

These topics are present in the sketch but need more design work before they can
become clean canonical LearnForge content.

| Topic | Reason | Planned target kind |
| --- | --- | --- |
| Semester project brief and grading rubric | Current description is too high-level for canonical assignment copy | assignment / course material |
| Business uses of blockchain | Part B is named but not yet scoped into reusable teaching units | concept + resources |
| Cryptocurrency markets and forecasting | The sketch explicitly leaves this block TBA | concept + exercise later |

### Defer

These should remain in the inbox until the first cryptography foundation slice is
stable.

| Legacy source | Reason for deferral |
| --- | --- |
| `Course_description/course_description.pdf` | Generated artifact, useful only as a convenience reference |
| Smart-contract tooling choices (`brownie`, `web3.py`, local chain tooling) | Better decided when the smart-contract slice is actually authored |
| The full Part B market / forecasting block | Still too underspecified to promote responsibly |

### Drop Or Archive

| Legacy source | Reason |
| --- | --- |
| `.git/` inside `course-inbox/Blockchain-foundations/` | Tooling noise, not course source |
| `*.aux`, `*.fdb_latexmk`, `*.fls`, `*.out`, generated PDF byproducts | LaTeX build artifacts |

## Proposed First Canonical Slice

Build the first LearnForge checkpoint for `tem00uu` around the early Part A
cryptography foundations.

### First concept candidates

- `distributed-ledgers-and-trust`
- `cryptographic-hash-functions`
- `public-key-cryptography`
- `digital-signatures`

### First exercise candidates

- `hash-avalanche-python`
- `signature-verification-lab`

### First lecture candidates

- `tem00uu-lecture-01` ledgers + hashes
- `tem00uu-lecture-02` keys + signatures

## Current Canonical Checkpoint

The first eight Part A slices are now scaffolded in canonical LearnForge form.

### Implemented objects

- concept: `distributed-ledgers-and-trust`
- concept: `cryptographic-hash-functions`
- concept: `public-key-cryptography`
- concept: `digital-signatures`
- concept: `cryptocurrency-transactions`
- concept: `utxo-transaction-model`
- concept: `blockchain-data-structures`
- concept: `merkle-trees`
- concept: `blockchain-consensus-and-canonical-chain`
- concept: `proof-of-work-and-proof-of-stake`
- concept: `blockchain-peer-to-peer-networks`
- concept: `gossip-protocol-and-peer-discovery`
- concept: `smart-contracts-and-the-evm`
- concept: `layer-2-scaling`
- concept: `blockchain-ethics-law-and-sustainability`
- exercise: `hash-avalanche-python`
- exercise: `signature-verification-lab`
- exercise: `transaction-validation-lab`
- exercise: `simple-blockchain-lab`
- exercise: `proof-of-work-mining-lab`
- exercise: `gossip-protocol-simulation`
- exercise: `smart-contract-state-machine-lab`
- lecture collection: `tem00uu-lecture-01`
- lecture collection: `tem00uu-lecture-02`
- lecture collection: `tem00uu-lecture-03`
- lecture collection: `tem00uu-lecture-04`
- lecture collection: `tem00uu-lecture-05`
- lecture collection: `tem00uu-lecture-06`
- lecture collection: `tem00uu-lecture-07`
- lecture collection: `tem00uu-lecture-08`

### Course plan status

- `courses/tem00uu/plan.yml` now includes `tem00uu-lecture-01`
- `courses/tem00uu/plan.yml` now includes `tem00uu-lecture-02`
- `courses/tem00uu/plan.yml` now includes `tem00uu-lecture-03`
- `courses/tem00uu/plan.yml` now includes `tem00uu-lecture-04`
- `courses/tem00uu/plan.yml` now includes `tem00uu-lecture-05`
- `courses/tem00uu/plan.yml` now includes `tem00uu-lecture-06`
- `courses/tem00uu/plan.yml` now includes `tem00uu-lecture-07`
- `courses/tem00uu/plan.yml` now includes `tem00uu-lecture-08`
- The first transaction exercise stays in plain Python data structures to keep the
  focus on ledger-state validation rather than reusable class design
- The first blockchain data-structure exercise includes a small deterministic
  Merkle-root helper while staying otherwise sequential and lightweight
- The first consensus exercise keeps the coding strictly on Proof of Work while
  leaving Proof of Stake in the comparative concept discussion
- The first networking exercise keeps propagation local and deterministic instead of
  depending on real socket setup or classroom machine configuration
- The first smart-contract exercise stays tooling-neutral and models contract logic as
  a local state machine rather than committing the course to Solidity or `web3.py`
- Lecture 8 is now represented canonically as the ethics, regulation, and
  sustainability slice rather than a combined lecture with project logistics
- The semester project brief remains intentionally deferred until the assessment is
  stable enough to promote as its own canonical object
- Part B remains intentionally deferred until the next migration pass

## Next Migration Actions

1. Decide whether the semester project should become a canonical assignment
   collection, a lighter course-material object, or remain syllabus-only for another
   draft cycle.
2. If project material is promoted later, keep it outside the lecture sequence rather
   than forcing it into `tem00uu-lecture-08`.
3. Begin scoping Part B into reusable business, market, and forecasting objects
   instead of carrying it as a single TBA block.
4. Leave Part B outside the canonical plan until the business / forecasting scope is
   actually designed.
