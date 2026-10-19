import uuid
from datetime import date
from typing import Optional
from fastapi import APIRouter, HTTPException
from db import run_query, run_write_transaction
from models import ConsultationCreate
import schema_map as sm

router = APIRouter(prefix="/consultations", tags=["Consultations"])

def gen_id(prefix: str = "CA") -> str:
    return f"{prefix}{uuid.uuid4().hex[:4].upper()}"

@router.get("")
def list_consultations(appointment_id: Optional[str] = None):
    cypher = f"""
    MATCH (a:{sm.LABEL_APPOINTMENT})-[:{sm.REL_HAS_CONSULTATION}]->(c:{sm.LABEL_CONSULTATION})
    OPTIONAL MATCH (p:{sm.LABEL_PATIENT})-[:{sm.REL_HAS_APPOINTMENT}]->(a)
    OPTIONAL MATCH (d:{sm.LABEL_DOCTOR})-[:{sm.REL_ASSIGNED_TO}]->(a)
    OPTIONAL MATCH (a)-[:{sm.REL_HAS_TREATMENT}]->(t:{sm.LABEL_TREATMENT})
    OPTIONAL MATCH (t)-[:{sm.REL_HAS_PRESCRIPTION}]->(rx:{sm.LABEL_PRESCRIPTION})
    OPTIONAL MATCH (t)-[:{sm.REL_HAS_LAB_TEST}]->(lt:{sm.LABEL_LAB_TEST})
    WHERE ($appt_id IS NULL OR a.{sm.KEY_APPOINTMENT} = $appt_id)
    RETURN c.{sm.KEY_CONSULTATION} AS consultId,
           toString(c.consultationDate) AS date,
           coalesce(c.reason, c.diagnosis, 'General checkup') AS diagnosis,
           c.status AS status,
           a.{sm.KEY_APPOINTMENT} AS appointmentId,
           p.{sm.KEY_PATIENT} AS patientId,
           coalesce(p.name, p.firstName + ' ' + p.lastName) AS patientName,
           d.{sm.KEY_DOCTOR} AS doctorId,
           coalesce(d.name, d.firstName + ' ' + d.lastName) AS doctorName,
           collect(DISTINCT {{
               rxId: rx.{sm.KEY_PRESCRIPTION},
               treatmentType: rx.treatmentType,
               status: rx.status
           }}) AS prescriptions,
           collect(DISTINCT {{
               testId: lt.{sm.KEY_LAB_TEST},
               testType: lt.testType,
               status: lt.status
           }}) AS labTests
    ORDER BY c.consultationDate DESC
    """
    return run_query(cypher, {"appt_id": appointment_id})


@router.get("/medicines")
def list_medicines():
    """Helper to populate sample medicines for frontend selection."""
    return [
        {"medId": "MED01", "name": "Amoxicillin 500mg", "unitPrice": 12.50},
        {"medId": "MED02", "name": "Ibuprofen 400mg", "unitPrice": 8.00},
        {"medId": "MED03", "name": "Atorvastatin 20mg", "unitPrice": 25.00},
        {"medId": "MED04", "name": "Metformin 500mg", "unitPrice": 10.00},
        {"medId": "MED05", "name": "Lisinopril 10mg", "unitPrice": 15.00},
        {"medId": "MED06", "name": "Omeprazole 20mg", "unitPrice": 18.00},
        {"medId": "MED07", "name": "Paracetamol 650mg", "unitPrice": 5.00}
    ]


@router.get("/technicians")
def list_technicians():
    """Helper to populate technicians for lab test assignment."""
    return [
        {"empId": "TECH01", "name": "Robert Miller", "labSection": "Hematology"},
        {"empId": "TECH02", "name": "Sarah Connor", "labSection": "Biochemistry"},
        {"empId": "TECH03", "name": "David Clark", "labSection": "Radiology"},
        {"empId": "TECH04", "name": "Lisa Wang", "labSection": "Pathology"}
    ]


@router.get("/{consult_id}")
def get_consultation(consult_id: str):
    cypher = f"""
    MATCH (c:{sm.LABEL_CONSULTATION} {{{sm.KEY_CONSULTATION}: $id}})<-[:{sm.REL_HAS_CONSULTATION}]-(a:{sm.LABEL_APPOINTMENT})
    OPTIONAL MATCH (p:{sm.LABEL_PATIENT})-[:{sm.REL_HAS_APPOINTMENT}]->(a)
    OPTIONAL MATCH (d:{sm.LABEL_DOCTOR})-[:{sm.REL_ASSIGNED_TO}]->(a)
    OPTIONAL MATCH (a)-[:{sm.REL_HAS_TREATMENT}]->(t:{sm.LABEL_TREATMENT})
    OPTIONAL MATCH (t)-[:{sm.REL_HAS_PRESCRIPTION}]->(rx:{sm.LABEL_PRESCRIPTION})
    OPTIONAL MATCH (t)-[:{sm.REL_HAS_LAB_TEST}]->(lt:{sm.LABEL_LAB_TEST})
    RETURN c.{sm.KEY_CONSULTATION} AS consultId,
           toString(c.consultationDate) AS date,
           coalesce(c.reason, c.diagnosis, 'General checkup') AS diagnosis,
           c.status AS status,
           a.{sm.KEY_APPOINTMENT} AS appointmentId,
           p.{sm.KEY_PATIENT} AS patientId,
           coalesce(p.name, p.firstName + ' ' + p.lastName) AS patientName,
           d.{sm.KEY_DOCTOR} AS doctorId,
           coalesce(d.name, d.firstName + ' ' + d.lastName) AS doctorName,
           collect(DISTINCT {{
               rxId: rx.{sm.KEY_PRESCRIPTION},
               treatmentType: rx.treatmentType,
               status: rx.status
           }}) AS prescriptions,
           collect(DISTINCT {{
               testId: lt.{sm.KEY_LAB_TEST},
               testType: lt.testType,
               status: lt.status
           }}) AS labTests
    """
    records = run_query(cypher, {"id": consult_id})
    if not records:
        raise HTTPException(status_code=404, detail="Consultation not found")
    return records[0]


@router.post("", status_code=201)
def create_consultation(data: ConsultationCreate):
    check_appt = run_query(
        f"MATCH (a:{sm.LABEL_APPOINTMENT} {{{sm.KEY_APPOINTMENT}: $id}}) RETURN a",
        {"id": data.appointmentId}
    )
    if not check_appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    consult_id = gen_id("CA")
    treatment_id = gen_id("T")
    today_str = str(date.today())

    def _transaction_work(tx):
        # 1. Update appointment to Completed and create Consultation
        c_query = f"""
        MATCH (a:{sm.LABEL_APPOINTMENT} {{{sm.KEY_APPOINTMENT}: $appt_id}})
        SET a.status = 'Completed'
        CREATE (c:{sm.LABEL_CONSULTATION} {{
            {sm.KEY_CONSULTATION}: $consult_id,
            consultationDate: $date,
            reason: $diagnosis,
            diagnosis: $diagnosis,
            notes: $notes,
            status: 'Completed',
            dataType: 'clinical'
        }})
        CREATE (a)-[:{sm.REL_HAS_CONSULTATION}]->(c)
        RETURN c.{sm.KEY_CONSULTATION} AS consultId
        """
        tx.run(c_query, {
            "appt_id": data.appointmentId,
            "consult_id": consult_id,
            "date": today_str,
            "diagnosis": data.diagnosis,
            "notes": data.notes or ""
        })

        # 2. Create Treatment node
        t_query = f"""
        MATCH (a:{sm.LABEL_APPOINTMENT} {{{sm.KEY_APPOINTMENT}: $appt_id}})
        CREATE (t:{sm.LABEL_TREATMENT} {{
            {sm.KEY_TREATMENT}: $treatment_id,
            treatmentDate: $date,
            treatmentType: $diagnosis,
            cost: $cost,
            description: $notes,
            appointmentId: $appt_id
        }})
        CREATE (a)-[:{sm.REL_HAS_TREATMENT}]->(t)
        """
        total_lab_charge = sum(lt.charge for lt in (data.labTests or []))
        tx.run(t_query, {
            "appt_id": data.appointmentId,
            "treatment_id": treatment_id,
            "date": today_str,
            "diagnosis": data.diagnosis,
            "notes": data.notes or "Post-consultation therapy",
            "cost": 500.0 + total_lab_charge
        })

        # 3. Add Prescriptions
        if data.medicines:
            for med in data.medicines:
                rx_id = gen_id("RX")
                rx_query = f"""
                MATCH (t:{sm.LABEL_TREATMENT} {{{sm.KEY_TREATMENT}: $treatment_id}})
                CREATE (rx:{sm.LABEL_PRESCRIPTION} {{
                    {sm.KEY_PRESCRIPTION}: $rx_id,
                    treatmentType: $treatment_type,
                    dosage: $dosage,
                    durationDays: $duration,
                    status: 'Active',
                    dataType: 'clinical'
                }})
                CREATE (t)-[:{sm.REL_HAS_PRESCRIPTION}]->(rx)
                """
                tx.run(rx_query, {
                    "treatment_id": treatment_id,
                    "rx_id": rx_id,
                    "treatment_type": f"{med.medId} - {med.dosage}",
                    "dosage": med.dosage,
                    "duration": med.durationDays
                })

        # 4. Add Lab Tests
        if data.labTests:
            for item in data.labTests:
                test_id = gen_id("LAB")
                test_query = f"""
                MATCH (t:{sm.LABEL_TREATMENT} {{{sm.KEY_TREATMENT}: $treatment_id}})
                CREATE (lt:{sm.LABEL_LAB_TEST} {{
                    {sm.KEY_LAB_TEST}: $test_id,
                    testType: $test_type,
                    orderedDate: $date,
                    result: '',
                    resultStatus: 'Pending',
                    status: 'Pending',
                    charge: $charge,
                    dataType: 'clinical'
                }})
                CREATE (t)-[:{sm.REL_HAS_LAB_TEST}]->(lt)
                """
                tx.run(test_query, {
                    "treatment_id": treatment_id,
                    "test_id": test_id,
                    "test_type": item.testType,
                    "date": today_str,
                    "charge": item.charge
                })

        return consult_id

    run_write_transaction(_transaction_work)
    return get_consultation(consult_id)
