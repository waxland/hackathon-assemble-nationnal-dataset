import pytest
import subprocess
import os
import sqlite3

def test_sqlite_export():
    result = subprocess.run(["python3", "scripts/11_export_to_sqlite.py"], capture_output=True, text=True)
    assert result.returncode == 0, f"Erreur SQLite export:\n{result.stderr}"
    assert os.path.exists("data/france2030.sqlite")
    
    # Check that at least one table has data
    conn = sqlite3.connect("data/france2030.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM programs")
    count = cursor.fetchone()[0]
    assert count > 0, "La base SQLite est vide."
    conn.close()
