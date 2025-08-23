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

@frappe.whitelist()
def get_check_in_and_out_times():

    user = frappe.session.user
    employee_id = frappe.get_value("Employee", {"user_id": user}, "name")
    # Get today's date
    today_date = today()

    # Fetch attendance records for the employee for today
    attendance_records = frappe.get_all(
        "Employee Checkin",
        filters={"employee": employee_id},
        fields=['*'],
    )

    return {
        "attendance_records": attendance_records
    }
