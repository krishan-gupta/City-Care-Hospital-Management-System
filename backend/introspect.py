"""
Schema introspection script to inspect the active Neo4j database
and compare with the PRD data model.
"""
import sys
import json
from db import get_driver, run_query, close_driver

def introspect():
    print("Connecting to Neo4j...")
    try:
        driver = get_driver()
        with driver.session() as session:
            # 1. Labels
            print("\n=== LABELS ===")
            labels_res = session.run("CALL db.labels() YIELD label RETURN label ORDER BY label").data()
            labels = [r["label"] for r in labels_res]
            print(labels)

            # 2. Relationship Types
            print("\n=== RELATIONSHIP TYPES ===")
            rels_res = session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType").data()
            rels = [r["relationshipType"] for r in rels_res]
            print(rels)

            # 3. Property Keys
            print("\n=== PROPERTY KEYS ===")
            props_res = session.run("CALL db.propertyKeys() YIELD propertyKey RETURN propertyKey ORDER BY propertyKey").data()
            props = [r["propertyKey"] for r in props_res]
            print(props)

            # 4. Node counts by label
            print("\n=== NODE COUNTS BY LABELS ===")
            counts_res = session.run("MATCH (n) RETURN labels(n) AS labels, count(*) AS count ORDER BY count DESC").data()
            for r in counts_res:
                print(f"  {r['labels']}: {r['count']}")

            # 5. Sample properties for each label
            print("\n=== SAMPLE PROPERTIES PER LABEL ===")
            for label in labels:
                sample = session.run(f"MATCH (n:`{label}`) RETURN properties(n) AS props LIMIT 1").data()
                if sample:
                    print(f"  [{label}]: {list(sample[0]['props'].keys())}")
                    print(f"    Sample: {sample[0]['props']}")

            # 6. Sample relationships
            print("\n=== SAMPLE RELATIONSHIPS ===")
            sample_rels = session.run(
                "MATCH (a)-[r]->(b) RETURN labels(a) AS from_labels, type(r) AS rel_type, labels(b) AS to_labels, count(*) AS count "
                "ORDER BY count DESC"
            ).data()
            for r in sample_rels:
                print(f"  {r['from_labels']} -[:{r['rel_type']}]-> {r['to_labels']} (count: {r['count']})")

    except Exception as e:
        print(f"Error connecting or querying database: {e}", file=sys.stderr)
        return False
    finally:
        close_driver()
    return True

if __name__ == "__main__":
    introspect()
