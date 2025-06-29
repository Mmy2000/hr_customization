import frappe
from frappe.utils import format_time, today, formatdate
import pprint
import datetime


@frappe.whitelist()
def get_salary_slips(year=None):
    user = frappe.session.user
    employee = frappe.get_doc("Employee", {"user_id": user})

    if not employee:
        return "No Employee Linked"

    # Default to current year if not provided
    if not year:
        year = datetime.datetime.now().year
    else:
        year = int(year)

    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    salary_slips_list = frappe.get_all(
        "Salary Slip",
        filters={
            "employee": employee.name,
            "end_date": ["between", [start_date, end_date]],
        },
        fields=["name", "end_date", "net_pay"],
        order_by="end_date desc",
    )

    result = []
    for slip in salary_slips_list:
        label = formatdate(slip["end_date"], "MMMM yyyy")
        result.append(
            {"label": label, "net_salary": slip["net_pay"], "name": slip["name"]}
        )

    return result


@frappe.whitelist()
def get_salary_slips_details(name):
    user = frappe.session.user
    employee = frappe.get_doc("Employee", {"user_id": user})

    if not employee:
        return "No Employee Linked"

    # Get the salary slip document
    salary_slip = frappe.get_doc("Salary Slip", name)

    # Check if the salary slip belongs to the current user
    if salary_slip.employee != employee.name:
        return "Access Denied"

    # Employee Info
    employee_info = {
        "name": employee.employee_name,
        "employee_id": employee.name,
        "department": employee.department,
        "position": employee.designation,
    }

    # Payslip Title
    payslip_title = f"Payslip {formatdate(salary_slip.end_date, 'MMMM yyyy')}"

    # Earnings
    earnings = []
    total_earnings = 0
    for earning in salary_slip.earnings:
        earnings.append(
            {"component": earning.salary_component, "amount": earning.amount}
        )
        total_earnings += earning.amount

    # Deductions
    deductions = []
    total_deductions = 0
    for deduction in salary_slip.deductions:
        deductions.append(
            {"component": deduction.salary_component, "amount": deduction.amount}
        )
        total_deductions += deduction.amount

    # Bank Account (if available)
    bank_account = getattr(salary_slip, "bank_account_no", None) or getattr(
        employee, "bank_ac_no", None
    )

    # Payment Date
    payment_date = (
        salary_slip.payment_date
        if hasattr(salary_slip, "payment_date")
        else salary_slip.end_date
    )

    # Final structure
    details = {
        "payslip_title": payslip_title,
        "employee_info": employee_info,
        "salary_details": {
            "earnings": earnings,
            "total_earnings": total_earnings,
            "deductions": deductions,
            "total_deductions": total_deductions,
            "net_salary": salary_slip.net_pay,
        },
        "bank_account": bank_account,
        "payment_date": payment_date,
    }

    return details
