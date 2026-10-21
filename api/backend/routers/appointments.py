import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from db import run_query
from models import AppointmentCreate, AppointmentUpdate
import schema_map as sm

router = APIRouter(prefix="/appointments", tags=["Appointments"])

def gen_id(prefix: str = "A") -> str:
    return f"{prefix}{uuid.uuid4().hex[:5].upper()}"

@router.get("")
def list_appointments(
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    doctor: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    patient: Optional[str] = None
):
    cypher = f"""
    MATCH (p:{sm.LABEL_PATIENT})-[:{sm.REL_HAS_APPOINTMENT}]->(a:{sm.LABEL_APPOINTMENT})<-[:{sm.REL_ASSIGNED_TO}]-(d:{sm.LABEL_DOCTOR})
    OPTIONAL MATCH (d)-[:{sm.REL_BELONGS_TO}]->(dep:{sm.LABEL_DEPARTMENT})
    OPTIONAL MATCH (a)-[:{sm.REL_HAS_CONSULTATION}]->(c:{sm.LABEL_CONSULTATION})
    WHERE ($from IS NULL OR toString(a.appointmentDate) >= $from)
      AND ($to IS NULL OR toString(a.appointmentDate) <= $to)
      AND ($status IS NULL OR a.status = $status)
      AND ($doctor IS NULL OR (d.firstName + ' ' + d.lastName) =~ $doc_pattern OR d.{sm.KEY_DOCTOR} = $doctor)
      AND ($dept IS NULL OR dep.name = $dept OR dep.{sm.KEY_DEPARTMENT} = $dept)
      AND ($patient IS NULL OR (p.firstName + ' ' + p.lastName) =~ $pat_pattern OR p.{sm.KEY_PATIENT} = $patient)
    RETURN a.{sm.KEY_APPOINTMENT} AS apptId,
           toString(a.appointmentDate) AS date,
           a.appointmentTime AS time,
           a.status AS status,
           a.reasonForVisit AS reason,
           p.{sm.KEY_PATIENT} AS patientId,
           coalesce(p.name, p.firstName + ' ' + p.lastName) AS patientName,
           toString(coalesce(p.contactNumber, p.phone)) AS patientPhone,
           d.{sm.KEY_DOCTOR} AS doctorId,
           coalesce(d.name, d.firstName + ' ' + d.lastName) AS doctorName,
           d.specialization AS doctorSpecialization,
           dep.{sm.KEY_DEPARTMENT} AS deptId,
           dep.name AS departmentName,
           c.{sm.KEY_CONSULTATION} AS consultationId
    ORDER BY a.appointmentDate DESC
    """
    params = {
        "from": from_date,
        "to": to_date,
        "status": status,
        "doctor": doctor,
        "doc_pattern": f"(?i).*{doctor}.*" if doctor else ".*",
        "dept": department,
        "patient": patient,
        "pat_pattern": f"(?i).*{patient}.*" if patient else ".*"
    }
    return run_query(cypher, params)


@router.post("", status_code=201)
def create_appointment(data: AppointmentCreate):
    check_patient = run_query(f"MATCH (p:{sm.LABEL_PATIENT} {{{sm.KEY_PATIENT}: $id}}) RETURN p", {"id": data.patientId})
    if not check_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    check_doc = run_query(f"MATCH (d:{sm.LABEL_DOCTOR} {{{sm.KEY_DOCTOR}: $id}}) RETURN d", {"id": data.doctorId})
    if not check_doc:
        raise HTTPException(status_code=404, detail="Doctor not found")

    appt_id = gen_id("A")
    cypher = f"""
    MATCH (p:{sm.LABEL_PATIENT} {{{sm.KEY_PATIENT}: $patient_id}})
    MATCH (d:{sm.LABEL_DOCTOR} {{{sm.KEY_DOCTOR}: $doctor_id}})
    CREATE (a:{sm.LABEL_APPOINTMENT} {{
        {sm.KEY_APPOINTMENT}: $appt_id,
        appointmentDate: $date,
        date: $date,
        appointmentTime: $time,
        time: $time,
        status: 'Scheduled',
        reasonForVisit: 'General Consultation',
        patientId: $patient_id,
        doctorId: $doctor_id
    }})
    CREATE (p)-[:{sm.REL_HAS_APPOINTMENT}]->(a)
    CREATE (d)-[:{sm.REL_ASSIGNED_TO}]->(a)
    RETURN a.{sm.KEY_APPOINTMENT} AS apptId
    """
    run_query(cypher, {
        "patient_id": data.patientId,
        "doctor_id": data.doctorId,
        "appt_id": appt_id,
        "date": data.date,
        "time": data.time
    })

    records = list_appointments(patient=data.patientId)
    created = [r for r in records if r["apptId"] == appt_id]
    return created[0] if created else {"apptId": appt_id, "status": "Scheduled"}


@router.put("/{appt_id}")
def update_appointment(appt_id: str, data: AppointmentUpdate):
    check = run_query(f"MATCH (a:{sm.LABEL_APPOINTMENT} {{{sm.KEY_APPOINTMENT}: $id}}) RETURN a", {"id": appt_id})
    if not check:
        raise HTTPException(status_code=404, detail="Appointment not found")

    updates = []
    params = {"appt_id": appt_id}
    if data.date is not None:
        updates.extend(["a.appointmentDate = $date", "a.date = $date"])
        params["date"] = data.date
    if data.time is not None:
        updates.extend(["a.appointmentTime = $time", "a.time = $time"])
        params["time"] = data.time
    if data.status is not None:
        updates.append("a.status = $status")
        params["status"] = data.status

    if updates:
        cypher = f"""
        MATCH (a:{sm.LABEL_APPOINTMENT} {{{sm.KEY_APPOINTMENT}: $appt_id}})
        SET {", ".join(updates)}
        RETURN a.{sm.KEY_APPOINTMENT} AS apptId
        """
        run_query(cypher, params)

    records = run_query(f"""
        MATCH (p:{sm.LABEL_PATIENT})-[:{sm.REL_HAS_APPOINTMENT}]->(a:{sm.LABEL_APPOINTMENT} {{{sm.KEY_APPOINTMENT}: $id}})<-[:{sm.REL_ASSIGNED_TO}]-(d:{sm.LABEL_DOCTOR})
        OPTIONAL MATCH (d)-[:{sm.REL_BELONGS_TO}]->(dep:{sm.LABEL_DEPARTMENT})
        RETURN a.{sm.KEY_APPOINTMENT} AS apptId, toString(a.appointmentDate) AS date, a.appointmentTime AS time, a.status AS status,
               coalesce(p.name, p.firstName + ' ' + p.lastName) AS patientName,
               coalesce(d.name, d.firstName + ' ' + d.lastName) AS doctorName,
               dep.name AS departmentName
    """, {"id": appt_id})
    return records[0] if records else {"apptId": appt_id}


@router.delete("/{appt_id}")
def delete_appointment(appt_id: str):
    check = run_query(f"MATCH (a:{sm.LABEL_APPOINTMENT} {{{sm.KEY_APPOINTMENT}: $id}}) RETURN a", {"id": appt_id})
    if not check:
        raise HTTPException(status_code=404, detail="Appointment not found")

    cypher = f"""
    MATCH (a:{sm.LABEL_APPOINTMENT} {{{sm.KEY_APPOINTMENT}: $id}})
    OPTIONAL MATCH (a)-[:{sm.REL_HAS_CONSULTATION}]->(c:{sm.LABEL_CONSULTATION})
    OPTIONAL MATCH (a)-[:{sm.REL_HAS_TREATMENT}]->(t:{sm.LABEL_TREATMENT})
    OPTIONAL MATCH (t)-[:{sm.REL_HAS_PRESCRIPTION}]->(rx:{sm.LABEL_PRESCRIPTION})
    OPTIONAL MATCH (t)-[:{sm.REL_HAS_LAB_TEST}]->(lt:{sm.LABEL_LAB_TEST})
    OPTIONAL MATCH (t)-[:{sm.REL_HAS_BILL}]->(b:{sm.LABEL_BILL})
    OPTIONAL MATCH (b)-[:{sm.REL_HAS_CLAIM}]->(cl:{sm.LABEL_INSURANCE_CLAIM})
    DETACH DELETE cl, b, lt, rx, t, c, a
    """
    run_query(cypher, {"id": appt_id})
    return {"status": "success", "message": f"Appointment {appt_id} and related consultation records deleted."}
