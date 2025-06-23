import frappe
from frappe.auth import LoginManager
from frappe import _


@frappe.whitelist(allow_guest=True)
def mobile_login(usr, pwd):
    user_doc = frappe.get_doc("User", usr)
    roles = [role.role for role in user_doc.roles]
    print(roles)

    if "Employee Self Service" not in roles:
        frappe.local.response.http_status_code = 403
        frappe.local.response.update(
            {
                "status": "error",
                "message": _("You are not authorized to log in from the mobile app."),
            }
        )
        return

    login_manager = LoginManager()
    login_manager.authenticate(user=usr, pwd=pwd)
    login_manager.post_login()

    frappe.local.response.update(
        {
            "status": "success",
            "message": "Login successful",
            "sid": frappe.session.sid,
            "user": usr,
        }
    )
    return
