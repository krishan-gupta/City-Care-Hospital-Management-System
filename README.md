# CityCare Hospital Management System (Neo4j)

**BACSE202 Database Systems — Digital Assignment 3**  
Full-stack Graph Database Application: **React Frontend + FastAPI Backend + Neo4j AuraDB**.

---

## 🏥 Architecture Overview

- **Frontend**: React (Vite 8), Tailwind CSS, React Router, Recharts, `react-force-graph-2d`, Axios, Lucide Icons.
- **Backend**: Python 3.11+, FastAPI, Official `neo4j` Python Driver, Pydantic, Uvicorn, `python-dotenv`.
- **Database**: Neo4j Graph Database (AuraDB cloud instance).
- **Schema Mapping**: Centralized [schema_map.py](file:///c:/Users/LENOVO/Desktop/Codes/City%20Care%20Hospital%20Management%20System/backend/schema_map.py) ensuring 100% synchronization with live AuraDB labels, relationships, and property keys.

---

## 🚀 Prerequisites

1. **Python 3.11+** installed
2. **Node.js 18+** & **npm** installed
3. An active **Neo4j database instance** (AuraDB or local)

---

## ⚙️ Environment Configuration

### 1. Backend (`backend/.env`)

Copy the example file and configure credentials:
```bash
cp backend/.env.example backend/.env
```

Ensure `backend/.env` contains your active database credentials:
```env
NEO4J_URI=neo4j+s://17fe6bc7.databases.neo4j.io
NEO4J_USER=17fe6bc7
NEO4J_PASSWORD=<your_password>
FRONTEND_ORIGIN=http://localhost:5173
```

### 2. Frontend (`frontend/.env`)

Copy the example file:
```bash
cp frontend/.env.example frontend/.env
```

Ensure `frontend/.env` contains:
```env
VITE_API_URL=http://localhost:8000/api
```

---

## 🏃 Running the Application

### Step 1: Start the FastAPI Backend

Open a terminal in the root directory:
```powershell
# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Navigate to backend directory and start Uvicorn
cd backend
uvicorn main:app --reload --port 8000
```
- Interactive Swagger API Documentation: **[http://localhost:8000/docs](http://localhost:8000/docs)**
- Health check: **[http://localhost:8000/api/health](http://localhost:8000/api/health)**

### Step 2: Start the React Frontend

Open a second terminal:
```powershell
cd frontend
npm run dev
```
- Web Application: **[http://localhost:5173](http://localhost:5173)**

---

## 🖥️ Application Pages

| Page | Route | Description |
|---|---|---|
| **Dashboard** | `/` | Operational KPIs, revenue by department chart, claim status pie chart, and doctor workload benchmarking. |
| **Patients** | `/patients` | Searchable patient directory, derived age calculation, registration modal, editing, cascade deletion, and journey links. |
| **Patient Journey** | `/patients/:id/journey` | Interactive 2D force-directed knowledge graph with colored entity types, zoom/drag, and side inspection panel. |
| **Doctors & Depts** | `/doctors` | Department doctor rosters, specialty badges, contact details, and patient workload reach. |
| **Appointments** | `/appointments` | Filter by status/doctor/dept, schedule new appointments, reschedule, update status, and cascading delete. |
| **Consultations & Lab** | `/consultations` | Atomic single-transaction consultations with diagnosis, prescriptions, and lab tests; diagnostic result entry with abnormal alerts. |
| **Billing & Claims** | `/billing` | Itemized invoice generation, insurance claim status & approval updates, and full patient billing report table. |
| **Query Console** | `/queries` | Interactive console with all 11 required Cypher queries, syntax highlighting, parameter inputs, and live AuraDB datasets. |

---

## 🔍 Required Cypher Queries Tested & Available in Console

1. **`patient_journey`**: Traverses all connected nodes for a patient (`Appointment`, `Doctor`, `Department`, `Consultation`, `Treatment`, `Prescription`, `LabTest`, `Billing`, `InsuranceClaim`).
2. **`appointments_overview`**: Patient, doctor, department, date, and status sorted by most recent date.
3. **`consultations_with_prescriptions`**: Diagnosis and list of prescribed treatments.
4. **`patients_per_doctor`**: Distinct patient count per doctor sorted descending.
5. **`departments_more_than_two_doctors`**: Filtered departments employing more than 2 doctors.
6. **`bill_statistics`**: Hospital revenue aggregate metrics (`sum`, `avg`, `max`, `min`).
7. **`doctors_above_average_patients`**: Nested aggregation calculating doctors exceeding hospital-wide average patient load.
8. **`patients_bill_above_average`**: Nested aggregation identifying patients with cumulative billing higher than average.
9. **`doctors_above_department_average`**: Correlated subquery computing practitioners exceeding their department's workload benchmark.
10. **`patients_with_abnormal_lab`**: Correlated `EXISTS` subquery finding patients with abnormal lab test results.
11. **`patient_billing_report`**: Total bill, insurance claim, approved amount, and net patient payable.

---

## 👥 Viva Defense Topics

| Member | Focus Area | Key Concepts |
|---|---|---|
| **Member 1** | Graph Model & Cypher | Graph vs Relational, nodes vs foreign keys, labels, relationship directions, correlated subqueries (`CALL { ... }`), `EXISTS`, nested aggregations. |
| **Member 2** | Backend & Database Transactions | Official `neo4j` driver, parameterized queries (`$id`), transactional units of work (`session.execute_write`), schema mapping layer, cascading deletes. |
| **Member 3** | Frontend & Visualization | React Component Architecture, `react-force-graph-2d` physics canvas, Recharts data visualizers, Axios interceptors, responsive Tailwind CSS design. |
