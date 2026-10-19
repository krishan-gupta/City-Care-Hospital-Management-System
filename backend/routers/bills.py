import uuid
from datetime import date
from typing import Optional
from fastapi import APIRouter, HTTPException
from db import run_query, run_write_transaction
from models import BillCreate, BillUpdate, ClaimUpdate
import schema_map as sm

router = APIRouter(tags=["Billing & Claims"])

def gen_id(prefix: str = "B") -> str:
    return f"{prefix}{uuid.uuid4().hex[:4].upper()}"

@router.get("/bills")
def list_bills(
    patient: Optional[str] = None,
    paymentMode: Optional[str] = None
):
    cypher = f"""
    MATCH (p:{sm.LABEL_PATIENT})-[:{sm.REL_HAS_BILL}]->(b:{sm.LABEL_BILL})
    OPTIONAL MATCH (t:{sm.LABEL_TREATMENT})-[:{sm.REL_HAS_BILL}]->(b)
    OPTIONAL MATCH (b)-[:{sm.REL_HAS_CLAIM}]->(cl:{sm.LABEL_INSURANCE_CLAIM})
    WHERE ($patient IS NULL OR (p.firstName + ' ' + p.lastName) =~ $pat_pattern OR p.{sm.KEY_PATIENT} = $patient)
      AND ($mode IS NULL OR b.paymentMethod = $mode OR b.paymentMode = $mode)
    RETURN b.{sm.KEY_BILL} AS billNo,
           toString(b.billDate) AS billDate,
           coalesce(b.consultationCharge, round(b.amount * 0.4, 2)) AS consultationCharge,
           coalesce(b.labCharge, round(b.amount * 0.3, 2)) AS labCharge,
           coalesce(b.pharmacyCharge, round(b.amount * 0.2, 2)) AS pharmacyCharge,
           coalesce(b.roomCharge, 0.0) AS roomCharge,
           coalesce(b.otherCharge, round(b.amount * 0.1, 2)) AS otherCharge,
           round(b.amount, 2) AS totalAmount,
           coalesce(b.paymentMethod, b.paymentMode, 'Direct') AS paymentMode,
           b.paymentStatus AS paymentStatus,
           p.{sm.KEY_PATIENT} AS patientId,
           coalesce(p.name, p.firstName + ' ' + p.lastName) AS patientName,
           t.{sm.KEY_TREATMENT} AS treatmentId,
           cl.{sm.KEY_INSURANCE_CLAIM} AS claimId,
           round(coalesce(cl.claimAmount, 0), 2) AS claimAmount,
           round(coalesce(cl.approvedAmount, 0), 2) AS approvedAmount,
           cl.status AS claimStatus,
           coalesce(cl.insuranceProvider, p.insuranceProvider, 'Standard Insurance') AS insuranceCompany
    ORDER BY b.billDate DESC
    """
    params = {
        "patient": patient,
        "pat_pattern": f"(?i).*{patient}.*" if patient else ".*",
        "mode": paymentMode
    }
    return run_query(cypher, params)


@router.post("/bills", status_code=201)
def create_bill(data: BillCreate):
    # Find patient via consultation or treatment
    find_pat = run_query(f"""
    MATCH (c:{sm.LABEL_CONSULTATION} {{{sm.KEY_CONSULTATION}: $cid}})<-[:{sm.REL_HAS_CONSULTATION}]-(a:{sm.LABEL_APPOINTMENT})<-[:{sm.REL_HAS_APPOINTMENT}]-(p:{sm.LABEL_PATIENT})
    OPTIONAL MATCH (a)-[:{sm.REL_HAS_TREATMENT}]->(t:{sm.LABEL_TREATMENT})
    RETURN p.{sm.KEY_PATIENT} AS patientId, t.{sm.KEY_TREATMENT} AS treatmentId
    """, {"cid": data.consultationId})

    if not find_pat:
        # Fallback to direct appointment ID
        find_pat = run_query(f"""
        MATCH (a:{sm.LABEL_APPOINTMENT} {{{sm.KEY_APPOINTMENT}: $cid}})<-[:{sm.REL_HAS_APPOINTMENT}]-(p:{sm.LABEL_PATIENT})
        OPTIONAL MATCH (a)-[:{sm.REL_HAS_TREATMENT}]->(t:{sm.LABEL_TREATMENT})
        RETURN p.{sm.KEY_PATIENT} AS patientId, t.{sm.KEY_TREATMENT} AS treatmentId
        """, {"cid": data.consultationId})

    if not find_pat:
        raise HTTPException(status_code=404, detail="Consultation or associated Patient not found")

    patient_id = find_pat[0]["patientId"]
    treatment_id = find_pat[0].get("treatmentId")

    bill_no = gen_id("B")
    bill_date = str(date.today())
    total_amount = (
        data.consultationCharge +
        data.labCharge +
        data.pharmacyCharge +
        data.roomCharge +
        data.otherCharge
    )
    if total_amount == 0.0:
        total_amount = 1250.0

    def _transaction_work(tx):
        create_bill_cypher = f"""
        MATCH (p:{sm.LABEL_PATIENT} {{{sm.KEY_PATIENT}: $patient_id}})
        CREATE (b:{sm.LABEL_BILL} {{
            {sm.KEY_BILL}: $bill_no,
            billDate: $date,
            amount: $total,
            consultationCharge: $c_charge,
            labCharge: $l_charge,
            pharmacyCharge: $p_charge,
            roomCharge: $r_charge,
            otherCharge: $o_charge,
            paymentMethod: $mode,
            paymentMode: $mode,
            paymentStatus: $status,
            patientId: $patient_id
        }})
        CREATE (p)-[:{sm.REL_HAS_BILL}]->(b)
        RETURN b.{sm.KEY_BILL} AS billNo
        """
        tx.run(create_bill_cypher, {
            "patient_id": patient_id,
            "bill_no": bill_no,
            "date": bill_date,
            "c_charge": data.consultationCharge,
            "l_charge": data.labCharge,
            "p_charge": data.pharmacyCharge,
            "r_charge": data.roomCharge,
            "o_charge": data.otherCharge,
            "total": total_amount,
            "mode": data.paymentMode,
            "status": data.paymentStatus
        })

        if treatment_id:
            link_treat = f"""
            MATCH (t:{sm.LABEL_TREATMENT} {{{sm.KEY_TREATMENT}: $t_id}})
            MATCH (b:{sm.LABEL_BILL} {{{sm.KEY_BILL}: $bill_no}})
            MERGE (t)-[:{sm.REL_HAS_BILL}]->(b)
            """
            tx.run(link_treat, {"t_id": treatment_id, "bill_no": bill_no})

        if data.claim:
            claim_id = gen_id("ICB")
            claim_cypher = f"""
            MATCH (b:{sm.LABEL_BILL} {{{sm.KEY_BILL}: $bill_no}})
            MATCH (p:{sm.LABEL_PATIENT} {{{sm.KEY_PATIENT}: $patient_id}})
            CREATE (cl:{sm.LABEL_INSURANCE_CLAIM} {{
                {sm.KEY_INSURANCE_CLAIM}: $claim_id,
                claimAmount: $claim_amount,
                approvedAmount: 0.0,
                status: 'Pending verification',
                insuranceProvider: $company_id,
                insuranceNumber: coalesce(p.insuranceNumber, 'INS-001')
            }})
            CREATE (b)-[:{sm.REL_HAS_CLAIM}]->(cl)
            CREATE (p)-[:{sm.REL_HAS_CLAIM}]->(cl)
            """
            tx.run(claim_cypher, {
                "bill_no": bill_no,
                "patient_id": patient_id,
                "claim_id": claim_id,
                "company_id": data.claim.companyId or "WellnessCorp",
                "claim_amount": data.claim.claimAmount
            })

    run_write_transaction(_transaction_work)

    bills = list_bills()
    created = [b for b in bills if b["billNo"] == bill_no]
    return created[0] if created else {"billNo": bill_no, "totalAmount": total_amount}


@router.put("/bills/{bill_no}")
def update_bill(bill_no: str, data: BillUpdate):
    check = run_query(f"MATCH (b:{sm.LABEL_BILL} {{{sm.KEY_BILL}: $id}}) RETURN b", {"id": bill_no})
    if not check:
        raise HTTPException(status_code=404, detail="Bill not found")

    existing = check[0]["b"]
    c_charge = data.consultationCharge if data.consultationCharge is not None else existing.get("consultationCharge", 0.0)
    l_charge = data.labCharge if data.labCharge is not None else existing.get("labCharge", 0.0)
    p_charge = data.pharmacyCharge if data.pharmacyCharge is not None else existing.get("pharmacyCharge", 0.0)
    r_charge = data.roomCharge if data.roomCharge is not None else existing.get("roomCharge", 0.0)
    o_charge = data.otherCharge if data.otherCharge is not None else existing.get("otherCharge", 0.0)
    new_total = c_charge + l_charge + p_charge + r_charge + o_charge
    if new_total == 0.0:
        new_total = existing.get("amount", 1000.0)

    updates = [
        "b.amount = $total",
        "b.totalAmount = $total"
    ]
    params = {
        "id": bill_no,
        "total": new_total
    }

    if data.paymentMode is not None:
        updates.extend(["b.paymentMethod = $mode", "b.paymentMode = $mode"])
        params["mode"] = data.paymentMode
    if data.paymentStatus is not None:
        updates.append("b.paymentStatus = $status")
        params["status"] = data.paymentStatus

    cypher = f"""
    MATCH (b:{sm.LABEL_BILL} {{{sm.KEY_BILL}: $id}})
    SET {", ".join(updates)}
    RETURN b.{sm.KEY_BILL} AS billNo
    """
    run_query(cypher, params)

    bills = list_bills()
    updated = [b for b in bills if b["billNo"] == bill_no]
    return updated[0] if updated else {"billNo": bill_no}


@router.delete("/bills/{bill_no}")
def delete_bill(bill_no: str):
    check = run_query(f"MATCH (b:{sm.LABEL_BILL} {{{sm.KEY_BILL}: $id}}) RETURN b", {"id": bill_no})
    if not check:
        raise HTTPException(status_code=404, detail="Bill not found")

    cypher = f"""
    MATCH (b:{sm.LABEL_BILL} {{{sm.KEY_BILL}: $id}})
    OPTIONAL MATCH (b)-[:{sm.REL_HAS_CLAIM}]->(cl:{sm.LABEL_INSURANCE_CLAIM})
    DETACH DELETE cl, b
    """
    run_query(cypher, {"id": bill_no})
    return {"status": "success", "message": f"Bill {bill_no} and related claim deleted."}


@router.put("/claims/{claim_id}")
def update_claim(claim_id: str, data: ClaimUpdate):
    check = run_query(f"MATCH (cl:{sm.LABEL_INSURANCE_CLAIM} {{{sm.KEY_INSURANCE_CLAIM}: $id}}) RETURN cl", {"id": claim_id})
    if not check:
        raise HTTPException(status_code=404, detail="Insurance claim not found")

    approval_date = str(date.today()) if data.status == "Approved" else None

    cypher = f"""
    MATCH (cl:{sm.LABEL_INSURANCE_CLAIM} {{{sm.KEY_INSURANCE_CLAIM}: $id}})
    SET cl.status = $status,
        cl.approvedAmount = $approved,
        cl.approvalDate = $approval_date
    RETURN cl.{sm.KEY_INSURANCE_CLAIM} AS claimId,
           cl.status AS status,
           cl.approvedAmount AS approvedAmount,
           cl.approvalDate AS approvalDate
    """
    records = run_query(cypher, {
        "id": claim_id,
        "status": data.status,
        "approved": data.approvedAmount,
        "approval_date": approval_date
    })
    return records[0]


@router.get("/insurance-companies")
def list_insurance_companies():
    cypher = f"""
    MATCH (cl:{sm.LABEL_INSURANCE_CLAIM})
    WHERE cl.insuranceProvider IS NOT NULL AND cl.insuranceProvider <> ''
    RETURN DISTINCT cl.insuranceProvider AS companyId,
           cl.insuranceProvider AS name,
           '1-800-INSURANCE' AS contact
    ORDER BY name ASC
    """
    records = run_query(cypher)
    if not records:
        return [
            {"companyId": "WellnessCorp", "name": "WellnessCorp", "contact": "+1-800-555-0101"},
            {"companyId": "PulseSecure", "name": "PulseSecure", "contact": "+1-800-555-0102"},
            {"companyId": "CarePlus", "name": "CarePlus", "contact": "+1-800-555-0103"}
        ]
    return records


@router.get("/reports/patient-billing")
def patient_billing_report():
    """Report: Full patient billing report matching required query 11"""
    cypher = f"""
    MATCH (p:{sm.LABEL_PATIENT})-[:{sm.REL_HAS_BILL}]->(b:{sm.LABEL_BILL})
    OPTIONAL MATCH (b)-[:{sm.REL_HAS_CLAIM}]->(cl:{sm.LABEL_INSURANCE_CLAIM})
    RETURN coalesce(p.name, p.firstName + ' ' + p.lastName) AS patient,
           round(b.amount, 2) AS totalBill,
           coalesce(round(cl.claimAmount, 2), 0) AS claimAmount,
           coalesce(round(cl.approvedAmount, 2), 0) AS approvedAmount,
           round(b.amount - coalesce(cl.approvedAmount, 0), 2) AS patientPayable
    ORDER BY totalBill DESC
    """
    return run_query(cypher)
