// ==============================================================================
// CityCare Hospital Management System - Additional Graph Dataset
// Compatible with Neo4j 5.x / Neo4j AuraDB
// Idempotent MERGE queries for Departments, Doctors, Patients, Appointments,
// Consultations, Treatments, Prescriptions, Lab Tests, Billing & Insurance Claims.
// ==============================================================================

// ------------------------------------------------------------------------------
// 1. DEPARTMENTS
// ------------------------------------------------------------------------------
MERGE (dep04:Department {id: 'DEP-04'}) SET dep04.name = 'Pediatrics', dep04.floor = '1st Floor';
MERGE (dep06:Department {id: 'DEP-06'}) SET dep06.name = 'Oncology', dep06.floor = '4th Floor';
MERGE (dep07:Department {id: 'DEP-07'}) SET dep07.name = 'Dermatology', dep07.floor = '2nd Floor';
MERGE (dep08:Department {id: 'DEP-08'}) SET dep08.name = 'Gastroenterology', dep08.floor = '3rd Floor';
MERGE (dep09:Department {id: 'DEP-09'}) SET dep09.name = 'Nephrology & Urology', dep09.floor = '4th Floor';
MERGE (dep10:Department {id: 'DEP-10'}) SET dep10.name = 'ENT & Head-Neck', dep10.floor = '2nd Floor';
MERGE (dep11:Department {id: 'DEP-11'}) SET dep11.name = 'Pulmonology', dep11.floor = '3rd Floor';

// ------------------------------------------------------------------------------
// 2. DOCTORS (Expanding Pediatrics, Oncology, and New Specialties)
// ------------------------------------------------------------------------------
// Oncology Doctors
MERGE (d13:Doctor {id: 'DOC-13'})
SET d13.name = 'Dr. Radhika Sen', d13.specialty = 'Medical Oncology', d13.specialization = 'Medical Oncology', d13.phone = '9876543222', d13.email = 'radhika.sen@citycare.com';
MERGE (d14:Doctor {id: 'DOC-14'})
SET d14.name = 'Dr. Tarun Nambiar', d14.specialty = 'Surgical Oncology', d14.specialization = 'Surgical Oncology', d14.phone = '9876543223', d14.email = 'tarun.nambiar@citycare.com';
MERGE (d15:Doctor {id: 'DOC-15'})
SET d15.name = 'Dr. Alok Verma', d15.specialty = 'Radiation Oncology', d15.specialization = 'Radiation Oncology', d15.phone = '9876543224', d15.email = 'alok.verma@citycare.com';

// Additional Pediatrics Doctors
MERGE (d16:Doctor {id: 'DOC-16'})
SET d16.name = 'Dr. Shalini Aggarwal', d16.specialty = 'Pediatric Cardiology', d16.specialization = 'Pediatric Cardiology', d16.phone = '9876543225', d16.email = 'shalini.aggarwal@citycare.com';
MERGE (d17:Doctor {id: 'DOC-17'})
SET d17.name = 'Dr. Vivek Menon', d17.specialty = 'Neonatology', d17.specialization = 'Neonatology', d17.phone = '9876543226', d17.email = 'vivek.menon@citycare.com';

// Dermatology Doctors
MERGE (d18:Doctor {id: 'DOC-18'})
SET d18.name = 'Dr. Natasha Kapoor', d18.specialty = 'Cosmetic Dermatology', d18.specialization = 'Cosmetic Dermatology', d18.phone = '9876543227', d18.email = 'natasha.kapoor@citycare.com';
MERGE (d19:Doctor {id: 'DOC-19'})
SET d19.name = 'Dr. Pradeep Mishra', d19.specialty = 'Dermatopathology', d19.specialization = 'Dermatopathology', d19.phone = '9876543228', d19.email = 'pradeep.mishra@citycare.com';

// Gastroenterology Doctors
MERGE (d20:Doctor {id: 'DOC-20'})
SET d20.name = 'Dr. Harish Chander', d20.specialty = 'Hepatology', d20.specialization = 'Hepatology', d20.phone = '9876543229', d20.email = 'harish.chander@citycare.com';
MERGE (d21:Doctor {id: 'DOC-21'})
SET d21.name = 'Dr. Deepa Nair', d21.specialty = 'Advanced Endoscopy', d21.specialization = 'Advanced Endoscopy', d21.phone = '9876543230', d21.email = 'deepa.nair@citycare.com';

// Nephrology & Urology Doctors
MERGE (d22:Doctor {id: 'DOC-22'})
SET d22.name = 'Dr. Farhan Siddiqui', d22.specialty = 'Renal Transplantation', d22.specialization = 'Renal Transplantation', d22.phone = '9876543231', d22.email = 'farhan.siddiqui@citycare.com';
MERGE (d23:Doctor {id: 'DOC-23'})
SET d23.name = 'Dr. Meenakshi Sundaram', d23.specialty = 'Urology & Laparoscopy', d23.specialization = 'Urology & Laparoscopy', d23.phone = '9876543232', d23.email = 'meenakshi.s@citycare.com';

// ENT & Pulmonology Doctors
MERGE (d24:Doctor {id: 'DOC-24'})
SET d24.name = 'Dr. Gautam Bhatnagar', d24.specialty = 'Otolaryngology & Head-Neck', d24.specialization = 'Otolaryngology & Head-Neck', d24.phone = '9876543233', d24.email = 'gautam.b@citycare.com';
MERGE (d25:Doctor {id: 'DOC-25'})
SET d25.name = 'Dr. Ritu Singhania', d25.specialty = 'Interventional Pulmonology', d25.specialization = 'Interventional Pulmonology', d25.phone = '9876543234', d25.email = 'ritu.singhania@citycare.com';

// Link Doctors to Departments
MATCH (d13:Doctor {id: 'DOC-13'}), (dep06:Department {id: 'DEP-06'}) MERGE (d13)-[:BELONGS_TO]->(dep06);
MATCH (d14:Doctor {id: 'DOC-14'}), (dep06:Department {id: 'DEP-06'}) MERGE (d14)-[:BELONGS_TO]->(dep06);
MATCH (d15:Doctor {id: 'DOC-15'}), (dep06:Department {id: 'DEP-06'}) MERGE (d15)-[:BELONGS_TO]->(dep06);
MATCH (d16:Doctor {id: 'DOC-16'}), (dep04:Department {id: 'DEP-04'}) MERGE (d16)-[:BELONGS_TO]->(dep04);
MATCH (d17:Doctor {id: 'DOC-17'}), (dep04:Department {id: 'DEP-04'}) MERGE (d17)-[:BELONGS_TO]->(dep04);
MATCH (d18:Doctor {id: 'DOC-18'}), (dep07:Department {id: 'DEP-07'}) MERGE (d18)-[:BELONGS_TO]->(dep07);
MATCH (d19:Doctor {id: 'DOC-19'}), (dep07:Department {id: 'DEP-07'}) MERGE (d19)-[:BELONGS_TO]->(dep07);
MATCH (d20:Doctor {id: 'DOC-20'}), (dep08:Department {id: 'DEP-08'}) MERGE (d20)-[:BELONGS_TO]->(dep08);
MATCH (d21:Doctor {id: 'DOC-21'}), (dep08:Department {id: 'DEP-08'}) MERGE (d21)-[:BELONGS_TO]->(dep08);
MATCH (d22:Doctor {id: 'DOC-22'}), (dep09:Department {id: 'DEP-09'}) MERGE (d22)-[:BELONGS_TO]->(dep09);
MATCH (d23:Doctor {id: 'DOC-23'}), (dep09:Department {id: 'DEP-09'}) MERGE (d23)-[:BELONGS_TO]->(dep09);
MATCH (d24:Doctor {id: 'DOC-24'}), (dep10:Department {id: 'DEP-10'}) MERGE (d24)-[:BELONGS_TO]->(dep10);
MATCH (d25:Doctor {id: 'DOC-25'}), (dep11:Department {id: 'DEP-11'}) MERGE (d25)-[:BELONGS_TO]->(dep11);

// ------------------------------------------------------------------------------
// 3. PATIENTS (PAT-111 to PAT-125)
// ------------------------------------------------------------------------------
MERGE (p111:Patient {id: 'PAT-111'})
SET p111.name = 'Ishaan Trivedi', p111.dob = '2016-05-18', p111.gender = 'Male', p111.phone = '9820121314', p111.address = '22 Juhu Scheme, Mumbai', p111.bloodGroup = 'O+', p111.companyId = 'HDFC ERGO', p111.policyNo = 'HE-119922';

MERGE (p112:Patient {id: 'PAT-112'})
SET p112.name = 'Geeta Srinivasan', p112.dob = '1958-11-20', p112.gender = 'Female', p112.phone = '9820131415', p112.address = '78 Mylapore, Chennai', p112.bloodGroup = 'B+', p112.companyId = 'Star Health', p112.policyNo = 'SH-991188';

MERGE (p113:Patient {id: 'PAT-113'})
SET p113.name = 'Rahul Wadhwa', p113.dob = '1992-07-03', p113.gender = 'Male', p113.phone = '9820141516', p113.address = '51 Model Town, Delhi', p113.bloodGroup = 'A+', p113.companyId = 'Care Health', p113.policyNo = 'CH-551144';

MERGE (p114:Patient {id: 'PAT-114'})
SET p114.name = 'Sanya Merchant', p114.dob = '1999-01-14', p114.gender = 'Female', p114.phone = '9820151617', p114.address = '102 Colaba, Mumbai', p114.bloodGroup = 'AB-', p114.companyId = 'ICICI Lombard', p114.policyNo = 'IL-774411';

MERGE (p115:Patient {id: 'PAT-115'})
SET p115.name = 'Brijesh Pandey', p115.dob = '1967-03-25', p115.gender = 'Male', p115.phone = '9820161718', p115.address = '14 Gomti Nagar, Lucknow', p115.bloodGroup = 'O-', p115.companyId = 'Star Health', p115.policyNo = 'SH-442266';

MERGE (p116:Patient {id: 'PAT-116'})
SET p116.name = 'Nidhi Goswami', p116.dob = '1985-09-09', p116.gender = 'Female', p116.phone = '9820171819', p116.address = '84 Viman Nagar, Pune', p116.bloodGroup = 'B-', p116.companyId = 'Niva Bupa', p116.policyNo = 'NB-663322';

MERGE (p117:Patient {id: 'PAT-117'})
SET p117.name = 'Amanpreet Singh', p117.dob = '1978-12-12', p117.gender = 'Male', p117.phone = '9820181920', p117.address = '33 Sector 35, Chandigarh', p117.bloodGroup = 'A-', p117.companyId = 'Bajaj Allianz', p117.policyNo = 'BA-882244';

MERGE (p118:Patient {id: 'PAT-118'})
SET p118.name = 'Sunaina Hegde', p118.dob = '2005-06-30', p118.gender = 'Female', p118.phone = '9820192021', p118.address = '9 Malleshwaram, Bangalore', p118.bloodGroup = 'O+', p118.companyId = 'HDFC ERGO', p118.policyNo = 'HE-337711';

MERGE (p119:Patient {id: 'PAT-119'})
SET p119.name = 'Kunal Bansal', p119.dob = '1980-08-04', p119.gender = 'Male', p119.phone = '9820202122', p119.address = '17 Mansarovar, Jaipur', p119.bloodGroup = 'B+', p119.companyId = 'Care Health', p119.policyNo = 'CH-229988';

MERGE (p120:Patient {id: 'PAT-120'})
SET p120.name = 'Shruti Mukherjee', p120.dob = '1993-04-22', p120.gender = 'Female', p120.phone = '9820212223', p120.address = '63 Ballygunge, Kolkata', p120.bloodGroup = 'AB+', p120.companyId = 'ICICI Lombard', p120.policyNo = 'IL-993355';

// ------------------------------------------------------------------------------
// 4. APPOINTMENTS, CLINICAL CONSULTATIONS & TREATMENTS
// ------------------------------------------------------------------------------

// Episode 1: Pediatrics - Childhood Asthma Exacerbation (PAT-111 & DOC-16)
MERGE (a211:Appointments {id: 'APT-211'})
SET a211.appointmentDate = date('2026-04-05'), a211.time = '09:30', a211.status = 'Completed';
MATCH (p:Patient {id: 'PAT-111'}), (d:Doctor {id: 'DOC-16'}), (a:Appointments {id: 'APT-211'})
MERGE (p)-[:HAS_APPOINTMENT]->(a)
MERGE (d)-[:ASSIGNED_TO]->(a);

MERGE (c311:Consultation {id: 'CON-311'})
SET c311.consultationDate = date('2026-04-05'), c311.diagnosis = 'Pediatric Bronchial Asthma Exacerbation', c311.notes = 'Wheezing and night cough after viral respiratory infection.', c311.reason = 'Pediatric Bronchial Asthma Exacerbation';
MERGE (t411:Treatment {id: 'TRT-411'})
SET t411.description = 'Pediatric Bronchial Asthma Exacerbation Protocol', t411.date = date('2026-04-05');
MATCH (a:Appointments {id: 'APT-211'}), (c:Consultation {id: 'CON-311'}) MERGE (a)-[:HAS_CONSULTATION]->(c);
MATCH (a:Appointments {id: 'APT-211'}), (t:Treatment {id: 'TRT-411'}) MERGE (a)-[:HAS_TREATMENT]->(t);

MERGE (rx511:Prescription {id: 'RX-511'})
SET rx511.treatmentType = 'Budesonide + Levosalbutamol Respules', rx511.dosage = 'Nebulization Twice Daily', rx511.durationDays = 7, rx511.status = 'Completed';
MATCH (t:Treatment {id: 'TRT-411'}), (rx:Prescription {id: 'RX-511'}) MERGE (t)-[:HAS_PRESCRIPTION]->(rx);

MERGE (lt611:LabTest {id: 'LAB-611'})
SET lt611.testType = 'Pediatric Spirometry & Fractional Exhaled Nitric Oxide', lt611.status = 'Abnormal', lt611.resultStatus = 'Abnormal', lt611.result = 'FeNO 48 ppb (Significant eosinophilic inflammation)', lt611.charge = 2800.0;
MATCH (t:Treatment {id: 'TRT-411'}), (lt:LabTest {id: 'LAB-611'}) MERGE (t)-[:HAS_LAB_TEST]->(lt);

// Episode 2: Oncology - Early Stage Breast Carcinoma Evaluation (PAT-112 & DOC-14)
MERGE (a212:Appointments {id: 'APT-212'})
SET a212.appointmentDate = date('2026-04-06'), a212.time = '10:45', a212.status = 'Completed';
MATCH (p:Patient {id: 'PAT-112'}), (d:Doctor {id: 'DOC-14'}), (a:Appointments {id: 'APT-212'})
MERGE (p)-[:HAS_APPOINTMENT]->(a)
MERGE (d)-[:ASSIGNED_TO]->(a);

MERGE (c312:Consultation {id: 'CON-312'})
SET c312.consultationDate = date('2026-04-06'), c312.diagnosis = 'Invasive Ductal Carcinoma (Stage IIA)', c312.notes = 'Palpable painless lump in upper outer quadrant of left breast.', c312.reason = 'Invasive Ductal Carcinoma (Stage IIA)';
MERGE (t412:Treatment {id: 'TRT-412'})
SET t412.description = 'Oncology Neoadjuvant Chemotherapy & Surgical Workup', t412.date = date('2026-04-06');
MATCH (a:Appointments {id: 'APT-212'}), (c:Consultation {id: 'CON-312'}) MERGE (a)-[:HAS_CONSULTATION]->(c);
MATCH (a:Appointments {id: 'APT-212'}), (t:Treatment {id: 'TRT-412'}) MERGE (a)-[:HAS_TREATMENT]->(t);

MERGE (rx512:Prescription {id: 'RX-512'})
SET rx512.treatmentType = 'Doxorubicin + Cyclophosphamide (AC Regimen)', rx512.dosage = 'Day 1 of 21-day cycle IV infusion', rx512.durationDays = 21, rx512.status = 'Active';
MATCH (t:Treatment {id: 'TRT-412'}), (rx:Prescription {id: 'RX-512'}) MERGE (t)-[:HAS_PRESCRIPTION]->(rx);

MERGE (lt612:LabTest {id: 'LAB-612'})
SET lt612.testType = 'Core Needle Biopsy & IHC (ER/PR/HER2)', lt612.status = 'Abnormal', lt612.resultStatus = 'Abnormal', lt612.result = 'ER positive (80%), PR positive (60%), HER2 Neu Negative (Score 1+)', lt612.charge = 11500.0;
MATCH (t:Treatment {id: 'TRT-412'}), (lt:LabTest {id: 'LAB-612'}) MERGE (t)-[:HAS_LAB_TEST]->(lt);

// Episode 3: Gastroenterology - Non-Alcoholic Steatohepatitis (PAT-113 & DOC-20)
MERGE (a213:Appointments {id: 'APT-213'})
SET a213.appointmentDate = date('2026-04-08'), a213.time = '11:15', a213.status = 'Completed';
MATCH (p:Patient {id: 'PAT-113'}), (d:Doctor {id: 'DOC-20'}), (a:Appointments {id: 'APT-213'})
MERGE (p)-[:HAS_APPOINTMENT]->(a)
MERGE (d)-[:ASSIGNED_TO]->(a);

MERGE (c313:Consultation {id: 'CON-313'})
SET c313.consultationDate = date('2026-04-08'), c313.diagnosis = 'Non-Alcoholic Steatohepatitis (NASH Grade 2)', c313.notes = 'Persistent right upper quadrant discomfort, elevated transaminases.', c313.reason = 'Non-Alcoholic Steatohepatitis (NASH Grade 2)';
MERGE (t413:Treatment {id: 'TRT-413'})
SET t413.description = 'Hepatoprotective and Metabolic Lifestyle Protocol', t413.date = date('2026-04-08');
MATCH (a:Appointments {id: 'APT-213'}), (c:Consultation {id: 'CON-313'}) MERGE (a)-[:HAS_CONSULTATION]->(c);
MATCH (a:Appointments {id: 'APT-213'}), (t:Treatment {id: 'TRT-413'}) MERGE (a)-[:HAS_TREATMENT]->(t);

MERGE (rx513:Prescription {id: 'RX-513'})
SET rx513.treatmentType = 'Ursodeoxycholic Acid 300mg + Saroglitazar 4mg', rx513.dosage = 'Once Daily after dinner', rx513.durationDays = 90, rx513.status = 'Active';
MATCH (t:Treatment {id: 'TRT-413'}), (rx:Prescription {id: 'RX-513'}) MERGE (t)-[:HAS_PRESCRIPTION]->(rx);

MERGE (lt613:LabTest {id: 'LAB-613'})
SET lt613.testType = 'Liver FibroScan & Comprehensive LFT', lt613.status = 'Abnormal', lt613.resultStatus = 'Abnormal', lt613.result = 'Liver stiffness 8.4 kPa (F2 moderate fibrosis), ALT 92 U/L', lt613.charge = 5200.0;
MATCH (t:Treatment {id: 'TRT-413'}), (lt:LabTest {id: 'LAB-613'}) MERGE (t)-[:HAS_LAB_TEST]->(lt);

// Episode 4: Dermatology - Chronic Severe Plaque Psoriasis (PAT-114 & DOC-18)
MERGE (a214:Appointments {id: 'APT-214'})
SET a214.appointmentDate = date('2026-04-10'), a214.time = '14:30', a214.status = 'Completed';
MATCH (p:Patient {id: 'PAT-114'}), (d:Doctor {id: 'DOC-18'}), (a:Appointments {id: 'APT-214'})
MERGE (p)-[:HAS_APPOINTMENT]->(a)
MERGE (d)-[:ASSIGNED_TO]->(a);

MERGE (c314:Consultation {id: 'CON-314'})
SET c314.consultationDate = date('2026-04-10'), c314.diagnosis = 'Chronic Plaque Psoriasis (PASI 14.2)', c314.notes = 'Erythematous scaly plaques on extensor surfaces of elbows, knees and scalp.', c314.reason = 'Chronic Plaque Psoriasis (PASI 14.2)';
MERGE (t414:Treatment {id: 'TRT-414'})
SET t414.description = 'Targeted Biologic Therapy & Topical Keratolytic Protocol', t414.date = date('2026-04-10');
MATCH (a:Appointments {id: 'APT-214'}), (c:Consultation {id: 'CON-314'}) MERGE (a)-[:HAS_CONSULTATION]->(c);
MATCH (a:Appointments {id: 'APT-214'}), (t:Treatment {id: 'TRT-414'}) MERGE (a)-[:HAS_TREATMENT]->(t);

MERGE (rx514:Prescription {id: 'RX-514'})
SET rx514.treatmentType = 'Secukinumab 300mg Subcutaneous Injection', rx514.dosage = 'Weekly for 4 weeks then monthly maintenance', rx514.durationDays = 60, rx514.status = 'Active';
MATCH (t:Treatment {id: 'TRT-414'}), (rx:Prescription {id: 'RX-514'}) MERGE (t)-[:HAS_PRESCRIPTION]->(rx);

MERGE (lt614:LabTest {id: 'LAB-614'})
SET lt614.testType = 'Quantiferon TB Gold & Hepatitis Viral Screen', lt614.status = 'Normal', lt614.resultStatus = 'Normal', lt614.result = 'Negative for latent infections, safe for biologic initiation', lt614.charge = 3600.0;
MATCH (t:Treatment {id: 'TRT-414'}), (lt:LabTest {id: 'LAB-614'}) MERGE (t)-[:HAS_LAB_TEST]->(lt);

// Episode 5: Nephrology - Chronic Kidney Disease Stage 3b (PAT-115 & DOC-22)
MERGE (a215:Appointments {id: 'APT-215'})
SET a215.appointmentDate = date('2026-04-12'), a215.time = '10:00', a215.status = 'Completed';
MATCH (p:Patient {id: 'PAT-115'}), (d:Doctor {id: 'DOC-22'}), (a:Appointments {id: 'APT-215'})
MERGE (p)-[:HAS_APPOINTMENT]->(a)
MERGE (d)-[:ASSIGNED_TO]->(a);

MERGE (c315:Consultation {id: 'CON-315'})
SET c315.consultationDate = date('2026-04-12'), c315.diagnosis = 'Hypertensive Nephrosclerosis (CKD Stage 3b)', c315.notes = 'Progressive decline in eGFR, nocturia, and persistent microalbuminuria.', c315.reason = 'Hypertensive Nephrosclerosis (CKD Stage 3b)';
MERGE (t415:Treatment {id: 'TRT-415'})
SET t415.description = 'Renoprotective SGLT2i & ACE-I Stabilization Protocol', t415.date = date('2026-04-12');
MATCH (a:Appointments {id: 'APT-215'}), (c:Consultation {id: 'CON-315'}) MERGE (a)-[:HAS_CONSULTATION]->(c);
MATCH (a:Appointments {id: 'APT-215'}), (t:Treatment {id: 'TRT-415'}) MERGE (a)-[:HAS_TREATMENT]->(t);

MERGE (rx515:Prescription {id: 'RX-515'})
SET rx515.treatmentType = 'Dapagliflozin 10mg + Telmisartan 40mg', rx515.dosage = 'Once Daily in Morning', rx515.durationDays = 90, rx515.status = 'Active';
MATCH (t:Treatment {id: 'TRT-415'}), (rx:Prescription {id: 'RX-515'}) MERGE (t)-[:HAS_PRESCRIPTION]->(rx);

MERGE (lt615:LabTest {id: 'LAB-615'})
SET lt615.testType = 'Serum Creatinine, eGFR & Urine Albumin/Creatinine Ratio (uACR)', lt615.status = 'Abnormal', lt615.resultStatus = 'Abnormal', lt615.result = 'Serum Creatinine 2.1 mg/dL, eGFR 38 mL/min/1.73m2, uACR 280 mg/g', lt615.charge = 2100.0;
MATCH (t:Treatment {id: 'TRT-415'}), (lt:LabTest {id: 'LAB-615'}) MERGE (t)-[:HAS_LAB_TEST]->(lt);

// Episode 6: Pulmonology - Chronic Obstructive Pulmonary Disease (PAT-117 & DOC-25)
MERGE (a216:Appointments {id: 'APT-216'})
SET a216.appointmentDate = date('2026-04-14'), a216.time = '16:00', a216.status = 'Completed';
MATCH (p:Patient {id: 'PAT-117'}), (d:Doctor {id: 'DOC-25'}), (a:Appointments {id: 'APT-216'})
MERGE (p)-[:HAS_APPOINTMENT]->(a)
MERGE (d)-[:ASSIGNED_TO]->(a);

MERGE (c316:Consultation {id: 'CON-316'})
SET c316.consultationDate = date('2026-04-14'), c316.diagnosis = 'COPD GOLD Stage 2 (Moderate Obstruction)', c316.notes = 'Exertional dyspnea with 20 pack-year smoking history.', c316.reason = 'COPD GOLD Stage 2 (Moderate Obstruction)';
MERGE (t416:Treatment {id: 'TRT-416'})
SET t416.description = 'Dual Bronchodilator Maintenance & Pulmonary Rehabilitation', t416.date = date('2026-04-14');
MATCH (a:Appointments {id: 'APT-216'}), (c:Consultation {id: 'CON-316'}) MERGE (a)-[:HAS_CONSULTATION]->(c);
MATCH (a:Appointments {id: 'APT-216'}), (t:Treatment {id: 'TRT-416'}) MERGE (a)-[:HAS_TREATMENT]->(t);

MERGE (rx516:Prescription {id: 'RX-516'})
SET rx516.treatmentType = 'Tiotropium 18mcg + Formoterol Inhaler', rx516.dosage = 'Two puffs every 12 hours with DPI device', rx516.durationDays = 60, rx516.status = 'Active';
MATCH (t:Treatment {id: 'TRT-416'}), (rx:Prescription {id: 'RX-516'}) MERGE (t)-[:HAS_PRESCRIPTION]->(rx);

MERGE (lt616:LabTest {id: 'LAB-616'})
SET lt616.testType = 'Post-Bronchodilator Spirometry & DLCO', lt616.status = 'Abnormal', lt616.resultStatus = 'Abnormal', lt616.result = 'FEV1/FVC 0.62, FEV1 64% predicted (Persistent airflow limitation)', lt616.charge = 3400.0;
MATCH (t:Treatment {id: 'TRT-416'}), (lt:LabTest {id: 'LAB-616'}) MERGE (t)-[:HAS_LAB_TEST]->(lt);

// Episode 7: Scheduled & Future Follow-up Appointments
MERGE (a217:Appointments {id: 'APT-217'})
SET a217.appointmentDate = date('2026-04-22'), a217.time = '11:00', a217.status = 'Scheduled';
MATCH (p:Patient {id: 'PAT-118'}), (d:Doctor {id: 'DOC-13'}), (a:Appointments {id: 'APT-217'})
MERGE (p)-[:HAS_APPOINTMENT]->(a)
MERGE (d)-[:ASSIGNED_TO]->(a);

MERGE (a218:Appointments {id: 'APT-218'})
SET a218.appointmentDate = date('2026-04-24'), a218.time = '15:15', a218.status = 'Scheduled';
MATCH (p:Patient {id: 'PAT-119'}), (d:Doctor {id: 'DOC-24'}), (a:Appointments {id: 'APT-218'})
MERGE (p)-[:HAS_APPOINTMENT]->(a)
MERGE (d)-[:ASSIGNED_TO]->(a);

// ------------------------------------------------------------------------------
// 5. BILLING & INSURANCE CLAIMS
// ------------------------------------------------------------------------------

// Bill 1: Pediatrics Asthma Episode (PAT-111, TRT-411)
MERGE (b711:Billing {id: 'BIL-711'})
SET b711.amount = 6200.0,
    b711.consultationCharge = 1200.0,
    b711.labCharge = 2800.0,
    b711.pharmacyCharge = 1500.0,
    b711.roomCharge = 700.0,
    b711.otherCharge = 0.0,
    b711.paymentMode = 'Insurance',
    b711.paymentStatus = 'Paid',
    b711.billingDate = date('2026-04-05');
MATCH (p:Patient {id: 'PAT-111'}), (t:Treatment {id: 'TRT-411'}), (b:Billing {id: 'BIL-711'})
MERGE (p)-[:HAS_BILL]->(b)
MERGE (t)-[:HAS_BILL]->(b);

MERGE (cl811:InsuranceClaim {id: 'CLM-811'})
SET cl811.companyId = 'HDFC ERGO',
    cl811.claimAmount = 5500.0,
    cl811.approvedAmount = 5000.0,
    cl811.status = 'Approved';
MATCH (b:Billing {id: 'BIL-711'}), (p:Patient {id: 'PAT-111'}), (cl:InsuranceClaim {id: 'CLM-811'})
MERGE (b)-[:HAS_INSURANCE_CLAIM]->(cl)
MERGE (p)-[:HAS_INSURANCE_CLAIM]->(cl);

// Bill 2: Oncology Chemo & Biopsy (PAT-112, TRT-412)
MERGE (b712:Billing {id: 'BIL-712'})
SET b712.amount = 48500.0,
    b712.consultationCharge = 3000.0,
    b712.labCharge = 11500.0,
    b712.pharmacyCharge = 18000.0,
    b712.roomCharge = 16000.0,
    b712.otherCharge = 0.0,
    b712.paymentMode = 'Insurance',
    b712.paymentStatus = 'Paid',
    b712.billingDate = date('2026-04-06');
MATCH (p:Patient {id: 'PAT-112'}), (t:Treatment {id: 'TRT-412'}), (b:Billing {id: 'BIL-712'})
MERGE (p)-[:HAS_BILL]->(b)
MERGE (t)-[:HAS_BILL]->(b);

MERGE (cl812:InsuranceClaim {id: 'CLM-812'})
SET cl812.companyId = 'Star Health',
    cl812.claimAmount = 45000.0,
    cl812.approvedAmount = 41200.0,
    cl812.status = 'Approved';
MATCH (b:Billing {id: 'BIL-712'}), (p:Patient {id: 'PAT-112'}), (cl:InsuranceClaim {id: 'CLM-812'})
MERGE (b)-[:HAS_INSURANCE_CLAIM]->(cl)
MERGE (p)-[:HAS_INSURANCE_CLAIM]->(cl);

// Bill 3: Gastroenterology NASH Episode (PAT-113, TRT-413)
MERGE (b713:Billing {id: 'BIL-713'})
SET b713.amount = 8900.0,
    b713.consultationCharge = 1500.0,
    b713.labCharge = 5200.0,
    b713.pharmacyCharge = 2200.0,
    b713.roomCharge = 0.0,
    b713.otherCharge = 0.0,
    b713.paymentMode = 'Card',
    b713.paymentStatus = 'Paid',
    b713.billingDate = date('2026-04-08');
MATCH (p:Patient {id: 'PAT-113'}), (t:Treatment {id: 'TRT-413'}), (b:Billing {id: 'BIL-713'})
MERGE (p)-[:HAS_BILL]->(b)
MERGE (t)-[:HAS_BILL]->(b);

// Bill 4: Dermatology Biologic Therapy (PAT-114, TRT-414)
MERGE (b714:Billing {id: 'BIL-714'})
SET b714.amount = 34500.0,
    b714.consultationCharge = 1500.0,
    b714.labCharge = 3600.0,
    b714.pharmacyCharge = 29400.0,
    b714.roomCharge = 0.0,
    b714.otherCharge = 0.0,
    b714.paymentMode = 'Insurance',
    b714.paymentStatus = 'Pending',
    b714.billingDate = date('2026-04-10');
MATCH (p:Patient {id: 'PAT-114'}), (t:Treatment {id: 'TRT-414'}), (b:Billing {id: 'BIL-714'})
MERGE (p)-[:HAS_BILL]->(b)
MERGE (t)-[:HAS_BILL]->(b);

MERGE (cl814:InsuranceClaim {id: 'CLM-814'})
SET cl814.companyId = 'ICICI Lombard',
    cl814.claimAmount = 32000.0,
    cl814.approvedAmount = 0.0,
    cl814.status = 'Submitted';
MATCH (b:Billing {id: 'BIL-714'}), (p:Patient {id: 'PAT-114'}), (cl:InsuranceClaim {id: 'CLM-814'})
MERGE (b)-[:HAS_INSURANCE_CLAIM]->(cl)
MERGE (p)-[:HAS_INSURANCE_CLAIM]->(cl);

// Bill 5: Nephrology CKD Episode (PAT-115, TRT-415)
MERGE (b715:Billing {id: 'BIL-715'})
SET b715.amount = 6100.0,
    b715.consultationCharge = 1500.0,
    b715.labCharge = 2100.0,
    b715.pharmacyCharge = 2500.0,
    b715.roomCharge = 0.0,
    b715.otherCharge = 0.0,
    b715.paymentMode = 'UPI',
    b715.paymentStatus = 'Paid',
    b715.billingDate = date('2026-04-12');
MATCH (p:Patient {id: 'PAT-115'}), (t:Treatment {id: 'TRT-415'}), (b:Billing {id: 'BIL-715'})
MERGE (p)-[:HAS_BILL]->(b)
MERGE (t)-[:HAS_BILL]->(b);

// Bill 6: Pulmonology COPD Episode (PAT-117, TRT-416)
MERGE (b716:Billing {id: 'BIL-716'})
SET b716.amount = 7600.0,
    b716.consultationCharge = 1400.0,
    b716.labCharge = 3400.0,
    b716.pharmacyCharge = 2800.0,
    b716.roomCharge = 0.0,
    b716.otherCharge = 0.0,
    b716.paymentMode = 'Insurance',
    b716.paymentStatus = 'Paid',
    b716.billingDate = date('2026-04-14');
MATCH (p:Patient {id: 'PAT-117'}), (t:Treatment {id: 'TRT-416'}), (b:Billing {id: 'BIL-716'})
MERGE (p)-[:HAS_BILL]->(b)
MERGE (t)-[:HAS_BILL]->(b);

MERGE (cl816:InsuranceClaim {id: 'CLM-816'})
SET cl816.companyId = 'Bajaj Allianz',
    cl816.claimAmount = 6500.0,
    cl816.approvedAmount = 5800.0,
    cl816.status = 'Approved';
MATCH (b:Billing {id: 'BIL-716'}), (p:Patient {id: 'PAT-117'}), (cl:InsuranceClaim {id: 'CLM-816'})
MERGE (b)-[:HAS_INSURANCE_CLAIM]->(cl)
MERGE (p)-[:HAS_INSURANCE_CLAIM]->(cl);
