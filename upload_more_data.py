"""
CityCare Hospital Management System - Automated Additional Data Loader
Runs the Cypher queries in seed_more_data.cypher directly into the configured Neo4j AuraDB instance.
"""

import sys
from pathlib import Path

# Add backend directory to path to reuse db.py and connection pool
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from db import run_query, close_driver, get_driver

def run_cypher_file(file_path: Path):
    print("=" * 65)
    print("      Uploading Additional Dataset to Neo4j AuraDB")
    print("=" * 65)
    
    if not file_path.exists():
        print(f"[ERROR] Could not find {file_path}")
        return

    # Verify connection
    try:
        driver = get_driver()
        with driver.session() as s:
            s.run("RETURN 1")
        print("[OK] Connected to Neo4j successfully!\n")
    except Exception as e:
        print(f"[ERROR] Cannot connect to Neo4j: {e}")
        return

    content = file_path.read_text(encoding="utf-8")
    
    # Split queries by semicolon (ignoring comments)
    raw_statements = content.split(";")
    queries = []
    for stmt in raw_statements:
        # Strip comments and whitespace
        lines = [line for line in stmt.splitlines() if not line.strip().startswith("//")]
        clean_stmt = "\n".join(lines).strip()
        if clean_stmt:
            queries.append(clean_stmt)

    print(f"Executing {len(queries)} Cypher statements into AuraDB...")
    success_count = 0
    for idx, q in enumerate(queries, 1):
        try:
            run_query(q)
            success_count += 1
            # Print brief progress indicator
            first_line = q.split("\n")[0][:60]
            print(f"  [{idx}/{len(queries)}] {first_line}...")
        except Exception as err:
            print(f"  [WARN] Query {idx} failed: {err}")

    print("\n" + "=" * 65)
    print(f"[SUCCESS] Uploaded {success_count}/{len(queries)} statements!")
    
    # Show summary counts
    node_res = run_query("MATCH (n) RETURN count(n) AS nodes")
    rel_res = run_query("MATCH ()-[r]->() RETURN count(r) AS rels")
    doc_res = run_query("MATCH (d:Doctor) RETURN count(d) AS docs")
    dep_res = run_query("MATCH (dep:Department) WHERE dep.name IS NOT NULL RETURN count(dep) AS depts")
    pat_res = run_query("MATCH (p:Patient) RETURN count(p) AS patients")
    
    print(f"  * Total Graph Nodes:         {node_res[0]['nodes']}")
    print(f"  * Total Relationships:       {rel_res[0]['rels']}")
    print(f"  * Active Doctors:            {doc_res[0]['docs']}")
    print(f"  * Active Departments:        {dep_res[0]['depts']}")
    print(f"  * Total Patients:            {pat_res[0]['patients']}")
    print("=" * 65)

if __name__ == "__main__":
    try:
        cypher_file = ROOT_DIR / "seed_more_data.cypher"
        run_cypher_file(cypher_file)
    finally:
        close_driver()
