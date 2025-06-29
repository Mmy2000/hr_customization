import frappe
from frappe.utils import format_time, today
import pprint


@frappe.whitelist()
def get_salary_slips():
    user = frappe.session.user
    employee = frappe.get_value("Employee", {"user_id": user}, "name")

    if not employee:
        return "No Employee Linked"

    salary_slips_list = frappe.get_all(
        "Salary Slip",
        filters={
            "employee": employee,
        },
        fields=["*"],
    )

    return salary_slips_list
