from typing import Optional
from fastapi import APIRouter, HTTPException
from db import run_query
from models import LabTestUpdate
import schema_map as sm

router = APIRouter(prefix="/labtests", tags=["Lab Tests"])

@router.get("")
def list_lab_tests(status: Optional[str] = None):
    cypher = f"""
    MATCH (lt:{sm.LABEL_LAB_TEST})<-[:{sm.REL_HAS_LAB_TEST}]-(t:{sm.LABEL_TREATMENT})<-[:{sm.REL_HAS_TREATMENT}]-(a:{sm.LABEL_APPOINTMENT})<-[:{sm.REL_HAS_APPOINTMENT}]-(p:{sm.LABEL_PATIENT})
    OPTIONAL MATCH (d:{sm.LABEL_DOCTOR})-[:{sm.REL_ASSIGNED_TO}]->(a)
    WHERE ($status IS NULL OR lt.status = $status OR lt.resultStatus = $status)
    RETURN lt.{sm.KEY_LAB_TEST} AS testId,
           coalesce(lt.testType, t.treatmentType, 'Diagnostic Test') AS testType,
           toString(coalesce(lt.orderedDate, t.treatmentDate)) AS orderedDate,
           coalesce(lt.result, '') AS result,
           coalesce(lt.resultStatus, lt.status) AS resultStatus,
           coalesce(lt.charge, 350.0) AS charge,
           p.{sm.KEY_PATIENT} AS patientId,
           coalesce(p.name, p.firstName + ' ' + p.lastName) AS patientName,
           coalesce(d.name, d.firstName + ' ' + d.lastName) AS doctorName
    ORDER BY t.treatmentDate DESC
    """
    return run_query(cypher, {"status": status})


@router.put("/{test_id}")
def update_lab_test(test_id: str, data: LabTestUpdate):
    check = run_query(f"MATCH (lt:{sm.LABEL_LAB_TEST} {{{sm.KEY_LAB_TEST}: $id}}) RETURN lt", {"id": test_id})
    if not check:
        raise HTTPException(status_code=404, detail="Lab test not found")

    cypher = f"""
    MATCH (lt:{sm.LABEL_LAB_TEST} {{{sm.KEY_LAB_TEST}: $id}})
    SET lt.result = $result,
        lt.resultStatus = $status,
        lt.status = $status
    RETURN lt.{sm.KEY_LAB_TEST} AS testId,
           lt.testType AS testType,
           lt.result AS result,
           lt.resultStatus AS resultStatus,
           lt.status AS status
    """
    records = run_query(cypher, {
        "id": test_id,
        "result": data.result,
        "status": data.resultStatus
    })
    return records[0]
