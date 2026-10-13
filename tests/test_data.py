"""Unit test: check that all simulated enterprise JSON files are valid."""

import json

from app.config import DATA_DIR


def test_enterprise_json_files_are_valid_and_nonempty():
    filenames = [
        "customers.json",
        "employees.json",
        "tickets.json",
        "policies.json",
    ]

    for filename in filenames:
        path = DATA_DIR / filename
        assert path.exists(), f"Missing file: {filename}"

        with path.open("r", encoding="utf-8") as file:
            records = json.load(file)

        assert isinstance(records, list)
        assert records, f"{filename} should contain at least one record"
