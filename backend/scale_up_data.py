"""
Scale Data Script for CityCare Hospital Management System
Expands the active Neo4j AuraDB graph database to ~1000 - 1100 nodes with complete,
realistic medical entities and all relationships.
"""

import sys
import random
from datetime import date, timedelta
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from db import get_driver, close_driver
import schema_map as sm

# Reference data lists
FIRST_NAMES_MALE = [
    "Aditya", "Rohan", "Manish", "Suresh", "Karan", "Nikhil", "Deepak", "Vivek",
    "Abhishek", "Gaurav", "Rahul", "Sachin", "Vijay", "Anil", "Sunil", "Rajesh",
    "Sanjay", "Dinesh", "Manoj", "Pradeep", "Harish", "Kunal", "Alok", "Dev", "Yash"
]
FIRST_NAMES_FEMALE = [
    "Pooja", "Ananya", "Sneha", "Kavita", "Ritu", "Priyanka", "Deepa", "Shalini",
    "Neha", "Swati", "Megha", "Shweta", "Divya", "Sangeeta", "Bhavna", "Sunita",
    "Radha", "Kiran", "Archana", "Geeta", "Jyoti", "Pallavi", "Preeti", "Rashmi", "Tanvi"
]
LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Malhotra", "Mehta", "Patel", "Nair", "Iyer",
    "Rao", "Reddy", "Kulkarni", "Deshmukh", "Chawla", "Bhatia", "Saxena", "Sen",
    "Chatterjee", "Mishra", "Joshi", "Bhatnagar", "Agarwal", "Chopra", "Kapoor", "Menon"
]
CITIES = ["Mumbai", "Delhi", "Bengaluru", "Chennai", "Hyderabad", "Kolkata", "Pune", "Ahmedabad", "Chandigarh", "Jaipur"]
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
INSURANCE_COMPANIES = ["Star Health", "HDFC ERGO", "ICICI Lombard", "Care Health", "Niva Bupa"]
PAYMENT_MODES = ["Insurance", "UPI", "Card", "Cash"]

DOCTOR_SPECIALTIES = {
    "DEP-01": ("Cardiology", ["Interventional Cardiology", "Cardiology Specialist", "Electrophysiology", "Heart Failure Specialist"]),
    "DEP-02": ("Neurology", ["Neurology Specialist", "Neuro-radiologist", "Stroke Specialist", "Epileptology"]),
    "DEP-03": ("Orthopedics", ["Orthopedic Surgeon", "Joint Replacement", "Spine Surgery", "Sports Medicine"]),
    "DEP-04": ("Pediatrics", ["Pediatrician", "Pediatric Neonatology", "Pediatric Critical Care"]),
    "DEP-05": ("General Medicine", ["Internal Medicine", "Consultant Physician", "Diabetology", "Infectious Disease"]),
    "DEP-06": ("Oncology", ["Medical Oncology", "Surgical Oncology", "Radiation Oncology"]),
    "DEP-07": ("Dermatology", ["Cosmetic Dermatology", "Dermatologist", "Pediatric Dermatology"]),
    "DEP-08": ("Gastroenterology", ["Hepatology", "Endoscopy Specialist", "Gastroenterologist"]),
    "DEP-09": ("Nephrology & Urology", ["Nephrologist", "Urological Surgeon", "Renal Transplant Specialist"]),
    "DEP-10": ("ENT & Head-Neck", ["Otolaryngologist", "ENT Surgeon", "Rhinologist"]),
    "DEP-11": ("Pulmonology", ["Pulmonologist", "Interventional Pulmonology", "Sleep Medicine"])
}

DIAGNOSES = [
    ("Type 2 Diabetes Mellitus", "Metformin 500mg", "HbA1c & Fasting Glucose", 1200.0, "Abnormal", "HbA1c 8.8% (Elevated)"),
    ("Essential Hypertension", "Telmisartan 40mg", "Lipid Profile & ECG", 1500.0, "Abnormal", "Borderline high LDL 148 mg/dL"),
    ("Stable Angina Pectoris", "Atorvastatin 20mg + Aspirin", "Treadmill Stress Test", 3500.0, "Abnormal", "ST-segment depression in Lead II"),
    ("Chronic Bronchial Asthma", "Budesonide + Formoterol Inhaler", "Pulmonary Function Test", 2200.0, "Abnormal", "FEV1/FVC ratio 65%"),
    ("Osteoarthritis of Bilateral Knees", "Diacerein 50mg + Paracetamol", "Knee X-Ray Bilateral", 1100.0, "Abnormal", "Grade 2 Joint Space Reduction"),
    ("Lumbar Spondylosis", "Pregabalin 75mg + Methylcobalamin", "Lumbosacral Spine X-Ray", 1400.0, "Normal", "Mild osteophytes without canal stenosis"),
    ("Gastroesophageal Reflux Disease (GERD)", "Pantoprazole 40mg + Domperidone", "Upper GI Endoscopy", 4500.0, "Normal", "Mild mucosal erythema, no ulcers"),
    ("Acute Viral Pharyngitis", "Azithromycin 500mg + Cetirizine", "Complete Blood Count (CBC)", 450.0, "Normal", "WBC within normal limits 7,800/uL"),
    ("Hypothyroidism", "Levothyroxine 50mcg", "Thyroid Profile (T3, T4, TSH)", 800.0, "Abnormal", "TSH 7.4 uIU/mL (Elevated)"),
    ("Kidney Stone (Nephrolithiasis)", "Tamsulosin 0.4mg + Analgesics", "Renal Ultrasound KUB", 1800.0, "Abnormal", "4.2mm calculus in right lower pole"),
    ("Allergic Dermatitis", "Levocetirizine 5mg + Calamine", "Total IgE Serum Test", 1000.0, "Abnormal", "Elevated IgE at 420 IU/mL"),
    ("Iron Deficiency Anemia", "Ferrous Ascorbate + Folic Acid", "Complete Blood Count & Ferritin", 950.0, "Abnormal", "Hemoglobin 9.2 g/dL, Ferritin 12 ng/mL"),
    ("Chronic Migraine", "Propranolol 40mg + Naproxen", "Brain MRI with Contrast", 6500.0, "Normal", "Normal brain parenchyma, no mass lesion"),
    ("Fatty Liver Disease (Grade 1)", "Ursodeoxycholic Acid 300mg", "Liver Function Test (LFT)", 1100.0, "Abnormal", "SGPT/ALT 64 U/L (Elevated)"),
    ("Benign Prostatic Hyperplasia", "Finasteride 5mg + Tamsulosin", "Serum PSA Test", 1300.0, "Normal", "PSA 2.1 ng/mL (Normal)"),
    ("Acute Sinusitis", "Amoxicillin-Clavulanate 625mg", "PNS X-Ray Water's View", 850.0, "Normal", "Mild mucosal haziness in maxillary sinus"),
    ("Cervical Radiculopathy", "Aceclofenac + Thiocolchicoside", "Cervical Spine MRI", 5500.0, "Abnormal", "C5-C6 posterior disc bulge"),
    ("Gouty Arthritis", "Febuxostat 40mg + Colchicine", "Serum Uric Acid Test", 600.0, "Abnormal", "Uric Acid 8.9 mg/dL (High)"),
    ("General Preventive Health Check", "Multivitamin & Minerals", "Comprehensive Health Panel", 2800.0, "Normal", "All baseline metrics within reference range")
]

def generate_random_patient(pat_idx: int):
    is_male = random.random() > 0.5
    fn = random.choice(FIRST_NAMES_MALE if is_male else FIRST_NAMES_FEMALE)
    ln = random.choice(LAST_NAMES)
    full_name = f"{fn} {ln}"
    gender = "Male" if is_male else "Female"
    
    # Age between 18 and 82
    birth_year = random.randint(1944, 2006)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    dob_str = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
    
    phone = f"98{random.randint(10000000, 99999999)}"
    city = random.choice(CITIES)
    address = f"{random.randint(10, 899)}, Sector {random.randint(1, 45)}, {city}"
    blood_group = random.choice(BLOOD_GROUPS)
    company = random.choice(INSURANCE_COMPANIES)
    policy_no = f"{company[:2].upper()}-{random.randint(100000, 999999)}"
    
    pat_id = f"PAT-{pat_idx:03d}"
    return {
        "id": pat_id,
        "name": full_name,
        "firstName": fn,
        "lastName": ln,
        "gender": gender,
        "dob": dob_str,
        "phone": phone,
        "address": address,
        "bloodGroup": blood_group,
        "companyId": company,
        "policyNo": policy_no
    }

def generate_random_doctor(doc_idx: int, dep_id: str):
    is_male = random.random() > 0.5
    fn = random.choice(FIRST_NAMES_MALE if is_male else FIRST_NAMES_FEMALE)
    ln = random.choice(LAST_NAMES)
    full_name = f"Dr. {fn} {ln}"
    dep_info = DOCTOR_SPECIALTIES.get(dep_id, ("General Medicine", ["Specialist"]))
    spec = random.choice(dep_info[1])
    phone = f"98{random.randint(10000000, 99999999)}"
    email = f"{fn.lower()}.{ln.lower()}{random.randint(1, 99)}@citycare.com"
    doc_id = f"DOC-{doc_idx:02d}"
    fee = random.choice([600, 800, 1000, 1200, 1500])
    doc_type = random.choice(["Full-Time", "Full-Time", "Visiting"])
    
    return {
        "id": doc_id,
        "name": full_name,
        "firstName": fn,
        "lastName": ln,
        "depId": dep_id,
        "specialty": spec,
        "specialization": spec,
        "phone": phone,
        "email": email,
        "fee": fee,
        "doc_type": doc_type
    }

def scale_database(target_total_nodes: int = 1050):
    print("=" * 70)
    print("  CityCare Hospital Graph Data Scaler - Expanding to 1000-1100 Nodes")
    print("=" * 70)
    
    driver = get_driver()
    with driver.session() as session:
        # Check current counts
        initial_nodes = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
        initial_rels = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
        print(f"[*] Current Total Nodes:         {initial_nodes}")
        print(f"[*] Current Total Relationships: {initial_rels}")
        
        needed_nodes = target_total_nodes - initial_nodes
        print(f"[*] Target Total Nodes:          {target_total_nodes}")
        print(f"[*] Required Additional Nodes:   {needed_nodes}")
        
        if needed_nodes <= 0:
            print("[INFO] Target already satisfied. Nothing to add.")
            return

        # Target additions calibrated to hit exact total:
        # 15 Doctors + 100 Patients + 125 Appointments + 115 Consultations
        # + 110 Treatments + 110 Prescriptions + 50 LabTests + 90 Bills + 47 Claims = 762 nodes!
        n_docs = 15
        n_pats = 100
        n_apts = 125
        n_cons = 115
        n_trts = 110
        n_rxs  = 110
        n_labs = 50
        n_bils = 90
        n_clms = 47
        
        planned_total_added = n_docs + n_pats + n_apts + n_cons + n_trts + n_rxs + n_labs + n_bils + n_clms
        print(f"[*] Planned new nodes: {planned_total_added} (Doctor:{n_docs}, Patient:{n_pats}, "
              f"Appt:{n_apts}, Cons:{n_cons}, Trt:{n_trts}, Rx:{n_rxs}, Lab:{n_labs}, Bill:{n_bils}, Claim:{n_clms})")
        print(f"[*] Expected Final Node Count:   {initial_nodes + planned_total_added}\n")
        
        # 1. DOCTORS
        print(f"[1/7] Adding {n_docs} Doctors across departments...")
        dep_keys = list(DOCTOR_SPECIALTIES.keys())
        doc_ids = []
        for i in range(1, n_docs + 1):
            doc_idx = 30 + i
            dep_id = dep_keys[(i - 1) % len(dep_keys)]
            doc = generate_random_doctor(doc_idx, dep_id)
            doc_ids.append(doc["id"])
            session.run("""
                MERGE (doc:Doctor {id: $id})
                SET doc.name = $name,
                    doc.firstName = $firstName,
                    doc.lastName = $lastName,
                    doc.emp_id = $id,
                    doc.specialty = $specialty,
                    doc.specialization = $specialization,
                    doc.phone = $phone,
                    doc.email = $email,
                    doc.consultation_fee = $fee,
                    doc.doctor_type = $doc_type,
                    doc.role = 'Doctor'
                WITH doc
                MATCH (dep:Department)
                WHERE dep.id = $depId OR dep.dept_id = $depId
                MERGE (doc)-[:BELONGS_TO]->(dep)
                MERGE (doc)-[:WORKS_IN]->(dep)
            """, doc)

        # Retrieve all available Doctor IDs in DB (both newly added and existing)
        all_doc_records = session.run("MATCH (d:Doctor) RETURN coalesce(d.id, d.emp_id) AS id").data()
        all_doc_ids = [r["id"] for r in all_doc_records if r["id"]]

        # 2. PATIENTS
        print(f"[2/7] Adding {n_pats} Patients with complete demographics...")
        pat_ids = []
        for i in range(1, n_pats + 1):
            pat_idx = 200 + i
            pat = generate_random_patient(pat_idx)
            pat_ids.append(pat["id"])
            session.run("""
                MERGE (p:Patient {id: $id})
                SET p.name = $name,
                    p.firstName = $firstName,
                    p.lastName = $lastName,
                    p.patient_id = $id,
                    p.dob = date($dob),
                    p.dateOfBirth = date($dob),
                    p.gender = $gender,
                    p.phone = $phone,
                    p.contactNumber = $phone,
                    p.address = $address,
                    p.bloodGroup = $bloodGroup,
                    p.blood_group = $bloodGroup,
                    p.companyId = $companyId,
                    p.policyNo = $policyNo
            """, pat)

        all_pat_records = session.run("MATCH (p:Patient) RETURN coalesce(p.id, p.patient_id) AS id").data()
        all_pat_ids = [r["id"] for r in all_pat_records if r["id"]]

        # 3. APPOINTMENTS
        print(f"[3/7] Adding {n_apts} Appointments linking Patients and Doctors...")
        apt_ids = []
        base_date = date.today()
        statuses = ["Completed", "Completed", "Completed", "Scheduled", "Cancelled"]
        hours = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00"]

        for i in range(1, n_apts + 1):
            apt_idx = 300 + i
            apt_id = f"APT-{apt_idx:03d}"
            apt_ids.append(apt_id)
            
            # Days offset: between 90 days ago and 15 days in future
            day_offset = random.randint(-90, 15)
            apt_date = base_date + timedelta(days=day_offset)
            status = "Scheduled" if day_offset > 0 else random.choice(statuses)
            time_slot = random.choice(hours)
            pat_id = random.choice(all_pat_ids)
            doc_id = random.choice(all_doc_ids)
            diag_item = random.choice(DIAGNOSES)
            reason = diag_item[0]
            
            session.run("""
                MATCH (p:Patient) WHERE p.id = $patId OR p.patient_id = $patId
                MATCH (d:Doctor) WHERE d.id = $docId OR d.emp_id = $docId
                MERGE (a:Appointments {id: $aptId})
                SET a.appointmentDate = date($aptDate),
                    a.date = date($aptDate),
                    a.time = $time,
                    a.appointmentTime = $time,
                    a.status = $status,
                    a.reason = $reason,
                    a.reasonForVisit = $reason
                MERGE (p)-[:HAS_APPOINTMENT]->(a)
                MERGE (d)-[:ASSIGNED_TO]->(a)
            """, {
                "aptId": apt_id,
                "aptDate": str(apt_date),
                "time": time_slot,
                "status": status,
                "reason": reason,
                "patId": pat_id,
                "docId": doc_id
            })

        # 4. CONSULTATIONS & TREATMENTS
        print(f"[4/7] Adding {n_cons} Consultations & {n_trts} Treatments...")
        trt_ids = []
        for i in range(1, n_cons + 1):
            cons_idx = 400 + i
            cons_id = f"CON-{cons_idx:03d}"
            apt_id = apt_ids[(i - 1) % len(apt_ids)]
            diag_item = random.choice(DIAGNOSES)
            diagnosis = diag_item[0]
            notes = f"Patient evaluated for {diagnosis.lower()}. Clinical vital parameters assessed and therapeutic regimen prescribed."
            cons_date = str(base_date - timedelta(days=random.randint(1, 90)))
            
            # Add Consultation
            session.run("""
                MATCH (a:Appointments {id: $aptId})
                MERGE (c:Consultation {id: $consId})
                SET c.consultationDate = date($consDate),
                    c.date = date($consDate),
                    c.diagnosis = $diagnosis,
                    c.reason = $diagnosis,
                    c.notes = $notes
                MERGE (a)-[:HAS_CONSULTATION]->(c)
            """, {
                "aptId": apt_id,
                "consId": cons_id,
                "consDate": cons_date,
                "diagnosis": diagnosis,
                "notes": notes
            })

            # Add Treatment for the first n_trts items
            if i <= n_trts:
                trt_idx = 500 + i
                trt_id = f"TRT-{trt_idx:03d}"
                trt_ids.append((trt_id, apt_id, diag_item, cons_date))
                session.run("""
                    MATCH (a:Appointments {id: $aptId})
                    MERGE (t:Treatment {id: $trtId})
                    SET t.description = $diag + ' Protocol',
                        t.date = date($trtDate)
                    MERGE (a)-[:HAS_TREATMENT]->(t)
                """, {
                    "aptId": apt_id,
                    "trtId": trt_id,
                    "diag": diagnosis,
                    "trtDate": cons_date
                })

        # 5. PRESCRIPTIONS & LAB TESTS
        print(f"[5/7] Adding {n_rxs} Prescriptions & {n_labs} Lab Tests...")
        for i, (trt_id, apt_id, diag_item, treat_date) in enumerate(trt_ids, 1):
            if i <= n_rxs:
                rx_idx = 600 + i
                rx_id = f"RX-{rx_idx:03d}"
                med = diag_item[1]
                dosage = random.choice(["Once Daily", "Twice Daily", "Three Times Daily", "SOS as needed"])
                days = random.choice([7, 10, 14, 30, 60, 90])
                rx_status = random.choice(["Active", "Active", "Completed"])
                
                session.run("""
                    MATCH (t:Treatment {id: $trtId})
                    MERGE (rx:Prescription {id: $rxId})
                    SET rx.treatmentType = $med,
                        rx.dosage = $dosage,
                        rx.durationDays = $days,
                        rx.status = $status
                    MERGE (t)-[:HAS_PRESCRIPTION]->(rx)
                """, {
                    "trtId": trt_id,
                    "rxId": rx_id,
                    "med": med,
                    "dosage": dosage,
                    "days": days,
                    "status": rx_status
                })

            if i <= n_labs:
                lab_idx = 700 + i
                lab_id = f"LAB-{lab_idx:03d}"
                lab_type = diag_item[2]
                charge = diag_item[3]
                status = diag_item[4]
                result = diag_item[5]
                
                session.run("""
                    MATCH (t:Treatment {id: $trtId})
                    MERGE (lt:LabTest {id: $labId})
                    SET lt.testType = $labType,
                        lt.test_name = $labType,
                        lt.status = $status,
                        lt.resultStatus = $status,
                        lt.result = $result,
                        lt.charge = $charge,
                        lt.price = $charge
                    MERGE (t)-[:HAS_LAB_TEST]->(lt)
                """, {
                    "trtId": trt_id,
                    "labId": lab_id,
                    "labType": lab_type,
                    "status": status,
                    "result": result,
                    "charge": charge
                })

        # 6. BILLING & INSURANCE CLAIMS
        print(f"[6/7] Adding {n_bils} Billing records & {n_clms} Insurance Claims...")
        claim_counter = 0
        for i in range(1, n_bils + 1):
            bil_idx = 800 + i
            bil_id = f"BIL-{bil_idx:03d}"
            trt_id = trt_ids[(i - 1) % len(trt_ids)][0]
            
            # Find patient connected to this treatment's appointment
            pat_rec = session.run("""
                MATCH (p:Patient)-[:HAS_APPOINTMENT]->(a:Appointments)-[:HAS_TREATMENT]->(t:Treatment {id: $trtId})
                RETURN coalesce(p.id, p.patient_id) AS patId, coalesce(p.companyId, 'Star Health') AS comp
                LIMIT 1
            """, {"trtId": trt_id}).single()
            
            if pat_rec:
                pat_id = pat_rec["patId"]
                ins_company = pat_rec["comp"]
            else:
                pat_id = random.choice(all_pat_ids)
                ins_company = random.choice(INSURANCE_COMPANIES)

            cons_fee = random.choice([600.0, 800.0, 1000.0, 1500.0])
            lab_charge = random.choice([0.0, 800.0, 1500.0, 2500.0, 4500.0])
            pharm_charge = random.choice([350.0, 650.0, 1200.0, 2400.0])
            room_charge = random.choice([0.0, 0.0, 0.0, 4500.0, 9000.0, 18000.0])
            total_amt = round(cons_fee + lab_charge + pharm_charge + room_charge, 2)
            
            pay_mode = "Insurance" if (room_charge > 0 or random.random() > 0.5) else random.choice(["UPI", "Card", "Cash"])
            pay_status = "Paid" if random.random() > 0.15 else "Pending"
            
            bill_date = str(base_date - timedelta(days=random.randint(0, 75)))
            
            session.run("""
                MATCH (p:Patient) WHERE p.id = $patId OR p.patient_id = $patId
                MATCH (t:Treatment {id: $trtId})
                MERGE (b:Billing {id: $bilId})
                SET b.bill_id = $bilId,
                    b.amount = $amount,
                    b.total = $amount,
                    b.consultationCharge = $cons,
                    b.labCharge = $lab,
                    b.pharmacyCharge = $pharm,
                    b.roomCharge = $room,
                    b.otherCharge = 0.0,
                    b.paymentMode = $mode,
                    b.paymentStatus = $status,
                    b.billingDate = date($billDate)
                MERGE (p)-[:HAS_BILL]->(b)
                MERGE (t)-[:HAS_BILL]->(b)
            """, {
                "patId": pat_id,
                "trtId": trt_id,
                "bilId": bil_id,
                "amount": total_amt,
                "cons": cons_fee,
                "lab": lab_charge,
                "pharm": pharm_charge,
                "room": room_charge,
                "mode": pay_mode,
                "status": pay_status,
                "billDate": bill_date
            })

            # Create Insurance Claim if mode is Insurance and we haven't reached n_clms
            if pay_mode == "Insurance" and claim_counter < n_clms:
                claim_counter += 1
                clm_idx = 900 + claim_counter
                clm_id = f"CLM-{clm_idx:03d}"
                claim_amt = round(total_amt * random.uniform(0.75, 0.95), 2)
                clm_status = random.choice(["Approved", "Approved", "Approved", "Submitted", "In Review"])
                approved_amt = round(claim_amt * random.uniform(0.80, 1.0), 2) if clm_status == "Approved" else 0.0
                
                session.run("""
                    MATCH (p:Patient) WHERE p.id = $patId OR p.patient_id = $patId
                    MATCH (b:Billing {id: $bilId})
                    MERGE (cl:InsuranceClaim {id: $clmId})
                    SET cl.claim_id = $clmId,
                        cl.companyId = $comp,
                        cl.claimAmount = $claimAmt,
                        cl.approvedAmount = $approvedAmt,
                        cl.status = $status
                    MERGE (b)-[:HAS_INSURANCE_CLAIM]->(cl)
                    MERGE (p)-[:HAS_INSURANCE_CLAIM]->(cl)
                """, {
                    "patId": pat_id,
                    "bilId": bil_id,
                    "clmId": clm_id,
                    "comp": ins_company,
                    "claimAmt": claim_amt,
                    "approvedAmt": approved_amt,
                    "status": clm_status
                })

        # 7. FINAL VERIFICATION
        print("\n[7/7] Validating Final Database Totals...")
        final_nodes = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
        final_rels = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
        
        print("=" * 70)
        print(f"  [SUCCESS] SCALING COMPLETE!")
        print(f"  * Total Graph Nodes:         {final_nodes} (Target: 1000 - 1100)")
        print(f"  * Total Graph Relationships: {final_rels}")
        print("=" * 70)

if __name__ == "__main__":
    try:
        scale_database(target_total_nodes=1050)
    finally:
        close_driver()
