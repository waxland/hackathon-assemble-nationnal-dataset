import pytest
import subprocess
import os

def test_neo4j_export():
    result = subprocess.run(["python3", "scripts/12_export_graph_neo4j.py"], capture_output=True, text=True)
    assert result.returncode == 0, f"Erreur Neo4j export:\n{result.stderr}"
    assert os.path.exists("data/neo4j_export/nodes_programs.csv")
    assert os.path.exists("data/neo4j_export/relationships.csv")
