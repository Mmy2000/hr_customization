import frappe
from frappe import _


@frappe.whitelist(allow_guest=False)
def get_tasks(status=None):
    user = frappe.session.user
    user_lang = frappe.db.get_value("User", user, "language") or frappe.local.lang
    frappe.local.lang = user_lang

    # Fetch filtered tasks
    filters = {"allocated_to": user}
    if status:
        filters["status"] = status

    tasks = frappe.get_all("ToDo", filters=filters, fields=["*"])

    # Get status options
    meta = frappe.get_meta("ToDo")
    status_field = next((f for f in meta.fields if f.fieldname == "status"), None)
    all_statuses = (
        [s.strip() for s in status_field.options.split("\n")]
        if status_field and status_field.options
        else []
    )

    # Init status counts
    status_counts = {s: 0 for s in all_statuses}

    # Count all tasks for the user
    all_tasks = frappe.get_all(
        "ToDo", filters={"allocated_to": user}, fields=["status"]
    )
    for t in all_tasks:
        st = t.get("status")
        status_counts[st] = status_counts.get(st, 0) + 1

    # Translate filtered tasks
    translated_tasks = []
    for task in tasks:
        translated_task = {}
        for k, v in task.items():
            translated_task[k] = _(v) if isinstance(v, str) else v
        translated_tasks.append(translated_task)

    return {"tasks": translated_tasks, "status_counts": status_counts}


@frappe.whitelist(allow_guest=False)
def get_task_details(name):
    user = frappe.session.user
    user_lang = frappe.db.get_value("User", user, "language") or frappe.local.lang
    frappe.local.lang = user_lang
    # Get the task as a doc
    task = frappe.get_doc("ToDo", name)

    # Convert to dict
    task_dict = task.as_dict()

    # Translate string fields
    translated_task = {}
    for k, v in task_dict.items():
        translated_task[k] = _(v) if isinstance(v, str) else v

    return translated_task
