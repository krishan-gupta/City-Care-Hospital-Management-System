import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from neo4j import GraphDatabase, Driver
from neo4j.time import Date, DateTime, Time

# Load environment variables from backend/.env regardless of CWD
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

_driver: Optional[Driver] = None


def get_driver() -> Driver:
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
    return _driver


def close_driver():
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None


def serialize_neo4j_value(val: Any) -> Any:
    """Convert Neo4j types (Nodes, Relationships, Dates, Integers) to JSON-serializable types."""
    if val is None:
        return None
    # Neo4j temporal types
    if isinstance(val, (Date, DateTime, Time)):
        return val.isoformat()
    # Check for neo4j Node
    if hasattr(val, "labels") and hasattr(val, "items"):
        node_dict = dict(val.items())
        node_dict["_labels"] = list(val.labels)
        node_dict["_element_id"] = getattr(val, "element_id", None)
        return {k: serialize_neo4j_value(v) for k, v in node_dict.items()}
    # Check for neo4j Relationship
    if hasattr(val, "type") and hasattr(val, "items") and hasattr(val, "start_node"):
        rel_dict = dict(val.items())
        rel_dict["_type"] = val.type
        rel_dict["_element_id"] = getattr(val, "element_id", None)
        return {k: serialize_neo4j_value(v) for k, v in rel_dict.items()}
    # Dictionaries
    if isinstance(val, dict):
        return {k: serialize_neo4j_value(v) for k, v in val.items()}
    # Lists / tuples
    if isinstance(val, (list, tuple, set)):
        return [serialize_neo4j_value(x) for x in val]
    return val


def run_query(cypher: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Execute a read-oriented or standard Cypher query and return serialized dictionaries."""
    driver = get_driver()
    with driver.session() as session:
        result = session.run(cypher, parameters or {})
        records = [serialize_neo4j_value(record.data()) for record in result]
        return records


def run_write_transaction(unit_of_work, *args, **kwargs):
    """Execute a multi-step write function inside a single transaction."""
    driver = get_driver()
    with driver.session() as session:
        return session.execute_write(unit_of_work, *args, **kwargs)
