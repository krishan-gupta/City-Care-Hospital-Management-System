from typing import List, Optional
from pydantic import BaseModel, Field

# --- Patient Models ---
class PatientCreate(BaseModel):
    name: str = Field(..., min_length=1)
    dob: str = Field(..., description="YYYY-MM-DD")
    gender: str = Field(..., description="Male, Female, Other")
    phone: str = Field(..., min_length=1)
    address: Optional[str] = ""
    bloodGroup: Optional[str] = ""
    companyId: Optional[str] = None
    policyNo: Optional[str] = None

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    bloodGroup: Optional[str] = None

# --- Appointment Models ---
class AppointmentCreate(BaseModel):
    patientId: str
    doctorId: str
    date: str = Field(..., description="YYYY-MM-DD")
    time: str = Field(..., description="HH:MM")

class AppointmentUpdate(BaseModel):
    date: Optional[str] = None
    time: Optional[str] = None
    status: Optional[str] = Field(None, description="Scheduled, Completed, Cancelled")

# --- Consultation Models ---
class MedicineItem(BaseModel):
    medId: str
    dosage: str
    durationDays: int = Field(..., gt=0)

class LabTestItem(BaseModel):
    testType: str = Field(..., description="Blood, MRI, X-Ray, ECG, CT, etc.")
    charge: float = Field(0.0, ge=0)
    technicianId: Optional[str] = None

class ConsultationCreate(BaseModel):
    appointmentId: str
    diagnosis: str
    notes: Optional[str] = ""
    medicines: Optional[List[MedicineItem]] = []
    labTests: Optional[List[LabTestItem]] = []

# --- Lab Test Models ---
class LabTestUpdate(BaseModel):
    result: str
    resultStatus: str = Field(..., description="Normal, Abnormal, Pending")

# --- Bill & Claim Models ---
class ClaimCreate(BaseModel):
    companyId: str
    claimAmount: float = Field(..., gt=0)

class ClaimUpdate(BaseModel):
    status: str = Field(..., description="Submitted, Approved, Rejected, Pending")
    approvedAmount: float = Field(..., ge=0)

class BillCreate(BaseModel):
    consultationId: str
    consultationCharge: float = Field(0.0, ge=0)
    labCharge: float = Field(0.0, ge=0)
    pharmacyCharge: float = Field(0.0, ge=0)
    roomCharge: float = Field(0.0, ge=0)
    otherCharge: float = Field(0.0, ge=0)
    paymentMode: str = Field("Direct", description="Direct, Insurance")
    paymentStatus: str = Field("Paid", description="Paid, Pending")
    claim: Optional[ClaimCreate] = None

class BillUpdate(BaseModel):
    consultationCharge: Optional[float] = Field(None, ge=0)
    labCharge: Optional[float] = Field(None, ge=0)
    pharmacyCharge: Optional[float] = Field(None, ge=0)
    roomCharge: Optional[float] = Field(None, ge=0)
    otherCharge: Optional[float] = Field(None, ge=0)
    paymentMode: Optional[str] = None
    paymentStatus: Optional[str] = None
