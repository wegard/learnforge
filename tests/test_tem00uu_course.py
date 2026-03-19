from __future__ import annotations

from app.assembly import assemble_target
from app.config import REPO_ROOT
from app.indexer import load_repository


def test_tem00uu_course_is_indexed_with_first_eight_lecture_slices() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)

    course = index.courses["tem00uu"]

    assert course.model.id == "tem00uu"
    assert course.model.languages == ["en"]
    assert course.plan.lectures == [
        "tem00uu-lecture-01",
        "tem00uu-lecture-02",
        "tem00uu-lecture-03",
        "tem00uu-lecture-04",
        "tem00uu-lecture-05",
        "tem00uu-lecture-06",
        "tem00uu-lecture-07",
        "tem00uu-lecture-08",
    ]
    assert course.plan.assignments == []


def test_tem00uu_course_assembles_with_first_eight_lecture_slices() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "tem00uu",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    assert assembly.target.kind == "course"
    assert assembly.target.identifier == "tem00uu"
    assert "TEM 00UU - Foundations of Cryptocurrency and Blockchain" in assembly.markdown
    assert "Lecture 1 - Ledgers, trust, and cryptographic hashes" in assembly.markdown
    assert "Lecture 2 - Public keys and digital signatures" in assembly.markdown
    assert "Lecture 3 - Transactions and the UTXO model" in assembly.markdown
    assert "Lecture 4 - Block structure and Merkle trees" in assembly.markdown
    assert "Lecture 5 - Consensus and mining" in assembly.markdown
    assert "Lecture 6 - Peer-to-peer networking and gossip" in assembly.markdown
    assert "Lecture 7 - Smart contracts and Layer 2 scaling" in assembly.markdown
    assert "Lecture 8 - Ethics, regulation, and sustainability" in assembly.markdown
    assert "Hash avalanche in Python" in assembly.markdown
    assert "Signature verification lab" in assembly.markdown
    assert "Transaction validation lab" in assembly.markdown
    assert "Simple blockchain lab" in assembly.markdown
    assert "Proof-of-work mining lab" in assembly.markdown
    assert "Gossip protocol simulation" in assembly.markdown
    assert "Smart contract state machine lab" in assembly.markdown
    assert "Part A: Cryptography and blockchain foundations" in assembly.markdown
    assert "Part B: Business, markets, and forecasting" in assembly.markdown
    assert "semester-long group project" in assembly.markdown


def test_tem00uu_lecture_01_assembly_expands_first_foundation_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "tem00uu-lecture-01",
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
        "distributed-ledgers-and-trust",
        "cryptographic-hash-functions",
        "hash-avalanche-python",
    ]
    assert "## Ledgers are coordination technology" in assembly.markdown
    assert "## Hash functions turn arbitrary data into short fingerprints" in assembly.markdown
    assert "## Lab brief" in assembly.markdown


def test_tem00uu_lecture_02_assembly_expands_key_and_signature_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "tem00uu-lecture-02",
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
        "public-key-cryptography",
        "digital-signatures",
        "signature-verification-lab",
    ]
    assert "## Public-key cryptography separates disclosure from control" in assembly.markdown
    assert "## Digital signatures prove authorization over a message" in assembly.markdown
    assert "## Lab brief" in assembly.markdown


def test_tem00uu_lecture_03_assembly_expands_transaction_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "tem00uu-lecture-03",
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
        "cryptocurrency-transactions",
        "utxo-transaction-model",
        "transaction-validation-lab",
    ]
    assert "## Transactions express state changes, not just payments" in assembly.markdown
    assert "## A UTXO is a spendable chunk, not an account balance" in assembly.markdown
    assert "## Lab brief" in assembly.markdown


def test_tem00uu_lecture_04_assembly_expands_block_structure_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "tem00uu-lecture-04",
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
        "blockchain-data-structures",
        "merkle-trees",
        "simple-blockchain-lab",
    ]
    assert "## Blocks package transactions into an ordered hash-linked history" in assembly.markdown
    assert "## Merkle trees compress many transaction hashes into one commitment" in assembly.markdown
    assert "## Lab brief" in assembly.markdown


def test_tem00uu_lecture_05_assembly_expands_consensus_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "tem00uu-lecture-05",
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
        "blockchain-consensus-and-canonical-chain",
        "proof-of-work-and-proof-of-stake",
        "proof-of-work-mining-lab",
    ]
    assert "## Consensus chooses one history from many valid candidates" in assembly.markdown
    assert (
        "## Proof of Work and Proof of Stake make Sybil resistance costly in different ways"
        in assembly.markdown
    )
    assert "## Lab brief" in assembly.markdown


def test_tem00uu_lecture_06_assembly_expands_networking_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "tem00uu-lecture-06",
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
        "blockchain-peer-to-peer-networks",
        "gossip-protocol-and-peer-discovery",
        "gossip-protocol-simulation",
    ]
    assert (
        "## Blockchain networks are peer-to-peer systems, not client-server services"
        in assembly.markdown
    )
    assert (
        "## Gossip spreads transactions and blocks through repeated local relay"
        in assembly.markdown
    )
    assert "## Lab brief" in assembly.markdown


def test_tem00uu_lecture_07_assembly_expands_smart_contract_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "tem00uu-lecture-07",
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
        "smart-contracts-and-the-evm",
        "layer-2-scaling",
        "smart-contract-state-machine-lab",
    ]
    assert (
        "## Smart contracts are shared state machines executed by the blockchain"
        in assembly.markdown
    )
    assert (
        "## Layer 2 scaling moves activity off the base layer without abandoning it"
        in assembly.markdown
    )
    assert "## Lab brief" in assembly.markdown


def test_tem00uu_lecture_08_assembly_expands_ethics_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "tem00uu-lecture-08",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == ["blockchain-ethics-law-and-sustainability"]
    assert (
        "## Blockchain systems create governance tradeoffs, not just technical capabilities"
        in assembly.markdown
    )
