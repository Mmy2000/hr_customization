import frappe
from frappe.utils import format_time, today
import pprint


@frappe.whitelist()
def get_attendance_list():
    user = frappe.session.user
    employee = frappe.get_value("Employee", {"user_id": user}, "name")

    if not employee:
        return {
            "attendance_status": {
                "check_in_time": None,
                "status": "No Employee Linked",
                "action": "Check In",
            }
        }

    attendance_list = frappe.get_all(
        "Attendance",
        filters={
            "employee": employee,
        },
        fields=["*"],
    )
    pprint.pprint(attendance_list)

    return attendance_list