import frappe
from frappe.utils import format_time, today
import pprint


@frappe.whitelist(allow_guest=False)
def get_attendance_status():
    current_date = today()
    user = frappe.session.user

    # Get linked employee from user
    employee = frappe.get_value("Employee", {"user_id": user}, "name")

    if not employee:
        return {
            "attendance_status": {
                "check_in_time": None,
                "status": "No Employee Linked",
                "action": "Check In",
            }
        }

    # Get IN check-in
    checkin = frappe.get_all(
        "Employee Checkin",
        filters={
            "employee": employee,
            "time": [
                "between",
                [f"{current_date} 00:00:00", f"{current_date} 23:59:59"],
            ],
            "log_type": "IN",
        },
        fields=["time"],
        order_by="time asc",
        limit=1,
    )

    # Get OUT check-in
    checkout = frappe.get_all(
        "Employee Checkin",
        filters={
            "employee": employee,
            "time": [
                "between",
                [f"{current_date} 00:00:00", f"{current_date} 23:59:59"],
            ],
            "log_type": "OUT",
        },
        fields=["time"],
        order_by="time desc",
        limit=1,
    )

    # Get today's attendance
    attendance = frappe.get_all(
        "Attendance",
        filters={"employee": employee, "attendance_date": current_date},
        fields=["status"],
        limit=1,
    )

    # Prepare output
    check_in_time = format_time(checkin[0]["time"]) if checkin else None
    check_out_time = format_time(checkout[0]["time"]) if checkout else None

    status = attendance[0]["status"] if attendance else "Unknown"

    # Determine the action
    action = "Check Out" if check_out_time and not check_in_time else "Check In"
    show_time = check_out_time if check_out_time else check_in_time
    action_time = "Check_Out_Time" if check_out_time else "Check_In_Time"

    return {
        "attendance_status": {
            f"{action_time}": show_time,
            "status": status,
            "action": action,
        }
    }
