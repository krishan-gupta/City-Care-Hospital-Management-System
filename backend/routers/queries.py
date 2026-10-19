from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from db import run_query
import schema_map as sm

router = APIRouter(prefix="/queries", tags=["Named Cypher Queries"])

QUERIES_DEF = {
    "patient_journey": {
        "name": "patient_journey",
        "title": "Patient Complete Journey",
        "description": "All linked data for one patient (appointment, doctor, consultation, treatment, prescription, lab test, bills, claims).",
        "requiresId": True,
        "paramName": "id",
        "cypher": f"""
MATCH (p:{sm.LABEL_PATIENT} {{{sm.KEY_PATIENT}: $id}})-[:{sm.REL_HAS_APPOINTMENT}]->(a:{sm.LABEL_APPOINTMENT})<-[:{sm.REL_ASSIGNED_TO}]-(d:{sm.LABEL_DOCTOR})-[:{sm.REL_BELONGS_TO}]->(dep:{sm.LABEL_DEPARTMENT})
OPTIONAL MATCH (a)-[:{sm.REL_HAS_CONSULTATION}]->(c:{sm.LABEL_CONSULTATION})
OPTIONAL MATCH (a)-[:{sm.REL_HAS_TREATMENT}]->(t:{sm.LABEL_TREATMENT})
OPTIONAL MATCH (t)-[:{sm.REL_HAS_PRESCRIPTION}]->(rx:{sm.LABEL_PRESCRIPTION})
OPTIONAL MATCH (t)-[:{sm.REL_HAS_LAB_TEST}]->(lt:{sm.LABEL_LAB_TEST})
OPTIONAL MATCH (p)-[:{sm.REL_HAS_BILL}]->(b:{sm.LABEL_BILL})
OPTIONAL MATCH (b)-[:{sm.REL_HAS_CLAIM}]->(cl:{sm.LABEL_INSURANCE_CLAIM})
RETURN coalesce(p.name, p.firstName + ' ' + p.lastName) AS patient,
       toString(a.appointmentDate) AS appointmentDate,
       a.status AS appointmentStatus,
       coalesce(d.name, d.firstName + ' ' + d.lastName) AS doctor,
       dep.name AS department,
       coalesce(c.reason, c.diagnosis, 'General Consultation') AS diagnosis,
       coalesce(rx.treatmentType, 'Medication') AS prescription,
       coalesce(lt.testType, 'Lab Test') AS labTest,
       coalesce(lt.status, 'Pending') AS testStatus,
       round(b.amount, 2) AS billTotal,
       round(coalesce(cl.claimAmount, 0), 2) AS claimAmount;
        """
    },
    "appointments_overview": {
        "name": "appointments_overview",
        "title": "Appointments Overview",
        "description": "Patient, doctor, department, date, and status sorted by most recent date.",
        "requiresId": False,
        "cypher": f"""
MATCH (p:{sm.LABEL_PATIENT})-[:{sm.REL_HAS_APPOINTMENT}]->(a:{sm.LABEL_APPOINTMENT})<-[:{sm.REL_ASSIGNED_TO}]-(d:{sm.LABEL_DOCTOR})-[:{sm.REL_BELONGS_TO}]->(dep:{sm.LABEL_DEPARTMENT})
RETURN coalesce(p.name, p.firstName + ' ' + p.lastName) AS patient,
       coalesce(d.name, d.firstName + ' ' + d.lastName) AS doctor,
       dep.name AS department,
       toString(a.appointmentDate) AS date,
       a.status AS status
ORDER BY a.appointmentDate DESC;
        """
    },
    "consultations_with_prescriptions": {
        "name": "consultations_with_prescriptions",
        "title": "Consultations with Prescriptions",
        "description": "Patient consultation diagnoses and list of all prescribed treatments.",
        "requiresId": False,
        "cypher": f"""
MATCH (p:{sm.LABEL_PATIENT})-[:{sm.REL_HAS_APPOINTMENT}]->(a:{sm.LABEL_APPOINTMENT})-[:{sm.REL_HAS_CONSULTATION}]->(c:{sm.LABEL_CONSULTATION})
OPTIONAL MATCH (a)-[:{sm.REL_HAS_TREATMENT}]->(t:{sm.LABEL_TREATMENT})-[:{sm.REL_HAS_PRESCRIPTION}]->(rx:{sm.LABEL_PRESCRIPTION})
RETURN coalesce(p.name, p.firstName + ' ' + p.lastName) AS patient,
       toString(c.consultationDate) AS consultationDate,
       coalesce(c.reason, c.diagnosis, 'Consultation') AS diagnosis,
       collect(coalesce(rx.treatmentType, 'Medication') + ' (' + rx.status + ')') AS prescription;
        """
    },
    "patients_per_doctor": {
        "name": "patients_per_doctor",
        "title": "Patients per Doctor",
        "description": "Number of distinct patients treated by each doctor, ordered from highest to lowest.",
        "requiresId": False,
        "cypher": f"""
MATCH (d:{sm.LABEL_DOCTOR})-[:{sm.REL_ASSIGNED_TO}]->(a:{sm.LABEL_APPOINTMENT})<-[:{sm.REL_HAS_APPOINTMENT}]-(p:{sm.LABEL_PATIENT})
RETURN coalesce(d.name, d.firstName + ' ' + d.lastName) AS doctor, count(DISTINCT p) AS patients
ORDER BY patients DESC;
        """
    },
    "departments_more_than_two_doctors": {
        "name": "departments_more_than_two_doctors",
        "title": "Departments with More Than 2 Doctors",
        "description": "Filtered list of departments employing more than 2 doctors.",
        "requiresId": False,
        "cypher": f"""
MATCH (d:{sm.LABEL_DOCTOR})-[:{sm.REL_BELONGS_TO}]->(dep:{sm.LABEL_DEPARTMENT})
WITH dep, count(d) AS doctors
WHERE doctors > 2
RETURN dep.name AS department, doctors;
        """
    },
    "bill_statistics": {
        "name": "bill_statistics",
        "title": "Bill Amount Statistics",
        "description": "Overall total revenue, average bill, highest bill, and lowest bill.",
        "requiresId": False,
        "cypher": f"""
MATCH (b:{sm.LABEL_BILL})
RETURN round(sum(b.amount), 2) AS total,
       round(avg(b.amount), 2) AS average,
       round(max(b.amount), 2) AS highest,
       round(min(b.amount), 2) AS lowest;
        """
    },
    "doctors_above_average_patients": {
        "name": "doctors_above_average_patients",
        "title": "Doctors Above Average Patients (Nested)",
        "description": "Identifies doctors who have treated more unique patients than the overall doctor average.",
        "requiresId": False,
        "cypher": f"""
MATCH (d:{sm.LABEL_DOCTOR})-[:{sm.REL_ASSIGNED_TO}]->(:{sm.LABEL_APPOINTMENT})<-[:{sm.REL_HAS_APPOINTMENT}]-(p:{sm.LABEL_PATIENT})
WITH d, count(DISTINCT p) AS cnt
WITH collect({{doctor: coalesce(d.name, d.firstName + ' ' + d.lastName), cnt: cnt}}) AS rows, avg(cnt) AS avgCnt
UNWIND rows AS r
WITH r WHERE r.cnt > avgCnt
RETURN r.doctor AS doctor, r.cnt AS patients
ORDER BY patients DESC;
        """
    },
    "patients_bill_above_average": {
        "name": "patients_bill_above_average",
        "title": "Patients Bill Above Average (Nested)",
        "description": "Finds patients whose cumulative billing exceeds the overall average patient billing.",
        "requiresId": False,
        "cypher": f"""
MATCH (p:{sm.LABEL_PATIENT})-[:{sm.REL_HAS_BILL}]->(b:{sm.LABEL_BILL})
WITH p, sum(b.amount) AS total
WITH collect({{patient: coalesce(p.name, p.firstName + ' ' + p.lastName), total: total}}) AS rows, avg(total) AS avgTotal
UNWIND rows AS r
WITH r WHERE r.total > avgTotal
RETURN r.patient AS patient, round(r.total, 2) AS totalBill
ORDER BY totalBill DESC;
        """
    },
    "doctors_above_department_average": {
        "name": "doctors_above_department_average",
        "title": "Doctors Above Department Average (Correlated)",
        "description": "Doctors serving more patients than their specific department's average workload.",
        "requiresId": False,
        "cypher": f"""
MATCH (d:{sm.LABEL_DOCTOR})-[:{sm.REL_BELONGS_TO}]->(dep:{sm.LABEL_DEPARTMENT})
CALL (d) {{
  MATCH (d)-[:{sm.REL_ASSIGNED_TO}]->(:{sm.LABEL_APPOINTMENT})<-[:{sm.REL_HAS_APPOINTMENT}]-(p:{sm.LABEL_PATIENT})
  RETURN count(DISTINCT p) AS cnt
}}
WITH dep, d, cnt
WITH dep, collect({{doctor: coalesce(d.name, d.firstName + ' ' + d.lastName), cnt: cnt}}) AS rows, avg(cnt) AS avgCnt
UNWIND rows AS r
WITH dep, r, avgCnt WHERE r.cnt > avgCnt
RETURN dep.name AS department, r.doctor AS doctor, r.cnt AS patients;
        """
    },
    "patients_with_abnormal_lab": {
        "name": "patients_with_abnormal_lab",
        "title": "Patients with Abnormal Lab Test (Correlated)",
        "description": "Patients who have had at least one test resulting in 'Abnormal' (EXISTS subquery).",
        "requiresId": False,
        "cypher": f"""
MATCH (p:{sm.LABEL_PATIENT})
WHERE EXISTS {{
  MATCH (p)-[:{sm.REL_HAS_APPOINTMENT}]->(:{sm.LABEL_APPOINTMENT})-[:{sm.REL_HAS_TREATMENT}]->(:{sm.LABEL_TREATMENT})-[:{sm.REL_HAS_LAB_TEST}]->(t:{sm.LABEL_LAB_TEST})
  WHERE t.status = 'Abnormal' OR t.resultStatus = 'Abnormal'
}}
RETURN coalesce(p.name, p.firstName + ' ' + p.lastName) AS patient;
        """
    },
    "patient_billing_report": {
        "name": "patient_billing_report",
        "title": "Patient Billing Report",
        "description": "Complete breakdown of total bill, claimed insurance, approved insurance, and patient payable.",
        "requiresId": False,
        "cypher": f"""
MATCH (p:{sm.LABEL_PATIENT})-[:{sm.REL_HAS_BILL}]->(b:{sm.LABEL_BILL})
OPTIONAL MATCH (b)-[:{sm.REL_HAS_CLAIM}]->(cl:{sm.LABEL_INSURANCE_CLAIM})
RETURN coalesce(p.name, p.firstName + ' ' + p.lastName) AS patient,
       round(b.amount, 2) AS totalBill,
       coalesce(round(cl.claimAmount, 2), 0) AS claimAmount,
       coalesce(round(cl.approvedAmount, 2), 0) AS approvedAmount,
       round(b.amount - coalesce(cl.approvedAmount, 0), 2) AS patientPayable
ORDER BY totalBill DESC;
        """
    }
}

@router.get("")
def list_queries():
    return [
        {
            "name": k,
            "title": v["title"],
            "description": v["description"],
            "requiresId": v.get("requiresId", False),
            "paramName": v.get("paramName"),
            "cypher": v["cypher"].strip()
        }
        for k, v in QUERIES_DEF.items()
    ]


@router.get("/{name}")
def run_named_query(name: str, id: Optional[str] = Query(None)):
    if name not in QUERIES_DEF:
        raise HTTPException(status_code=404, detail=f"Query '{name}' not found")

    query_meta = QUERIES_DEF[name]
    params = {}
    if query_meta.get("requiresId"):
        if not id:
            raise HTTPException(status_code=400, detail=f"Query '{name}' requires an 'id' query parameter")
        params["id"] = id

    cypher = query_meta["cypher"]
    results = run_query(cypher, params)
    return {
        "name": name,
        "title": query_meta["title"],
        "description": query_meta["description"],
        "cypher": cypher.strip(),
        "rowCount": len(results),
        "data": results
    }
