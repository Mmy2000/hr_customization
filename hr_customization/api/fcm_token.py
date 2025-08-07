import frappe


@frappe.whitelist(allow_guest=False)
def get_fcm_token():
    user = frappe.session.user
    doc_name = frappe.db.exists("FCM Token", {"user": user})
    if not doc_name:
        return {"fcm_token": None}

    doc = frappe.get_doc("FCM Token", doc_name)
    return {"fcm_token": doc.fcm_token}


@frappe.whitelist(allow_guest=False)
def save_fcm_token(token: str):
    user = frappe.session.user

    existing = frappe.db.exists("FCM Token", {"user": user})
    if existing:
        doc = frappe.get_doc("FCM Token", existing)
        doc.fcm_token = token
        doc.save(ignore_permissions=True)
    else:
        frappe.get_doc(
            {"doctype": "FCM Token", "user": user, "fcm_token": token}
        ).insert(ignore_permissions=True)

    return {"message": "FCM token saved successfully"}
