import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from db import run_query
from models import PatientCreate, PatientUpdate
import schema_map as sm

router = APIRouter(prefix="/patients", tags=["Patients"])

def gen_id(prefix: str = "P") -> str:
    return f"{prefix}{uuid.uuid4().hex[:5].upper()}"

@router.get("")
def list_patients(
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
):
    skip = (page - 1) * size
    search_term = f"(?i).*{search}.*" if search else ".*"

    count_cypher = f"""
    MATCH (p:{sm.LABEL_PATIENT})
    WHERE (p.firstName + ' ' + p.lastName) =~ $search
       OR toString(p.contactNumber) =~ $search
       OR p.{sm.KEY_PATIENT} =~ $search
    RETURN count(p) AS total
    """
    count_res = run_query(count_cypher, {"search": search_term})
    total = count_res[0]["total"] if count_res else 0

    cypher = f"""
    MATCH (p:{sm.LABEL_PATIENT})
    WHERE (p.firstName + ' ' + p.lastName) =~ $search
       OR toString(p.contactNumber) =~ $search
       OR p.{sm.KEY_PATIENT} =~ $search
    RETURN p.{sm.KEY_PATIENT} AS patientId,
           coalesce(p.name, p.firstName + ' ' + p.lastName) AS name,
           p.firstName AS firstName,
           p.lastName AS lastName,
           p.dateOfBirth AS dob,
           CASE
             WHEN p.dateOfBirth IS NOT NULL THEN duration.between(date(p.dateOfBirth), date()).years
             ELSE null
           END AS age,
           p.gender AS gender,
           toString(p.contactNumber) AS phone,
           p.address AS address,
           p.insuranceProvider AS insuranceCompany,
           p.insuranceNumber AS policyNo
    ORDER BY p.{sm.KEY_PATIENT} ASC
    SKIP $skip LIMIT $size
    """
    records = run_query(cypher, {"search": search_term, "skip": skip, "size": size})
    return {"items": records, "total": total, "page": page, "size": size}


@router.get("/{patient_id}")
def get_patient(patient_id: str):
    cypher = f"""
    MATCH (p:{sm.LABEL_PATIENT} {{{sm.KEY_PATIENT}: $patient_id}})
    RETURN p.{sm.KEY_PATIENT} AS patientId,
           coalesce(p.name, p.firstName + ' ' + p.lastName) AS name,
           p.firstName AS firstName,
           p.lastName AS lastName,
           p.dateOfBirth AS dob,
           CASE
             WHEN p.dateOfBirth IS NOT NULL THEN duration.between(date(p.dateOfBirth), date()).years
             ELSE null
           END AS age,
           p.gender AS gender,
           toString(p.contactNumber) AS phone,
           p.address AS address,
           p.insuranceProvider AS insuranceCompany,
           p.insuranceNumber AS policyNo
    """
    records = run_query(cypher, {"patient_id": patient_id})
    if not records:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
    return records[0]


@router.post("", status_code=201)
def create_patient(data: PatientCreate):
    patient_id = gen_id("P")
    names = data.name.strip().split(" ", 1)
    first_name = names[0]
    last_name = names[1] if len(names) > 1 else ""

    cypher = f"""
    CREATE (p:{sm.LABEL_PATIENT} {{
        {sm.KEY_PATIENT}: $patient_id,
        firstName: $first_name,
        lastName: $last_name,
        name: $name,
        dateOfBirth: $dob,
        dob: $dob,
        gender: $gender,
        contactNumber: $phone,
        phone: $phone,
        address: $address,
        bloodGroup: $bloodGroup,
        insuranceProvider: $insurance_provider,
        insuranceNumber: $insurance_number
    }})
    RETURN p.{sm.KEY_PATIENT} AS patientId
    """
    params = {
        "patient_id": patient_id,
        "first_name": first_name,
        "last_name": last_name,
        "name": data.name,
        "dob": data.dob,
        "gender": data.gender,
        "phone": data.phone,
        "address": data.address or "",
        "bloodGroup": data.bloodGroup or "",
        "insurance_provider": data.companyId or "",
        "insurance_number": data.policyNo or ""
    }
    run_query(cypher, params)
    return get_patient(patient_id)


@router.put("/{patient_id}")
def update_patient(patient_id: str, data: PatientUpdate):
    check = run_query(f"MATCH (p:{sm.LABEL_PATIENT} {{{sm.KEY_PATIENT}: $id}}) RETURN p", {"id": patient_id})
    if not check:
        raise HTTPException(status_code=404, detail="Patient not found")

    updates = []
    params = {"patient_id": patient_id}
    if data.name is not None:
        names = data.name.strip().split(" ", 1)
        updates.extend(["p.name = $name", "p.firstName = $first_name", "p.lastName = $last_name"])
        params["name"] = data.name
        params["first_name"] = names[0]
        params["last_name"] = names[1] if len(names) > 1 else ""
    if data.dob is not None:
        updates.extend(["p.dob = $dob", "p.dateOfBirth = $dob"])
        params["dob"] = data.dob
    if data.gender is not None:
        updates.append("p.gender = $gender")
        params["gender"] = data.gender
    if data.phone is not None:
        updates.extend(["p.phone = $phone", "p.contactNumber = $phone"])
        params["phone"] = data.phone
    if data.address is not None:
        updates.append("p.address = $address")
        params["address"] = data.address
    if data.bloodGroup is not None:
        updates.append("p.bloodGroup = $bloodGroup")
        params["bloodGroup"] = data.bloodGroup

    if updates:
        cypher = f"""
        MATCH (p:{sm.LABEL_PATIENT} {{{sm.KEY_PATIENT}: $patient_id}})
        SET {", ".join(updates)}
        RETURN p.{sm.KEY_PATIENT} AS patientId
        """
        run_query(cypher, params)

    return get_patient(patient_id)


@router.delete("/{patient_id}")
def delete_patient(patient_id: str):
    check = run_query(f"MATCH (p:{sm.LABEL_PATIENT} {{{sm.KEY_PATIENT}: $id}}) RETURN p", {"id": patient_id})
    if not check:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Cascade delete owned nodes only (Appointment, Consultation, Treatment, Prescription, LabTest, Billing, Claim)
    cypher = f"""
    MATCH (p:{sm.LABEL_PATIENT} {{{sm.KEY_PATIENT}: $id}})
    OPTIONAL MATCH (p)-[:{sm.REL_HAS_APPOINTMENT}]->(a:{sm.LABEL_APPOINTMENT})
    OPTIONAL MATCH (a)-[:{sm.REL_HAS_CONSULTATION}]->(c:{sm.LABEL_CONSULTATION})
    OPTIONAL MATCH (a)-[:{sm.REL_HAS_TREATMENT}]->(t:{sm.LABEL_TREATMENT})
    OPTIONAL MATCH (t)-[:{sm.REL_HAS_PRESCRIPTION}]->(rx:{sm.LABEL_PRESCRIPTION})
    OPTIONAL MATCH (t)-[:{sm.REL_HAS_LAB_TEST}]->(lt:{sm.LABEL_LAB_TEST})
    OPTIONAL MATCH (p)-[:{sm.REL_HAS_BILL}]->(b:{sm.LABEL_BILL})
    OPTIONAL MATCH (b)-[:{sm.REL_HAS_CLAIM}]->(cl:{sm.LABEL_INSURANCE_CLAIM})
    DETACH DELETE cl, b, lt, rx, t, c, a, p
    """
    run_query(cypher, {"id": patient_id})
    return {"status": "success", "message": f"Patient {patient_id} and related records deleted."}


@router.get("/{patient_id}/journey")
def get_patient_journey(patient_id: str):
    check = run_query(f"MATCH (p:{sm.LABEL_PATIENT} {{{sm.KEY_PATIENT}: $id}}) RETURN p", {"id": patient_id})
    if not check:
        raise HTTPException(status_code=404, detail="Patient not found")

    cypher = f"""
    MATCH (p:{sm.LABEL_PATIENT} {{{sm.KEY_PATIENT}: $id}})
    OPTIONAL MATCH (p)-[r_app:{sm.REL_HAS_APPOINTMENT}]->(a:{sm.LABEL_APPOINTMENT})
    OPTIONAL MATCH (d:{sm.LABEL_DOCTOR})-[r_doc:{sm.REL_ASSIGNED_TO}]->(a)
    OPTIONAL MATCH (d)-[r_dep:{sm.REL_BELONGS_TO}]->(dep:{sm.LABEL_DEPARTMENT})
    OPTIONAL MATCH (a)-[r_con:{sm.REL_HAS_CONSULTATION}]->(c:{sm.LABEL_CONSULTATION})
    OPTIONAL MATCH (a)-[r_trm:{sm.REL_HAS_TREATMENT}]->(t:{sm.LABEL_TREATMENT})
    OPTIONAL MATCH (t)-[r_rx:{sm.REL_HAS_PRESCRIPTION}]->(rx:{sm.LABEL_PRESCRIPTION})
    OPTIONAL MATCH (t)-[r_lab:{sm.REL_HAS_LAB_TEST}]->(lt:{sm.LABEL_LAB_TEST})
    OPTIONAL MATCH (p)-[r_bill:{sm.REL_HAS_BILL}]->(b:{sm.LABEL_BILL})
    OPTIONAL MATCH (b)-[r_claim:{sm.REL_HAS_CLAIM}]->(cl:{sm.LABEL_INSURANCE_CLAIM})
    RETURN p, a, d, dep, c, t, rx, lt, b, cl,
           r_app, r_doc, r_dep, r_con, r_trm, r_rx, r_lab, r_bill, r_claim
    """
    records = run_query(cypher, {"id": patient_id})

    nodes_map = {}
    links = []
    link_keys = set()

    def add_node(item, label, id_field, name_display):
        if not item:
            return None
        node_id = str(item.get(id_field) or item.get("_element_id") or id(item))
        if node_id not in nodes_map:
            props = {k: v for k, v in item.items() if not k.startswith("_")}
            nodes_map[node_id] = {
                "id": node_id,
                "label": label,
                "name": str(name_display),
                "properties": props
            }
        return node_id

    def add_link(source_id, target_id, rel_type):
        if not source_id or not target_id:
            return
        key = (str(source_id), str(target_id), rel_type)
        if key not in link_keys:
            link_keys.add(key)
            links.append({
                "source": str(source_id),
                "target": str(target_id),
                "type": rel_type
            })

    for row in records:
        p = row.get("p")
        if p:
            p_name = p.get("name") or f"{p.get('firstName', '')} {p.get('lastName', '')}".strip() or p.get("id")
            p_id = add_node(p, "Patient", sm.KEY_PATIENT, p_name)

            a = row.get("a")
            if a:
                a_name = f"Appt {a.get('id')} ({str(a.get('appointmentDate', ''))[:10]})"
                a_id = add_node(a, "Appointment", sm.KEY_APPOINTMENT, a_name)
                add_link(p_id, a_id, sm.REL_HAS_APPOINTMENT)

                d = row.get("d")
                if d:
                    d_name = f"Dr. {d.get('firstName', '')} {d.get('lastName', '')} ({d.get('specialization', '')})"
                    d_id = add_node(d, "Doctor", sm.KEY_DOCTOR, d_name)
                    add_link(d_id, a_id, sm.REL_ASSIGNED_TO)

                    dep = row.get("dep")
                    if dep:
                        dep_id = add_node(dep, "Department", sm.KEY_DEPARTMENT, dep.get("name"))
                        add_link(d_id, dep_id, sm.REL_BELONGS_TO)

                c = row.get("c")
                if c:
                    c_name = f"Consult: {c.get('reason', 'Consultation')}"
                    c_id = add_node(c, "Consultation", sm.KEY_CONSULTATION, c_name)
                    add_link(a_id, c_id, sm.REL_HAS_CONSULTATION)

                t = row.get("t")
                if t:
                    t_name = f"Treatment: {t.get('treatmentType', 'Therapy')}"
                    t_id = add_node(t, "Treatment", sm.KEY_TREATMENT, t_name)
                    add_link(a_id, t_id, sm.REL_HAS_TREATMENT)

                    rx = row.get("rx")
                    if rx:
                        rx_name = f"Rx: {rx.get('treatmentType', 'Medication')}"
                        rx_id = add_node(rx, "Prescription", sm.KEY_PRESCRIPTION, rx_name)
                        add_link(t_id, rx_id, sm.REL_HAS_PRESCRIPTION)

                    lt = row.get("lt")
                    if lt:
                        lt_name = f"Lab: {lt.get('testType', 'Lab Test')}"
                        lt_id = add_node(lt, "LabTest", sm.KEY_LAB_TEST, lt_name)
                        add_link(t_id, lt_id, sm.REL_HAS_LAB_TEST)

            b = row.get("b")
            if b:
                b_name = f"Bill: ${b.get('amount', 0)}"
                b_id = add_node(b, "Bill", sm.KEY_BILL, b_name)
                add_link(p_id, b_id, sm.REL_HAS_BILL)

                cl = row.get("cl")
                if cl:
                    cl_name = f"Claim: ${cl.get('claimAmount', 0)} ({cl.get('status', '')})"
                    cl_id = add_node(cl, "InsuranceClaim", sm.KEY_INSURANCE_CLAIM, cl_name)
                    add_link(b_id, cl_id, sm.REL_HAS_CLAIM)

    return {"nodes": list(nodes_map.values()), "links": links}
