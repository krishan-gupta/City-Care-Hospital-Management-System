from typing import Optional
from fastapi import APIRouter
from db import run_query
import schema_map as sm

router = APIRouter(tags=["Doctors & Departments"])

@router.get("/doctors")
def list_doctors(
    department: Optional[str] = None,
    type: Optional[str] = None
):
    cypher = f"""
    MATCH (d:{sm.LABEL_DOCTOR})
    OPTIONAL MATCH (d)-[:{sm.REL_BELONGS_TO}]->(dep:{sm.LABEL_DEPARTMENT})
    WITH d, dep
    WHERE ($dept IS NULL OR dep.name = $dept OR dep.{sm.KEY_DEPARTMENT} = $dept)
    OPTIONAL MATCH (d)-[:{sm.REL_ASSIGNED_TO}]->(:{sm.LABEL_APPOINTMENT})<-[:{sm.REL_HAS_APPOINTMENT}]-(p:{sm.LABEL_PATIENT})
    RETURN d.{sm.KEY_DOCTOR} AS empId,
           coalesce(d.name, d.firstName + ' ' + d.lastName) AS name,
           d.firstName AS firstName,
           d.lastName AS lastName,
           toString(coalesce(d.phoneNumber, d.phone)) AS phone,
           d.email AS email,
           coalesce(d.specialization, d.specialty) AS specialization,
           d.yearsExperience AS experience,
           d.hospitalBranch AS hospitalBranch,
           dep.{sm.KEY_DEPARTMENT} AS deptId,
           dep.name AS department,
           count(DISTINCT p) AS patientCount
    ORDER BY d.{sm.KEY_DOCTOR} ASC
    """
    records = run_query(cypher, {"dept": department})
    return records


@router.get("/departments")
def list_departments():
    cypher = f"""
    MATCH (dep:{sm.LABEL_DEPARTMENT})
    WHERE dep.name IS NOT NULL
    OPTIONAL MATCH (d:{sm.LABEL_DOCTOR})-[:{sm.REL_BELONGS_TO}]->(dep)
    RETURN dep.{sm.KEY_DEPARTMENT} AS deptId,
           dep.name AS name,
           dep.floor AS floor,
           count(d) AS doctorCount
    ORDER BY dep.name ASC
    """
    return run_query(cypher)
