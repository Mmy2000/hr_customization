import frappe
from frappe.utils import format_time, today
import pprint
from frappe.utils import now
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_requests_by_status(status):
    user = frappe.session.user
    employee = frappe.get_value("Employee", {"user_id": user}, "name")

    if not employee:
        return {"requests": []}

    filters = {"employee": employee, "docstatus": ["<", 2]}

    # Map UI statuses to ERPNext statuses
    status_map = {
        "active": ["Open"],
        "approved": ["Approved"],
        "rejected": ["Rejected"],
    }

    if status in status_map:
        filters["status"] = ["in", status_map[status]]
    else:
        frappe.throw("Invalid status filter")

    leave_apps = frappe.get_all(
        "Leave Application",
        # filters=filters,
        fields=[
            "name",
            "leave_type",
            "from_date",
            "to_date",
            "status",
            "total_leave_days",
        ],
        order_by="from_date desc",
    )

    return {"requests": leave_apps}
