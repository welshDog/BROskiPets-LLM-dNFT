"""
Guardrail tests for documentation data mirrors.
"""
import json
from pathlib import Path


def test_docs_eep_metadata_mirror_matches_squad_json():
    repo_root = Path(__file__).parent.parent
    mirror_path = repo_root / "docs" / "BROskiPets_all_EEPs_MetaData"
    squad_path = repo_root / "eeps" / "squad.json"

    mirror_data = json.loads(mirror_path.read_text(encoding="utf-8"))
    squad_data = json.loads(squad_path.read_text(encoding="utf-8"))

    assert mirror_data == squad_data, (
        "docs/BROskiPets_all_EEPs_MetaData is out of sync with eeps/squad.json. "
        "Update the docs mirror after editing squad.json."
    )
