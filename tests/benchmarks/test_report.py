# ABOUTME: Tests for the two documents a run generates: the one saying how the benchmark is
# ABOUTME: configured, and the one saying what came out.

from pathlib import Path

from benchmarks import report


def scored(**overrides: object) -> dict[str, object]:
    entry = {
        "model": "quickqual",
        "dataset": "fives",
        "declared": {
            "grid": 512,
            "network_grid": 512,
            "ensemble": 1,
            "device": "mps",
            "grades": "good, usable, bad",
            "named_grades": ("good", "usable", "bad"),
            "gate": "none; no catalogued pipeline gates on it",
            "upstream": {"commit": "a94feb02a79efa5380f6b0d863d1b80ab4c73e4e"},
        },
        "grade_source": ["derived"],
        "padding": 0.0,
        "counts": {"processed": 200, "total": 200, "complete": True, "excluded": {}},
        "summary": {
            "photographs": 200,
            "graded": 198,
            "declined": 1,
            "failed": 1,
            "coverage": 0.99,
            "reference_grades": ["good", "usable", "bad"],
            "gradeable": {"photographs": 198, "accuracy": 0.885, "roc_auc": None, "kappa": 0.7},
            "three_class": None,
            "gate": None,
        },
    }
    entry.update(overrides)
    return entry


def rows(**overrides: str) -> dict[str, str]:
    entry = {
        "key": "a",
        "subset": "main",
        "split": "train",
        "grade": "good",
        "outcome": "graded",
        "verdict": "good",
        "gradeable": "0.9",
        "carried_by_its_pipeline": "",
        "readers": "",
    }
    entry.update(overrides)
    return entry


def configured() -> dict[str, object]:
    """What a run knows before it measures anything."""
    return {
        "models": [{"slug": "quickqual", "declared": scored()["declared"]}],
        "datasets": [
            {
                "slug": "fives",
                "total": 200,
                "excluded": {"below the size floor": 3},
                "grade_source": ["derived"],
                "padding": 0.0,
            }
        ],
    }


def test_the_configuration_page_names_every_declared_model_including_the_absent(
    tmp_path: Path,
) -> None:
    path = report.write_docs(
        "quality",
        configured(),
        missing_models={"lunet-quality": "no adapter written"},
        missing_datasets={"eyeq": "no store built"},
        columns={"key": "the photograph"},
        into=tmp_path,
    )

    written = path.read_text()
    assert "lunet-quality" in written and "no adapter written" in written
    assert "eyeq" in written and "no store built" in written
    assert "`a94feb02`" in written, "a number with no commit behind it is an anecdote"


def test_the_configuration_page_explains_every_column_of_the_evidence(tmp_path: Path) -> None:
    written = report.write_docs(
        "quality",
        configured(),
        missing_models={},
        missing_datasets={},
        columns={"key": "the photograph", "gradeable": "how confident it is"},
        into=tmp_path,
    ).read_text()

    assert "| `key` | the photograph |" in written
    assert "| `gradeable` | how confident it is |" in written


def test_the_results_page_leads_with_model_by_dataset(tmp_path: Path) -> None:
    written = report.write_results(
        "quality", [scored()], {("quickqual", "fives"): [rows()]}, into=tmp_path
    ).read_text()

    assert written.index("## 1.") < written.index("## 2.")
    assert "quickqual" in written
    assert "out-of-sample" in written


def test_the_results_page_says_how_many_of_how_many_ran(tmp_path: Path) -> None:
    written = report.write_results(
        "quality",
        [scored()],
        {("quickqual", "fives"): [rows()]},
        missing_models={"lunet-quality": "no adapter written"},
        missing_datasets={"eyeq": "no store built"},
        into=tmp_path,
    ).read_text()

    assert "1 of 2 declared models" in written
    assert "1 of 2 declared datasets" in written


def test_a_partial_result_says_so(tmp_path: Path) -> None:
    entry = scored()
    entry["counts"] = {"processed": 20, "total": 488, "complete": False, "excluded": {}}

    written = report.write_results(
        "quality", [entry], {("quickqual", "fives"): [rows()]}, into=tmp_path
    ).read_text()

    assert "20 of 488" in written
    assert "not complete" in written


def test_the_detail_breaks_a_dataset_into_its_splits(tmp_path: Path) -> None:
    evidence = {
        ("quickqual", "fives"): [
            rows(key="a", split="train", grade="good", gradeable="0.9"),
            rows(key="b", split="test", grade="bad", gradeable="0.1"),
        ]
    }

    written = report.write_results("quality", [scored()], evidence, into=tmp_path).read_text()

    assert "fives / main / train" in written
    assert "fives / main / test" in written


def test_a_dataset_whose_splits_carry_different_marks_is_never_only_summarised(
    tmp_path: Path,
) -> None:
    entry = scored(dataset="eyeq")
    evidence = {
        ("quickqual", "eyeq"): [
            rows(key="a", split="train"),
            rows(key="b", split="test"),
        ]
    }

    written = report.write_results("quality", [entry], evidence, into=tmp_path).read_text()

    assert "in-sample" in written and "out-of-sample" in written
    assert "splits carry different marks" in written


def test_every_heading_is_numbered(tmp_path: Path) -> None:
    for written in (
        report.write_docs(
            "quality",
            configured(),
            missing_models={},
            missing_datasets={},
            columns={},
            into=tmp_path,
        ).read_text(),
        report.write_results(
            "quality", [scored()], {("quickqual", "fives"): [rows()]}, into=tmp_path
        ).read_text(),
    ):
        headings = [line for line in written.splitlines() if line.startswith("## ")]
        assert headings == [
            f"## {index}. {heading.split('. ', 1)[1]}"
            for index, heading in enumerate(headings, start=1)
        ]


def test_the_configuration_page_can_be_written_before_anything_is_measured(
    tmp_path: Path,
) -> None:
    written = report.write_docs(
        "quality",
        configured(),
        missing_models={},
        missing_datasets={},
        columns={},
        into=tmp_path,
    ).read_text()

    assert "before" in written, "the page says when it was written, because it matters"
    assert "3 below the size floor" in written, "the exclusions are known from the manifest alone"


def test_agreement_beyond_chance_is_reported_beside_accuracy(tmp_path: Path) -> None:
    evidence = {
        ("quickqual", "fives"): [
            rows(key="a", grade="good", gradeable="0.9"),
            rows(key="b", grade="bad", verdict="bad", gradeable="0.1"),
        ]
    }

    written = report.write_results("quality", [scored()], evidence, into=tmp_path).read_text()

    assert "Cohen's κ" in written
    assert "| 1.000 | 1.000 |" in written, "perfect agreement, beyond chance too"


def test_a_group_with_one_class_has_no_agreement_to_measure(tmp_path: Path) -> None:
    evidence = {
        ("quickqual", "fives"): [
            rows(key="a", grade="good", gradeable="0.9"),
            rows(key="b", grade="good", gradeable="0.8"),
        ]
    }

    written = report.write_results("quality", [scored()], evidence, into=tmp_path).read_text()

    assert "| 1.000 | — | — |" in written, "κ and a ranking both need both classes"
