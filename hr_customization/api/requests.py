import frappe
from frappe.utils import format_time, today, getdate
import json
import frappe
from frappe import _
from hr_customization.validations.validations import handle_request_error


# for shift requests
@frappe.whitelist(allow_guest=False)
def get_shift_types():
    shift_types = frappe.get_all("Shift Type", fields=["name"])
    return [s.name for s in shift_types]

# for shift requests
@frappe.whitelist(allow_guest=False)
def get_companies():
    companies = frappe.get_all("Company", fields=["name"])
    return [c.name for c in companies]


# for shift requests
@frappe.whitelist(allow_guest=False)
def get_status_shift_request():
    meta = frappe.get_meta("Shift Request")
    status_field = meta.get_field("status")

    if not status_field or status_field.fieldtype != "Select":
        frappe.throw(_("Reason field is not a Select field"))

    options = status_field.options or ""
    return [opt.strip() for opt in options.split("\n") if opt.strip()]


@frappe.whitelist(allow_guest=False)
def get_shift_request_approver():
    user = frappe.session.user

    # Get the linked employee ID
    employee_id = frappe.get_value("Employee", {"user_id": user}, "name")
    if not employee_id:
        frappe.throw(_("No Employee record linked to this user."))

    # Fetch full Employee doc to access fields
    employee_doc = frappe.get_doc("Employee", employee_id)
    company = employee_doc.company

    return {"approver": employee_doc.shift_request_approver, "company": company}


@frappe.whitelist(allow_guest=False)
def get_leave_application_approver():
    user = frappe.session.user

    # Get the linked employee ID
    employee_id = frappe.get_value("Employee", {"user_id": user}, "name")
    if not employee_id:
        frappe.throw(_("No Employee record linked to this user."))

    # Fetch full Employee doc to access fields
    employee_doc = frappe.get_doc("Employee", employee_id)
    company = employee_doc.company

    return {"approver": employee_doc.leave_approver, "company": company}


@frappe.whitelist(allow_guest=False)
def get_reasons():
    meta = frappe.get_meta("Attendance Request")
    reason_field = meta.get_field("reason")

    if not reason_field or reason_field.fieldtype != "Select":
        frappe.throw(_("Reason field is not a Select field"))

    options = reason_field.options or ""
    return [opt.strip() for opt in options.split("\n") if opt.strip()]


@frappe.whitelist(allow_guest=False)
def get_leaves_types():
    leaves = frappe.get_all("Leave Type", fields=["name"])
    return [c.name for c in leaves]

# for travel request
@frappe.whitelist(allow_guest=False)
def get_purpose_of_travel():
    purposes = frappe.get_all("Purpose of Travel", fields=["name"])
    return [c.name for c in purposes]

@frappe.whitelist(allow_guest=False)
def get_travel_funding():
    meta = frappe.get_meta("Travel Request")
    travel_funding_field = meta.get_field("travel_funding")

    if not travel_funding_field or travel_funding_field.fieldtype != "Select":
        frappe.throw(_("travel funding field is not a Select field"))

    options = travel_funding_field.options or ""
    return [opt.strip() for opt in options.split("\n") if opt.strip()]

@frappe.whitelist(allow_guest=False)
def get_travel_types():
    meta = frappe.get_meta("Travel Request")
    travel_type_field = meta.get_field("travel_type")

    if not travel_type_field or travel_type_field.fieldtype != "Select":
        frappe.throw(_("travel type field is not a Select field"))

    options = travel_type_field.options or ""
    return [opt.strip() for opt in options.split("\n") if opt.strip()]

@frappe.whitelist(allow_guest=False)
def get_identification_document_type():
    identification = frappe.get_all("Identification Document Type", fields=["name"])
    return [c.name for c in identification]

@frappe.whitelist(allow_guest=False)
def get_cost_center():
    user = frappe.session.user

    # Get the linked employee ID
    employee_id = frappe.get_value("Employee", {"user_id": user}, "name")
    if not employee_id:
        frappe.throw(_("No Employee record linked to this user."))

    # Fetch full Employee doc to access fields
    employee_doc = frappe.get_doc("Employee", employee_id)
    company = employee_doc.company
    costs = frappe.get_all("Cost Center", fields=["name"], filters={"company": company})
    return [c.name for c in costs]


@frappe.whitelist(allow_guest=True)
def get_expense_claim_types():
    try:
        expense_types = frappe.get_all("Expense Claim Type", fields=["name"])
        return [e.name for e in expense_types]
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error fetching Expense Claim Types")
        frappe.throw(_("Failed to fetch expense claim types."))


@frappe.whitelist(allow_guest=False)
def get_all_requests(request_type=None, status=None):
    user = frappe.session.user
    user_lang = frappe.db.get_value("User", user, "language") or frappe.local.lang
    frappe.local.lang = user_lang

    # Get linked employee
    employee_id = frappe.get_value("Employee", {"user_id": user}, "name")
    if not employee_id:
        frappe.throw(_("No Employee record linked to this user."))

    # Define request types
    request_types = {
        "Leave Application": {"doctype": "Leave Application", "status_field": "status"},
        "Shift Request": {"doctype": "Shift Request", "status_field": "status"},
        "Travel Request": {"doctype": "Travel Request", "status_field": "status"},
        "Attendance Request": {
            "doctype": "Attendance Request",
            "status_field": "status",
        },
    }

    status_options = {}
    requests = []

    for label, info in request_types.items():
        if request_type and request_type != label:
            continue

        doctype = info["doctype"]
        status_field = info["status_field"]

        # Base filters
        filters = {"employee": employee_id}
        if status:
            filters[status_field] = status

        # Fetch records
        records = frappe.get_all(doctype, filters=filters, fields=["*"])

        # Translate fields
        for r in records:
            translated = {}
            for k, v in r.items():
                translated[k] = _(v) if isinstance(v, str) else v
            translated["type"] = _(label)
            requests.append(translated)

        # Build translated status options
        field_meta = frappe.get_meta(doctype).get_field(status_field)
        options = []
        if field_meta and field_meta.fieldtype == "Select":
            raw = field_meta.options or ""
            options = [_(opt.strip()) for opt in raw.split("\n") if opt.strip()]
        status_options[_(label)] = options

    return {"requests": requests, "status_options": status_options}


@frappe.whitelist(allow_guest=False)
def create_request(request_type, data):
    if isinstance(data, str):
        data = json.loads(data)

    user = frappe.session.user

    # Get linked employee
    employee_id = frappe.get_value("Employee", {"user_id": user}, "name")
    if not employee_id:
        frappe.throw(_("No Employee record linked to this user."))

    allowed_request_types = {
        "Leave Application": "Leave Application",
        "Shift Request": "Shift Request",
        "Travel Request": "Travel Request",
        "Attendance Request": "Attendance Request",
    }

    if request_type not in allowed_request_types:
        frappe.throw(_("Invalid request type."))

    doctype = allowed_request_types[request_type]

    # Inject employee if required
    meta = frappe.get_meta(doctype)
    if "employee" in [df.fieldname for df in meta.fields]:
        data["employee"] = employee_id

    # Handle default values if needed
    if request_type == "Shift Request":

        # Validate required fields manually (optional but recommended)
        required_fields = ["shift_type", "company", "approver", "from_date", "status"]
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            frappe.throw(
                _("Missing required fields for Shift Request: {0}").format(
                    ", ".join(missing)
                )
            )
    elif request_type == "Leave Application":
        data.setdefault("status", "Open")
        required_fields = [
            "leave_approver",
            "leave_type",
            "company",
            "from_date",
            "to_date",
            "posting_date",
        ]
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            frappe.throw(
                _("Missing required fields for Shift Request: {0}").format(
                    ", ".join(missing)
                )
            )

    elif request_type == "Attendance Request":
        required_fields = ["shift", "company", "reason", "from_date", "to_date"]
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            frappe.throw(
                _("Missing required fields for Shift Request: {0}").format(
                    ", ".join(missing)
                )
            )

    elif request_type == "Travel Request":
        required_fields = [
            "travel_type",
            "purpose_of_travel",
        ]
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            frappe.throw(
                _("Missing required fields for Shift Request: {0}").format(
                    ", ".join(missing)
                )
            )

    # Create and insert the document
    try:
        doc = frappe.get_doc({"doctype": doctype, **data})
        doc.insert()
        frappe.db.commit()
    except Exception as e:
        handle_request_error(e)

    return {"message": f"{request_type} created successfully.", "docname": doc.name}


@frappe.whitelist(allow_guest=False)
def delete_request(request_type, docname):
    user = frappe.session.user

    # Get linked employee
    employee_id = frappe.get_value("Employee", {"user_id": user}, "name")
    if not employee_id:
        frappe.throw(_("No Employee record linked to this user."))

    allowed_request_types = {
        "Leave Application": "Leave Application",
        "Shift Request": "Shift Request",
        "Travel Request": "Travel Request",
        "Attendance Request": "Attendance Request",
    }

    if request_type not in allowed_request_types:
        frappe.throw(_("Invalid request type."))

    doctype = allowed_request_types[request_type]

    try:
        doc = frappe.get_doc(doctype, docname)

        # Optional: Security check — only allow if the request belongs to the logged-in employee
        if hasattr(doc, "employee") and doc.employee != employee_id:
            frappe.throw(_("You are not authorized to delete this request."))

        doc.delete()
        frappe.db.commit()

        return {"message": f"{request_type} '{docname}' deleted successfully."}

    except frappe.DoesNotExistError:
        frappe.throw(_(f"{request_type} with name '{docname}' does not exist."))

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delete Request Error")
        frappe.throw(_("An error occurred while deleting the request."))


@frappe.whitelist(allow_guest=False)
def update_request(request_type, docname, data=None):
    if isinstance(data, str):
        data = json.loads(data)

    user = frappe.session.user

    # Get linked employee
    employee_id = frappe.get_value("Employee", {"user_id": user}, "name")
    if not employee_id:
        frappe.throw(_("No Employee record linked to this user."))

    allowed_request_types = {
        "Leave Application": "Leave Application",
        "Shift Request": "Shift Request",
        "Travel Request": "Travel Request",
        "Attendance Request": "Attendance Request",
    }

    if request_type not in allowed_request_types:
        frappe.throw(_("Invalid request type."))

    doctype = allowed_request_types[request_type]
    is_admin_user = frappe.session.user == "Administrator"

    try:
        doc = frappe.get_doc(doctype, docname)

        # Optional: Only allow update if the request belongs to this employee
        if (
            hasattr(doc, "employee")
            and doc.employee != employee_id
            and not is_admin_user
        ):
            frappe.throw(_("You are not authorized to update this request."))

        # Handle Leave Application logic
        if request_type == "Leave Application":
            if is_admin_user:
                # Admin: update all fields
                for key, value in data.items():
                    if hasattr(doc, key):
                        setattr(doc, key, value)

                doc.save()
                # doc.submit()  # Submit the document
                frappe.db.commit()
                return {
                    "message": f"{request_type} '{docname}' updated and submitted successfully (admin)."
                }
            else:
                # Employee: update all fields except 'status'
                for key, value in data.items():
                    if key != "status" and hasattr(doc, key):
                        setattr(doc, key, value)

                doc.save()
                frappe.db.commit()
                return {
                    "message": f"{request_type} '{docname}' updated successfully (employee)."
                }
        elif request_type == "Shift Request":
            for key, value in data.items():
                if hasattr(doc, key):
                    setattr(doc, key, value)

            doc.save()
            # doc.submit()  # Submit the document
            frappe.db.commit()
            return {
                "message": f"{request_type} '{docname}' updated and submitted successfully."
            }

        elif request_type == "Attendance Request":
            if is_admin_user:
                for key, value in data.items():
                    if hasattr(doc, key):
                        setattr(doc, key, value)

                doc.save()
                # doc.submit()
                frappe.db.commit()
                return {
                    "message": f"{request_type} '{docname}' updated and submitted successfully (admin)."
                }
            else:
                for key, value in data.items():
                    if hasattr(doc, key):
                        setattr(doc, key, value)

                doc.save()
                frappe.db.commit()
                return {
                    "message": f"{request_type} '{docname}' updated successfully (employee)."
                }

        # Generic update for other request types
        else:
            for key, value in data.items():
                if hasattr(doc, key):
                    setattr(doc, key, value)

            doc.save()
            frappe.db.commit()

            return {"message": f"{request_type} '{docname}' updated successfully."}

    except frappe.DoesNotExistError:
        frappe.throw(_(f"{request_type} with name '{docname}' does not exist."))

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Update Request Error")
        frappe.throw(_("An error occurred while updating the request."))


@frappe.whitelist()
def get_allocated_leaves():
    user = frappe.session.user

    # set language to user language
    user_lang = frappe.db.get_value("User", user, "language") or frappe.local.lang
    frappe.local.lang = user_lang

    employee_id = frappe.get_value("Employee", {"user_id": user}, "name")
    if not employee_id:
        frappe.throw(_("No Employee record linked to this user."))

    today = getdate(frappe.utils.today())

    allocations = frappe.get_all(
        "Leave Allocation",
        filters={"employee": employee_id, "docstatus": 1},
        fields=["name", "leave_type", "from_date", "to_date", "total_leaves_allocated"],
    )

    result = []

    for alloc in allocations:
        leave_type = alloc.leave_type
        total_alloc = alloc.total_leaves_allocated or 0

        expired = 0
        if alloc.to_date and getdate(alloc.to_date) < today:
            expired = total_alloc

        used = (
            frappe.db.sql(
                """
                SELECT SUM(total_leave_days)
                FROM `tabLeave Application`
                WHERE employee = %s
                  AND leave_type = %s
                  AND from_date >= %s AND to_date <= %s
                  AND status = 'Approved'
                  AND docstatus = 1
            """,
                (employee_id, leave_type, alloc.from_date, alloc.to_date),
            )[0][0]
            or 0
        )

        pending = (
            frappe.db.sql(
                """
                SELECT SUM(total_leave_days)
                FROM `tabLeave Application`
                WHERE employee = %s
                  AND leave_type = %s
                  AND from_date >= %s AND to_date <= %s
                  AND status = 'Applied'
                  AND docstatus = 0
            """,
                (employee_id, leave_type, alloc.from_date, alloc.to_date),
            )[0][0]
            or 0
        )

        available = max(total_alloc - used - expired, 0)

        result.append(
            {
                "leave_type": _(leave_type),  # ✅ translated per user language
                "total_allocated": total_alloc,
                "expired": expired,
                "used": used,
                "pending": pending,
                "available": available,
            }
        )

    return result
