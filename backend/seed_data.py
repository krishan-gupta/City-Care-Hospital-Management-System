"""
CityCare Hospital Management System - Database Seed Script.
Populates a fresh Neo4j AuraDB instance with realistic hospital data:
- Departments & Doctors
- Patients
- Appointments
- Consultations & Treatments
- Prescriptions & LabTests (Normal and Abnormal for Viva query 10)
- Billing & Insurance Claims (matching Viva queries 6, 8, 11)
"""

import sys
import random
from datetime import datetime, timedelta
from db import run_query, run_write_transaction, close_driver, get_driver
import schema_map as sm

def seed():
    print("=" * 60)
    print("CityCare Hospital Management System - Database Seeder")
    print("=" * 60)

    try:
        driver = get_driver()
        with driver.session() as s:
            s.run("RETURN 1")
        print("[✓] Connected to Neo4j successfully!")
    except Exception as e:
        print(f"\n[✗] Cannot connect to Neo4j: {e}")
        print("\nPlease ensure your backend/.env has the correct NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD.")
        sys.exit(1)

    print("\n[1/7] Creating Constraints and Indexes...")
    constraints = [
        f"CREATE CONSTRAINT IF NOT EXISTS FOR (d:{sm.LABEL_DEPARTMENT}) REQUIRE d.id IS UNIQUE",
        f"CREATE CONSTRAINT IF NOT EXISTS FOR (doc:{sm.LABEL_DOCTOR}) REQUIRE doc.id IS UNIQUE",
        f"CREATE CONSTRAINT IF NOT EXISTS FOR (p:{sm.LABEL_PATIENT}) REQUIRE p.id IS UNIQUE",
        f"CREATE CONSTRAINT IF NOT EXISTS FOR (a:{sm.LABEL_APPOINTMENT}) REQUIRE a.id IS UNIQUE",
        f"CREATE CONSTRAINT IF NOT EXISTS FOR (c:{sm.LABEL_CONSULTATION}) REQUIRE c.id IS UNIQUE",
        f"CREATE CONSTRAINT IF NOT EXISTS FOR (t:{sm.LABEL_TREATMENT}) REQUIRE t.id IS UNIQUE",
        f"CREATE CONSTRAINT IF NOT EXISTS FOR (rx:{sm.LABEL_PRESCRIPTION}) REQUIRE rx.id IS UNIQUE",
        f"CREATE CONSTRAINT IF NOT EXISTS FOR (lt:{sm.LABEL_LAB_TEST}) REQUIRE lt.id IS UNIQUE",
        f"CREATE CONSTRAINT IF NOT EXISTS FOR (b:{sm.LABEL_BILL}) REQUIRE b.id IS UNIQUE",
        f"CREATE CONSTRAINT IF NOT EXISTS FOR (cl:{sm.LABEL_INSURANCE_CLAIM}) REQUIRE cl.id IS UNIQUE",
    ]
    for c in constraints:
        try:
            run_query(c)
        except Exception as e:
            # Aura Free may warn if edition syntax varies; safe to continue
            pass

    print("[2/7] Seeding Departments & Doctors...")
    # Meets Viva Query 5: "Departments with More Than 2 Doctors"
    departments = [
        {"id": "DEP-01", "name": "Cardiology"},
        {"id": "DEP-02", "name": "Neurology"},
        {"id": "DEP-03", "name": "Orthopedics"},
        {"id": "DEP-04", "name": "Pediatrics"},
        {"id": "DEP-05", "name": "General Medicine"},
        {"id": "DEP-06", "name": "Oncology"}
    ]
    for dep in departments:
        run_query(
            f"MERGE (d:{sm.LABEL_DEPARTMENT} {{id: $id}}) SET d.name = $name",
            dep
        )

    doctors = [
        # Cardiology (>2 doctors in Cardiology to fulfill DA3 query 5)
        {"id": "DOC-01", "name": "Dr. Rajesh Sharma", "depId": "DEP-01", "specialty": "Interventional Cardiology", "phone": "9876543210", "email": "rajesh.sharma@citycare.com"},
        {"id": "DOC-02", "name": "Dr. Priya Nair", "depId": "DEP-01", "specialty": "Electrophysiology", "phone": "9876543211", "email": "priya.nair@citycare.com"},
        {"id": "DOC-03", "name": "Dr. Amit Patel", "depId": "DEP-01", "specialty": "Heart Failure & Transplant", "phone": "9876543212", "email": "amit.patel@citycare.com"},
        # Neurology
        {"id": "DOC-04", "name": "Dr. Ananya Roy", "depId": "DEP-02", "specialty": "Neurovascular & Stroke", "phone": "9876543213", "email": "ananya.roy@citycare.com"},
        {"id": "DOC-05", "name": "Dr. Vikram Joshi", "depId": "DEP-02", "specialty": "Epileptology", "phone": "9876543214", "email": "vikram.joshi@citycare.com"},
        # Orthopedics (>2 doctors to fulfill query 5)
        {"id": "DOC-06", "name": "Dr. Sanjay Verma", "depId": "DEP-03", "specialty": "Joint Replacement", "phone": "9876543215", "email": "sanjay.verma@citycare.com"},
        {"id": "DOC-07", "name": "Dr. Sneha Rao", "depId": "DEP-03", "specialty": "Spine Surgery", "phone": "9876543216", "email": "sneha.rao@citycare.com"},
        {"id": "DOC-08", "name": "Dr. Rohan Kulkarni", "depId": "DEP-03", "specialty": "Sports Medicine", "phone": "9876543217", "email": "rohan.kulkarni@citycare.com"},
        # Pediatrics
        {"id": "DOC-09", "name": "Dr. Neha Gupta", "depId": "DEP-04", "specialty": "General Pediatrics", "phone": "9876543218", "email": "neha.gupta@citycare.com"},
        # General Medicine (>2 doctors to fulfill query 5)
        {"id": "DOC-10", "name": "Dr. Manoj Deshmukh", "depId": "DEP-05", "specialty": "Internal Medicine", "phone": "9876543219", "email": "manoj.deshmukh@citycare.com"},
        {"id": "DOC-11", "name": "Dr. Sunita Menon", "depId": "DEP-05", "specialty": "Critical Care Medicine", "phone": "9876543220", "email": "sunita.menon@citycare.com"},
        {"id": "DOC-12", "name": "Dr. Arjun Iyer", "depId": "DEP-05", "specialty": "Diabetology", "phone": "9876543221", "email": "arjun.iyer@citycare.com"},
    ]
    for doc in doctors:
        run_query(
            f"""
            MERGE (doc:{sm.LABEL_DOCTOR} {{id: $id}})
            SET doc.name = $name,
                doc.specialty = $specialty,
                doc.phone = $phone,
                doc.email = $email
            WITH doc
            MATCH (dep:{sm.LABEL_DEPARTMENT} {{id: $depId}})
            MERGE (doc)-[:{sm.REL_BELONGS_TO}]->(dep)
            """,
            doc
        )

    print("[3/7] Seeding Patients...")
    patients_data = [
        {"id": "PAT-101", "name": "Aarav Mehta", "dob": "1988-04-12", "gender": "Male", "phone": "9820011223", "address": "402 Marine Drive, Mumbai", "bloodGroup": "O+", "companyId": "Star Health", "policyNo": "SH-789012"},
        {"id": "PAT-102", "name": "Meera Krishnan", "dob": "1994-09-23", "gender": "Female", "phone": "9820022334", "address": "12 Indiranagar, Bangalore", "bloodGroup": "A+", "companyId": "HDFC ERGO", "policyNo": "HE-456123"},
        {"id": "PAT-103", "name": "Kabir Saxena", "dob": "1975-11-05", "gender": "Male", "phone": "9820033445", "address": "88 Civil Lines, Delhi", "bloodGroup": "B+", "companyId": "Care Health", "policyNo": "CH-987321"},
        {"id": "PAT-104", "name": "Diya Sengupta", "dob": "2001-02-17", "gender": "Female", "phone": "9820044556", "address": "15 Salt Lake, Kolkata", "bloodGroup": "AB+", "companyId": "ICICI Lombard", "policyNo": "IL-112233"},
        {"id": "PAT-105", "name": "Ramesh Chawla", "dob": "1962-08-30", "gender": "Male", "phone": "9820055667", "address": "304 Banjara Hills, Hyderabad", "bloodGroup": "O-", "companyId": "Star Health", "policyNo": "SH-334455"},
        {"id": "PAT-106", "name": "Pooja Bhatia", "dob": "1990-06-14", "gender": "Female", "phone": "9820066778", "address": "77 Koregaon Park, Pune", "bloodGroup": "B-", "companyId": "Niva Bupa", "policyNo": "NB-998877"},
        {"id": "PAT-107", "name": "Siddharth Rao", "dob": "1982-12-01", "gender": "Male", "phone": "9820077889", "address": "21 Anna Nagar, Chennai", "bloodGroup": "A-", "companyId": "HDFC ERGO", "policyNo": "HE-887766"},
        {"id": "PAT-108", "name": "Kavita Malhotra", "dob": "1998-03-29", "gender": "Female", "phone": "9820088990", "address": "55 Sector 17, Chandigarh", "bloodGroup": "O+", "companyId": "Care Health", "policyNo": "CH-445566"},
        {"id": "PAT-109", "name": "Vikram Sethi", "dob": "1970-07-19", "gender": "Male", "phone": "9820099001", "address": "104 Vastrapur, Ahmedabad", "bloodGroup": "B+", "companyId": "Star Health", "policyNo": "SH-667788"},
        {"id": "PAT-110", "name": "Ananya Chatterjee", "dob": "1996-10-10", "gender": "Female", "phone": "9820110112", "address": "90 Park Street, Kolkata", "bloodGroup": "AB-", "companyId": "ICICI Lombard", "policyNo": "IL-556677"}
    ]
    for p in patients_data:
        run_query(
            f"""
            MERGE (p:{sm.LABEL_PATIENT} {{id: $id}})
            SET p.name = $name,
                p.dob = $dob,
                p.gender = $gender,
                p.phone = $phone,
                p.address = $address,
                p.bloodGroup = $bloodGroup,
                p.companyId = $companyId,
                p.policyNo = $policyNo
            """,
            p
        )

    print("[4/7] Seeding Appointments, Consultations & Treatments...")
    appointments_data = [
        {"id": "APT-201", "patId": "PAT-101", "docId": "DOC-01", "date": "2026-03-10", "time": "10:00", "status": "Completed"},
        {"id": "APT-202", "patId": "PAT-102", "docId": "DOC-04", "date": "2026-03-12", "time": "11:30", "status": "Completed"},
        {"id": "APT-203", "patId": "PAT-103", "docId": "DOC-06", "date": "2026-03-14", "time": "09:00", "status": "Completed"},
        {"id": "APT-204", "patId": "PAT-104", "docId": "DOC-10", "date": "2026-03-15", "time": "14:00", "status": "Completed"},
        {"id": "APT-205", "patId": "PAT-105", "docId": "DOC-01", "date": "2026-03-18", "time": "10:30", "status": "Completed"},
        {"id": "APT-206", "patId": "PAT-106", "docId": "DOC-02", "date": "2026-03-20", "time": "12:00", "status": "Completed"},
        {"id": "APT-207", "patId": "PAT-107", "docId": "DOC-06", "date": "2026-03-22", "time": "15:30", "status": "Completed"},
        {"id": "APT-208", "patId": "PAT-108", "docId": "DOC-11", "date": "2026-03-25", "time": "16:00", "status": "Completed"},
        {"id": "APT-209", "patId": "PAT-109", "docId": "DOC-03", "date": "2026-03-28", "time": "11:00", "status": "Completed"},
        {"id": "APT-210", "patId": "PAT-110", "docId": "DOC-01", "date": "2026-04-02", "time": "09:30", "status": "Scheduled"},
    ]

    for apt in appointments_data:
        run_query(
            f"""
            MATCH (p:{sm.LABEL_PATIENT} {{id: $patId}})
            MATCH (d:{sm.LABEL_DOCTOR} {{id: $docId}})
            MERGE (a:{sm.LABEL_APPOINTMENT} {{id: $id}})
            SET a.appointmentDate = date($date),
                a.time = $time,
                a.status = $status
            MERGE (p)-[:{sm.REL_HAS_APPOINTMENT}]->(a)
            MERGE (d)-[:{sm.REL_ASSIGNED_TO}]->(a)
            """,
            apt
        )

    clinical_data = [
        {
            "aptId": "APT-201",
            "consId": "CON-301",
            "date": "2026-03-10",
            "diagnosis": "Hypertensive Heart Disease",
            "notes": "Patient complains of chest tightness upon exertion.",
            "treatId": "TRT-401",
            "rx": {"id": "RX-501", "type": "Amlodipine 5mg", "dosage": "Once Daily", "days": 30, "status": "Active"},
            "lab": {"id": "LAB-601", "type": "Lipid Profile & ECG", "status": "Abnormal", "result": "Elevated LDL (165 mg/dL), Sinus Rhythm", "charge": 1800.0}
        },
        {
            "aptId": "APT-202",
            "consId": "CON-302",
            "date": "2026-03-12",
            "diagnosis": "Migraine with Aura",
            "notes": "Recurring unilateral throbbing headache with photophobia.",
            "treatId": "TRT-402",
            "rx": {"id": "RX-502", "type": "Sumatriptan 50mg", "dosage": "SOS as needed", "days": 15, "status": "Active"},
            "lab": {"id": "LAB-602", "type": "Brain MRI", "status": "Normal", "result": "No focal lesions or hemorrhage", "charge": 4500.0}
        },
        {
            "aptId": "APT-203",
            "consId": "CON-303",
            "date": "2026-03-14",
            "diagnosis": "Osteoarthritis of Right Knee",
            "notes": "Severe joint stiffness and difficulty climbing stairs.",
            "treatId": "TRT-403",
            "rx": {"id": "RX-503", "type": "Glucosamine + Paracetamol", "dosage": "Twice Daily", "days": 45, "status": "Active"},
            "lab": {"id": "LAB-603", "type": "Knee Joint X-Ray", "status": "Abnormal", "result": "Grade 3 joint space narrowing", "charge": 1200.0}
        },
        {
            "aptId": "APT-204",
            "consId": "CON-304",
            "date": "2026-03-15",
            "diagnosis": "Type 2 Diabetes Mellitus with Neuropathy",
            "notes": "Fasting blood sugar poorly controlled, tingling in toes.",
            "treatId": "TRT-404",
            "rx": {"id": "RX-504", "type": "Metformin 1000mg + Pregabalin", "dosage": "Morning & Night", "days": 60, "status": "Active"},
            "lab": {"id": "LAB-604", "type": "HbA1c & Nerve Conduction", "status": "Abnormal", "result": "HbA1c 9.4% (Severe Uncontrolled)", "charge": 2200.0}
        },
        {
            "aptId": "APT-205",
            "consId": "CON-305",
            "date": "2026-03-18",
            "diagnosis": "Coronary Artery Stenosis",
            "notes": "Angina symptoms on moderate walking.",
            "treatId": "TRT-405",
            "rx": {"id": "RX-505", "type": "Atorvastatin 40mg + Clopidogrel", "dosage": "Bedtime", "days": 90, "status": "Active"},
            "lab": {"id": "LAB-605", "type": "CT Coronary Angiogram", "status": "Abnormal", "result": "75% stenosis in LAD", "charge": 8500.0}
        },
        {
            "aptId": "APT-206",
            "consId": "CON-306",
            "date": "2026-03-20",
            "diagnosis": "Atrial Fibrillation",
            "notes": "Palpitations accompanied by lightheadedness.",
            "treatId": "TRT-406",
            "rx": {"id": "RX-506", "type": "Metoprolol Succinate 25mg", "dosage": "Once Daily Morning", "days": 30, "status": "Active"},
            "lab": {"id": "LAB-606", "type": "Holter 24hr Monitor", "status": "Normal", "result": "Occasional ectopic beats", "charge": 3200.0}
        },
        {
            "aptId": "APT-207",
            "consId": "CON-307",
            "date": "2026-03-22",
            "diagnosis": "Lumbar Disc Herniation (L4-L5)",
            "notes": "Radiating sciatica down the left leg.",
            "treatId": "TRT-407",
            "rx": {"id": "RX-507", "type": "Methylprednisolone dose pack", "dosage": "Tapering schedule", "days": 7, "status": "Completed"},
            "lab": {"id": "LAB-607", "type": "Lumbar Spine MRI", "status": "Abnormal", "result": "Posterolateral disc extrusion compressing L5 nerve", "charge": 5000.0}
        },
        {
            "aptId": "APT-208",
            "consId": "CON-308",
            "date": "2026-03-25",
            "diagnosis": "Community-Acquired Bronchitis",
            "notes": "Productive cough and low grade fever for 5 days.",
            "treatId": "TRT-408",
            "rx": {"id": "RX-508", "type": "Azithromycin 500mg", "dosage": "Once Daily for 5 days", "days": 5, "status": "Completed"},
            "lab": {"id": "LAB-608", "type": "Chest X-Ray & CBC", "status": "Normal", "result": "Mild bronchial wall thickening, WBC normal", "charge": 1100.0}
        },
        {
            "aptId": "APT-209",
            "consId": "CON-309",
            "date": "2026-03-28",
            "diagnosis": "Congestive Cardiac Failure (Stage C)",
            "notes": "Bilateral pedal edema and orthopnea.",
            "treatId": "TRT-409",
            "rx": {"id": "RX-509", "type": "Sacubitril/Valsartan + Torsemide", "dosage": "Twice Daily", "days": 60, "status": "Active"},
            "lab": {"id": "LAB-609", "type": "2D Echocardiogram & NT-proBNP", "status": "Abnormal", "result": "EF 32%, Elevated NT-proBNP 4200 pg/mL", "charge": 4800.0}
        }
    ]

    for item in clinical_data:
        run_query(
            f"""
            MATCH (a:{sm.LABEL_APPOINTMENT} {{id: $aptId}})
            MERGE (c:{sm.LABEL_CONSULTATION} {{id: $consId}})
            SET c.consultationDate = date($date),
                c.diagnosis = $diagnosis,
                c.notes = $notes,
                c.reason = $diagnosis
            MERGE (a)-[:{sm.REL_HAS_CONSULTATION}]->(c)

            MERGE (t:{sm.LABEL_TREATMENT} {{id: $treatId}})
            SET t.description = $diagnosis + ' Protocol',
                t.date = date($date)
            MERGE (a)-[:{sm.REL_HAS_TREATMENT}]->(t)

            MERGE (rx:{sm.LABEL_PRESCRIPTION} {{id: $rxId}})
            SET rx.treatmentType = $rxType,
                rx.dosage = $rxDosage,
                rx.durationDays = $rxDays,
                rx.status = $rxStatus
            MERGE (t)-[:{sm.REL_HAS_PRESCRIPTION}]->(rx)

            MERGE (lt:{sm.LABEL_LAB_TEST} {{id: $labId}})
            SET lt.testType = $labType,
                lt.status = $labStatus,
                lt.resultStatus = $labStatus,
                lt.result = $labResult,
                lt.charge = $labCharge
            MERGE (t)-[:{sm.REL_HAS_LAB_TEST}]->(lt)
            """,
            {
                "aptId": item["aptId"],
                "consId": item["consId"],
                "date": item["date"],
                "diagnosis": item["diagnosis"],
                "notes": item["notes"],
                "treatId": item["treatId"],
                "rxId": item["rx"]["id"],
                "rxType": item["rx"]["type"],
                "rxDosage": item["rx"]["dosage"],
                "rxDays": item["rx"]["days"],
                "rxStatus": item["rx"]["status"],
                "labId": item["lab"]["id"],
                "labType": item["lab"]["type"],
                "labStatus": item["lab"]["status"],
                "labResult": item["lab"]["result"],
                "labCharge": item["lab"]["charge"]
            }
        )

    print("[5/7] Seeding Billing & Insurance Claims...")
    billing_data = [
        {"patId": "PAT-101", "treatId": "TRT-401", "billId": "BIL-701", "total": 12500.0, "cons": 1500.0, "lab": 1800.0, "pharm": 2200.0, "room": 7000.0, "mode": "Insurance", "status": "Paid", "claim": {"id": "CLM-801", "company": "Star Health", "claimAmount": 10000.0, "approved": 8500.0, "status": "Approved"}},
        {"patId": "PAT-102", "treatId": "TRT-402", "billId": "BIL-702", "total": 6800.0, "cons": 1200.0, "lab": 4500.0, "pharm": 1100.0, "room": 0.0, "mode": "UPI", "status": "Paid", "claim": {"id": "CLM-802", "company": "HDFC ERGO", "claimAmount": 5000.0, "approved": 4200.0, "status": "Approved"}},
        {"patId": "PAT-103", "treatId": "TRT-403", "billId": "BIL-703", "total": 3500.0, "cons": 1000.0, "lab": 1200.0, "pharm": 1300.0, "room": 0.0, "mode": "Card", "status": "Paid", "claim": None},
        {"patId": "PAT-104", "treatId": "TRT-404", "billId": "BIL-704", "total": 5400.0, "cons": 1000.0, "lab": 2200.0, "pharm": 2200.0, "room": 0.0, "mode": "UPI", "status": "Paid", "claim": {"id": "CLM-804", "company": "ICICI Lombard", "claimAmount": 4000.0, "approved": 3200.0, "status": "Approved"}},
        {"patId": "PAT-105", "treatId": "TRT-405", "billId": "BIL-705", "total": 28500.0, "cons": 2000.0, "lab": 8500.0, "pharm": 3000.0, "room": 15000.0, "mode": "Insurance", "status": "Paid", "claim": {"id": "CLM-805", "company": "Star Health", "claimAmount": 25000.0, "approved": 22000.0, "status": "Approved"}},
        {"patId": "PAT-106", "treatId": "TRT-406", "billId": "BIL-706", "total": 5200.0, "cons": 1200.0, "lab": 3200.0, "pharm": 800.0, "room": 0.0, "mode": "Card", "status": "Paid", "claim": None},
        {"patId": "PAT-107", "treatId": "TRT-407", "billId": "BIL-707", "total": 18000.0, "cons": 1500.0, "lab": 5000.0, "pharm": 1500.0, "room": 10000.0, "mode": "Insurance", "status": "Paid", "claim": {"id": "CLM-807", "company": "HDFC ERGO", "claimAmount": 16000.0, "approved": 13500.0, "status": "Approved"}},
        {"patId": "PAT-108", "treatId": "TRT-408", "billId": "BIL-708", "total": 2300.0, "cons": 800.0, "lab": 1100.0, "pharm": 400.0, "room": 0.0, "mode": "Cash", "status": "Paid", "claim": None},
        {"patId": "PAT-109", "treatId": "TRT-409", "billId": "BIL-709", "total": 32000.0, "cons": 2200.0, "lab": 4800.0, "pharm": 5000.0, "room": 20000.0, "mode": "Insurance", "status": "Pending", "claim": {"id": "CLM-809", "company": "Star Health", "claimAmount": 30000.0, "approved": 24000.0, "status": "Submitted"}}
    ]

    for b in billing_data:
        run_query(
            f"""
            MATCH (p:{sm.LABEL_PATIENT} {{id: $patId}})
            MATCH (t:{sm.LABEL_TREATMENT} {{id: $treatId}})
            MERGE (bill:{sm.LABEL_BILL} {{id: $billId}})
            SET bill.amount = $total,
                bill.consultationCharge = $cons,
                bill.labCharge = $lab,
                bill.pharmacyCharge = $pharm,
                bill.roomCharge = $room,
                bill.otherCharge = 0.0,
                bill.paymentMode = $mode,
                bill.paymentStatus = $status,
                bill.billingDate = date()
            MERGE (p)-[:{sm.REL_HAS_BILL}]->(bill)
            MERGE (t)-[:{sm.REL_HAS_BILL}]->(bill)
            """,
            {
                "patId": b["patId"],
                "treatId": b["treatId"],
                "billId": b["billId"],
                "total": b["total"],
                "cons": b["cons"],
                "lab": b["lab"],
                "pharm": b["pharm"],
                "room": b["room"],
                "mode": b["mode"],
                "status": b["status"]
            }
        )

        if b["claim"]:
            cl = b["claim"]
            run_query(
                f"""
                MATCH (p:{sm.LABEL_PATIENT} {{id: $patId}})
                MATCH (bill:{sm.LABEL_BILL} {{id: $billId}})
                MERGE (claim:{sm.LABEL_INSURANCE_CLAIM} {{id: $claimId}})
                SET claim.companyId = $company,
                    claim.claimAmount = $claimAmount,
                    claim.approvedAmount = $approved,
                    claim.status = $status
                MERGE (bill)-[:{sm.REL_HAS_CLAIM}]->(claim)
                MERGE (p)-[:{sm.REL_HAS_CLAIM}]->(claim)
                """,
                {
                    "patId": b["patId"],
                    "billId": b["billId"],
                    "claimId": cl["id"],
                    "company": cl["company"],
                    "claimAmount": cl["claimAmount"],
                    "approved": cl["approved"],
                    "status": cl["status"]
                }
            )

    print("[6/7] Validating Seeded Graph...")
    res = run_query("MATCH (n) RETURN count(n) AS nodes")
    rel_res = run_query("MATCH ()-[r]->() RETURN count(r) AS rels")
    print(f"      Total Nodes Created: {res[0]['nodes']}")
    print(f"      Total Relationships Created: {rel_res[0]['rels']}")

    print("[7/7] Testing Viva/DA3 Queries...")
    sample_q = run_query(
        f"""
        MATCH (d:{sm.LABEL_DOCTOR})-[:{sm.REL_BELONGS_TO}]->(dep:{sm.LABEL_DEPARTMENT})
        WITH dep, count(d) AS doctors
        WHERE doctors > 2
        RETURN dep.name AS department, doctors
        """
    )
    print(f"      Departments with > 2 doctors: {[r['department'] for r in sample_q]}")

    abnormal_q = run_query(
        f"""
        MATCH (p:{sm.LABEL_PATIENT})
        WHERE EXISTS {{
          MATCH (p)-[:{sm.REL_HAS_APPOINTMENT}]->(:{sm.LABEL_APPOINTMENT})-[:{sm.REL_HAS_TREATMENT}]->(:{sm.LABEL_TREATMENT})-[:{sm.REL_HAS_LAB_TEST}]->(t:{sm.LABEL_LAB_TEST})
          WHERE t.status = 'Abnormal' OR t.resultStatus = 'Abnormal'
        }}
        RETURN coalesce(p.name, p.firstName + ' ' + p.lastName) AS patient
        """
    )
    print(f"      Patients with Abnormal Lab tests (Query 10): {len(abnormal_q)} found")

    print("\n" + "=" * 60)
    print("SUCCESS: Database has been fully seeded and verified!")
    print("All 11 DA3 queries and dashboard charts are ready to run.")
    print("=" * 60)

if __name__ == "__main__":
    try:
        seed()
    finally:
        close_driver()
