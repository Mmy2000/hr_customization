import frappe
from frappe import _
from hr_customization.validations.validations import validate_password_strength

@frappe.whitelist(allow_guest=False)
def change_password(old_password, new_password):
    try:
        user_email = frappe.session.user
        user = frappe.get_doc("User", user_email)

        # Verify old password
        if not frappe.utils.password.check_password(user.name, old_password):
            return {"success": False, "error": _("Incorrect old password.")}

        # -------------------------------
        # Use the validator function
        # -------------------------------
        validation_error = validate_password_strength(new_password)
        if validation_error:
            return {"success": False, "error": validation_error}

        # Update password
        frappe.utils.password.update_password(user.name, new_password)
        user.save()
        frappe.db.commit()

        return {"success": True, "message": _("Password updated successfully.")}

    except frappe.DoesNotExistError:
        return {"success": False, "error": _("User not found.")}
    except frappe.AuthenticationError:
        return {
            "success": False,
            "error": _("Authentication failed. Please try again."),
        }
    except Exception as e:
        return {
            "success": False,
            "error": _("An unexpected error occurred. Please contact support."),
            "details": str(e),
        }
