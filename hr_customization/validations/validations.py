import re
from frappe import _
import frappe
from frappe.utils import strip_html


def validate_password_strength(password):
    """Validate password based on required rules."""

    # Minimum length 8
    if len(password) < 8:
        return _("Password must be at least 8 characters long.")

    # Uppercase letter
    if not re.search(r"[A-Z]", password):
        return _("Password must contain at least one uppercase letter.")

    # Lowercase letter
    if not re.search(r"[a-z]", password):
        return _("Password must contain at least one lowercase letter.")

    # Number
    if not re.search(r"[0-9]", password):
        return _("Password must contain at least one number.")

    # Allowed special characters
    if not re.search(r"[~$*&#@!]", password):
        return _("Password must contain at least one special character: ~ $ * & # @ !")

    # Passed all checks
    return None


def handle_request_error(error):
    """Convert raw ERPNext errors into clean readable messages"""

    msg = str(error)

    # ---- Specific HRMS Errors ----
    if "OverlappingAttendanceRequestError" in msg:
        frappe.throw(
            _(
                "This employee already has an attendance request overlapping with this period."
            )
        )

    if "Overlapping Leave Application" in msg:
        frappe.throw(
            _("You already have a leave application overlapping with these dates.")
        )

    if "Attendance is already marked" in msg:
        frappe.throw(_("Attendance is already marked for this date."))

    if "Overlapping Shift Assignment" in msg:
        frappe.throw(
            _(
                "You already have a shift assignment that overlaps with the selected period."
            )
        )

    if "Leave Approver Missing" in msg:
        frappe.throw(_("A leave approver is required for this request."))

    if "does not belong to company" in msg:
        frappe.throw(_("This employee is not linked to the selected company."))

    if "Duplicate" in msg or "already exists" in msg:
        frappe.throw(_("This request already exists."))

    # ---- Default fallback (clean HTML) ----
    clean = strip_html(msg)
    frappe.throw(_(clean))
