import pytest
import subprocess

def test_json_schemas_validity():
    result = subprocess.run(["python3", "scripts/19_validate_json_contracts.py"], capture_output=True, text=True)
    assert result.returncode == 0, f"Erreur de validation des schémas:\n{result.stderr}"
