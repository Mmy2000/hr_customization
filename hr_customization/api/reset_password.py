import frappe
from frappe import _
from frappe.core.doctype.user.user import reset_password

@frappe.whitelist(allow_guest=True)
def request_password_reset(email):
    """Send password reset link to user email"""
    try:
        user = frappe.get_doc("User", email)
        if not user.enabled:
            return {"success": False, "error": _("User account is disabled.")}

        reset_password(user.name)  # This creates reset key + sends email

        return {"success": True, "message": _("Password reset email sent.")}
    except frappe.DoesNotExistError:
        return {"success": False, "error": _("User not found.")}
    except Exception as e:
        return {
            "success": False,
            "error": _("An unexpected error occurred."),
            "details": str(e),
        }


@frappe.whitelist(allow_guest=True)
def reset_password_api(key, new_password):
    """Reset password using reset key"""
    try:

        # This version of reset_password works with key + new password
        user = reset_password(key, new_password=new_password)

        return {"success": True, "message": _("Password has been reset."), "user": user}
    except Exception as e:
        return {
            "success": False,
            "error": _("Invalid or expired reset key."),
            "details": str(e),
        }
