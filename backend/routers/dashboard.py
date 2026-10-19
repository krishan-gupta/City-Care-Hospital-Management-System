from datetime import date
from fastapi import APIRouter
from db import run_query
import schema_map as sm

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
def get_dashboard_summary():
    today_str = str(date.today())

    cypher = f"""
    CALL () {{
        MATCH (p:{sm.LABEL_PATIENT}) RETURN count(p) AS totalPatients
    }}
    CALL () {{
        MATCH (d:{sm.LABEL_DOCTOR}) RETURN count(d) AS totalDoctors
    }}
    CALL () {{
        MATCH (a:{sm.LABEL_APPOINTMENT}) RETURN count(a) AS totalAppointments
    }}
    CALL () {{
        MATCH (a2:{sm.LABEL_APPOINTMENT})
        WHERE toString(a2.appointmentDate) STARTS WITH $today
        RETURN count(a2) AS appointmentsToday
    }}
    CALL () {{
        MATCH (b:{sm.LABEL_BILL}) RETURN coalesce(round(sum(b.amount), 2), 0) AS totalRevenue
    }}
    CALL () {{
        MATCH (cl:{sm.LABEL_INSURANCE_CLAIM})
        WHERE cl.status =~ '(?i).*pending.*' OR cl.status = 'Submitted'
        RETURN count(cl) AS pendingClaims
    }}
    CALL () {{
        MATCH (t:{sm.LABEL_LAB_TEST})
        WHERE t.status = 'Abnormal'
        RETURN count(t) AS abnormalLabResults
    }}
    RETURN totalPatients, totalDoctors, totalAppointments, appointmentsToday, totalRevenue, pendingClaims, abnormalLabResults
    """
    records = run_query(cypher, {"today": today_str})
    if records:
        return records[0]
    return {
        "totalPatients": 0,
        "totalDoctors": 0,
        "totalAppointments": 0,
        "appointmentsToday": 0,
        "totalRevenue": 0,
        "pendingClaims": 0,
        "abnormalLabResults": 0
    }


@router.get("/billing")
def get_dashboard_billing():
    stats_cypher = f"""
    MATCH (b:{sm.LABEL_BILL})
    RETURN coalesce(round(sum(b.amount), 2), 0) AS total,
           coalesce(round(avg(b.amount), 2), 0) AS average,
           coalesce(round(max(b.amount), 2), 0) AS highest,
           coalesce(round(min(b.amount), 2), 0) AS lowest
    """
    stats_res = run_query(stats_cypher)
    stats = stats_res[0] if stats_res else {"total": 0, "average": 0, "highest": 0, "lowest": 0}

    dept_cypher = f"""
    MATCH (b:{sm.LABEL_BILL})<-[:{sm.REL_HAS_BILL}]-(t:{sm.LABEL_TREATMENT})<-[:{sm.REL_HAS_TREATMENT}]-(a:{sm.LABEL_APPOINTMENT})<-[:{sm.REL_ASSIGNED_TO}]-(d:{sm.LABEL_DOCTOR})-[:{sm.REL_BELONGS_TO}]->(dep:{sm.LABEL_DEPARTMENT})
    RETURN dep.name AS department, round(sum(b.amount), 2) AS revenue, count(b) AS billCount
    ORDER BY revenue DESC
    """
    dept_res = run_query(dept_cypher)

    return {
        "stats": stats,
        "revenueByDepartment": dept_res
    }


@router.get("/claims")
def get_dashboard_claims():
    status_cypher = f"""
    MATCH (cl:{sm.LABEL_INSURANCE_CLAIM})
    RETURN coalesce(cl.status, 'Unknown') AS status,
           count(cl) AS count,
           round(coalesce(sum(cl.claimAmount), 0), 2) AS totalAmount,
           round(coalesce(sum(cl.approvedAmount), 0), 2) AS totalApproved
    ORDER BY count DESC
    """
    by_status = run_query(status_cypher)

    company_cypher = f"""
    MATCH (cl:{sm.LABEL_INSURANCE_CLAIM})
    WHERE cl.insuranceProvider IS NOT NULL AND cl.insuranceProvider <> ''
    RETURN cl.insuranceProvider AS company,
           count(cl) AS claimCount,
           round(coalesce(sum(cl.claimAmount), 0), 2) AS totalClaimed,
           round(coalesce(sum(cl.approvedAmount), 0), 2) AS totalApproved
    ORDER BY totalClaimed DESC
    """
    by_company = run_query(company_cypher)

    return {
        "byStatus": by_status,
        "byCompany": by_company
    }


@router.get("/doctors")
def get_dashboard_doctors():
    cypher = f"""
    MATCH (d:{sm.LABEL_DOCTOR})
    OPTIONAL MATCH (d)-[:{sm.REL_ASSIGNED_TO}]->(:{sm.LABEL_APPOINTMENT})<-[:{sm.REL_HAS_APPOINTMENT}]-(p:{sm.LABEL_PATIENT})
    OPTIONAL MATCH (d)-[:{sm.REL_BELONGS_TO}]->(dep:{sm.LABEL_DEPARTMENT})
    WITH d, dep, count(DISTINCT p) AS cnt
    WITH collect({{
        empId: d.{sm.KEY_DOCTOR},
        doctor: coalesce(d.name, d.firstName + ' ' + d.lastName),
        department: dep.name,
        patients: cnt
    }}) AS rows, avg(cnt) AS avgCnt
    UNWIND rows AS r
    RETURN r.empId AS empId,
           r.doctor AS doctor,
           r.department AS department,
           r.patients AS patients,
           round(avgCnt, 2) AS averagePatients,
           (r.patients > avgCnt) AS isAboveAverage
    ORDER BY patients DESC
    """
    return run_query(cypher)
