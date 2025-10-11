import frappe
from frappe.utils import format_time, today
import pprint
from frappe.utils import now
from frappe import _
from hrms.hr.doctype.employee_checkin.employee_checkin import (
    add_log_based_on_employee_field,
)

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
def update_attendance_status(bssid=None, ssid=None):
    current_date = today()
    user = frappe.session.user
    log_type = None

    # Get linked employee
    employee = frappe.get_value("Employee", {"user_id": user}, "name")
    if not employee:
        frappe.throw(_("No Employee linked with this user."))

    # Get company from employee
    company = frappe.get_value("Employee", employee, "company")
    if not company:
        frappe.throw(_("No company linked with this employee."))

    # ✅ Check WiFi match
    wifi_match = False
    if bssid:
        wifi_match = frappe.db.exists(
            "Company WiFi", {"company": company, "bssid": bssid}
        )

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

    if not wifi_match:
        frappe.throw(_("Checkin and Checkout not allowed — not connected to company WiFi."))

    # Create new Employee Checkin
    checkin_doc = frappe.get_doc(
        {
            "doctype": "Employee Checkin",
            "employee": employee,
            "log_type": log_type,
            "time": now(),
            "skip_auto_attendance": 1,
            "custom_bssid": bssid,
            "custom_ssid": ssid,
            "custom_wifi_match": 1 if wifi_match else 0,
        }
    )
    checkin_doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "message": f"Successfully checked {log_type}",
        "checkin_id": checkin_doc.name,
        "timestamp": checkin_doc.time,
        "employee": employee,
        "wifi_match": bool(wifi_match),
    }


@frappe.whitelist(allow_guest=False)
def secure_employee_checkin(
    employee_field_value: str,
    log_type: str,
    timestamp: str | None = None,
    employee_fieldname: str = "cell_number",
    bssid: str | None = None,
    ssid: str | None = None,
) -> dict:
    """
    Custom secured employee check-in/out API that validates WiFi before allowing log creation.

    Args:
        employee_field_value (str): The employee identifier (e.g. cell number or employee ID)
        log_type (str): Either 'IN' or 'OUT'
        timestamp (str | None): The check-in/out timestamp (defaults to current time if None)
        employee_fieldname (str): The Employee field name to search by (default: 'cell_number')
        bssid (str | None): WiFi BSSID from the user's device
        ssid (str | None): WiFi SSID from the user's device

    Returns:
        dict: API response containing status, message, WiFi match info, and created check-in ID
    """

    # 1️⃣ Validate employee
    employee_name = frappe.get_value(
        "Employee", {employee_fieldname: employee_field_value}, "name"
    )

    if not employee_name:
        frappe.throw(_("No Employee found for the provided identifier."))

    company = frappe.get_value("Employee", employee_name, "company")
    if not company:
        frappe.throw(_("No Company linked to the specified Employee."))

    # 2️⃣ Validate WiFi information
    if not bssid:
        frappe.throw(_("BSSID is required to perform check-in or check-out."))

    wifi_match = frappe.db.exists("Company WiFi", {"company": company, "bssid": bssid})
    if not wifi_match:
        frappe.throw(
            _(
                "Check-in/out not allowed — you are not connected to an authorized company WiFi network."
            )
        )

    # 3️⃣ Call ERPNext’s built-in checkin function
    result = add_log_based_on_employee_field(
        employee_field_value=employee_field_value,
        log_type=log_type,
        timestamp=timestamp,
        employee_fieldname=employee_fieldname,
    )

    # 4️⃣ Update WiFi data in the newly created checkin record
    checkin_id = result.get("employee_checkin") if isinstance(result, dict) else None
    if checkin_id:
        frappe.db.set_value(
            "Employee Checkin",
            checkin_id,
            {
                "custom_bssid": bssid,
                "custom_ssid": ssid,
                "custom_wifi_match": 1,
            },
        )
        frappe.db.commit()

    # 5️⃣ Return structured response
    return {
        "status": "success",
        "message": _("Checked {0} successfully").format(log_type),
        "employee": employee_name,
        "company": company,
        "wifi_match": True,
        "checkin_id": checkin_id,
        "timestamp": timestamp or frappe.utils.now(),
    }
