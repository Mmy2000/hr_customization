import frappe
from frappe.utils import format_time, today
import pprint
from frappe import _


@frappe.whitelist()
def get_attendance_list():
    user = frappe.session.user
    employee = frappe.get_value("Employee", {"user_id": user}, "name")

    if not employee:
        frappe.throw(_("No Employee linked with this user."))

    attendance_list = frappe.get_all(
        "Attendance",
        filters={
            "employee": employee,
        },
        fields=["*"],
    )

    return attendance_list
