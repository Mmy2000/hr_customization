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

    # Get check-status
    check_status = frappe.get_all(
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

    # Prepare output
    check_status_date_time = (check_status[0]["time"]) if check_status else None
    action = check_status[0]["log_type"]

    return {
        "attendance_status": {
            "Time": check_status_date_time,
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

    if last_checkin:
        if last_checkin[0]["log_type"] == "IN":
            log_type = "OUT"
        else:
            log_type = "IN"
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
