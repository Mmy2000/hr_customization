import frappe
from frappe.utils import today
from collections import defaultdict


@frappe.whitelist(allow_guest=False)
def get_tasks(status=None):
    user = frappe.session.user

    # Build filters dynamically
    filters = {"allocated_to": user}
    if status:
        filters["status"] = status

    # Fetch tasks using the filters
    tasks = frappe.get_all(
        "ToDo",
        filters=filters,
        fields=["*"],
    )

    # Dynamically get all status values from ToDo DocType
    meta = frappe.get_meta("ToDo")
    status_field = next((f for f in meta.fields if f.fieldname == "status"), None)

    all_statuses = []
    if status_field and status_field.options:
        all_statuses = [s.strip() for s in status_field.options.split("\n")]

    # Initialize status counts with 0
    status_counts = {s: 0 for s in all_statuses}

    # Count tasks per status (based on all user's tasks, not just filtered)
    all_tasks = frappe.get_all(
        "ToDo",
        filters={"allocated_to": user},
        fields=["status"],
    )

    for t in all_tasks:
        st = t.get("status")
        if st in status_counts:
            status_counts[st] += 1
        else:
            status_counts[st] = (
                status_counts.get(st, 0) + 1
            )  # fallback for unknown status

    return {"tasks": tasks, "status_counts": status_counts}
