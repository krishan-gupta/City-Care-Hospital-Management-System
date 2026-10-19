"""
Schema Mapping for CityCare Hospital Management System.
Configured based on live Neo4j AuraDB database introspection.
The real database labels, relationship types, and properties are mapped here.
"""

# Node Labels in the Real Database
LABEL_PATIENT = "Patient"
LABEL_DEPARTMENT = "Department"
LABEL_EMPLOYEE = "Employee"
LABEL_DOCTOR = "Doctor"
LABEL_APPOINTMENT = "Appointments"  # Real DB uses 'Appointments'
LABEL_CONSULTATION = "Consultation"
LABEL_TREATMENT = "Treatment"
LABEL_PRESCRIPTION = "Prescription"
LABEL_LAB_TEST = "LabTest"
LABEL_BILL = "Billing"              # Real DB uses 'Billing'
LABEL_INSURANCE_CLAIM = "InsuranceClaim"

# Relationship Types in the Real Database
REL_BELONGS_TO = "BELONGS_TO"             # Doctor -> Department
REL_HAS_APPOINTMENT = "HAS_APPOINTMENT"   # Patient -> Appointments
REL_ASSIGNED_TO = "ASSIGNED_TO"           # Doctor -> Appointments
REL_HAS_CONSULTATION = "HAS_CONSULTATION" # Appointments -> Consultation
REL_HAS_TREATMENT = "HAS_TREATMENT"       # Appointments -> Treatment
REL_HAS_PRESCRIPTION = "HAS_PRESCRIPTION" # Treatment -> Prescription
REL_HAS_LAB_TEST = "HAS_LAB_TEST"         # Treatment -> LabTest
REL_HAS_BILL = "HAS_BILL"                 # Treatment -> Billing, Patient -> Billing
REL_HAS_CLAIM = "HAS_INSURANCE_CLAIM"     # Billing -> InsuranceClaim, Patient -> InsuranceClaim

# Primary Keys (all nodes use 'id' in the real database)
KEY_PATIENT = "id"
KEY_DEPARTMENT = "id"
KEY_EMPLOYEE = "id"
KEY_DOCTOR = "id"
KEY_APPOINTMENT = "id"
KEY_CONSULTATION = "id"
KEY_TREATMENT = "id"
KEY_PRESCRIPTION = "id"
KEY_LAB_TEST = "id"
KEY_BILL = "id"
KEY_INSURANCE_CLAIM = "id"
