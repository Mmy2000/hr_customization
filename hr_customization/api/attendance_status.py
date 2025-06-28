import frappe
from frappe.utils import format_time, today
import pprint
from frappe.utils import now
from frappe import _


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
        fields=["*"],
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
        fields=["*"],
        order_by="time desc",
        limit=1,
    )

    # Prepare output
    check_in_date_time = (checkin[0]["time"]) if checkin else None
    check_out_date_time = (checkout[0]["time"]) if checkout else None

    # Determine the action
    action = "Check Out" if check_out_date_time and not check_in_date_time else "Check In"
    show_time = check_out_date_time if check_out_date_time else check_in_date_time

    return {
        "attendance_status": {
            "Time": show_time,
            "status": action,
        }
    }


@frappe.whitelist(allow_guest=False)
def update_attendance_status():
    current_date = today()
    user = frappe.session.user
    log_type = None

    # Get linked employee
    employee = frappe.get_value("Employee", {"user_id": user}, "name")

    if not employee:
        frappe.throw(_("No Employee linked with this user."))

    # Get last checkin for today
    last_checkin = frappe.get_all(
        "Employee Checkin",
        filters={
            "employee": employee,
            "time": [
                "between",
                [f"{current_date} 00:00:00", f"{current_date} 23:59:59"],
            ],
        },
        fields=["*"],
        order_by="time desc",
        limit=1,
    )

    if last_checkin[0]["log_type"] == "IN":
        log_type = "OUT"
    else:
        log_type = "IN"

    # Create new Employee Checkin
    checkin_doc = frappe.get_doc(
        {
            "doctype": "Employee Checkin",
            "employee": employee,
            "log_type": log_type,
            "time": now(),
            "skip_auto_attendance": 1,  # Optional: skip automatic attendance marking
        }
    )
    checkin_doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "message": f"Successfully checked {log_type}",
        "checkin_id": checkin_doc.name,
        "timestamp": checkin_doc.time,
        "employee": employee,
    }
