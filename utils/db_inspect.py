#!/usr/bin/env python3
"""
Database inspection utility for agent_memory.db
"""

import sqlite3
from typing import List, Tuple

def inspect_database(db_path: str = "agent_memory.db") -> Tuple[List[str], List[Tuple]]:
    """Inspect database structure and sample data"""
    with sqlite3.connect(db_path) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        
        samples = []
        for table in tables:
            table_name = table[0]
            if not table_name.startswith('sqlite_'):
                samples.append((
                    table_name,
                    conn.execute(f"SELECT * FROM {table_name} LIMIT 1").fetchone()
                ))
    
    return tables, samples

if __name__ == "__main__":
    tables, samples = inspect_database()
    print("\nDatabase Structure:")
    print("-" * 40)
    for table in tables:
        print(f"Table: {table[0]}")
    
    print("\nSample Data:")
    print("-" * 40)
    for table_name, sample in samples:
        print(f"{table_name}: {sample}")