import frappe
from frappe.desk.doctype.notification_log.notification_log import get_notification_logs
from frappe.utils import cint


@frappe.whitelist()
def list_notifications():
    logs = get_notification_logs().get("notification_logs", [])

    for log in logs:
        if log.get("from_user"):
            from_user_image = frappe.db.get_value(
                "User", log["from_user"], "user_image"
            )
            log["from_user_image"] = from_user_image or ""  # fallback image
        else:
            log["user_image"] = ""

        if log.get("for_user"):
            for_user_image = frappe.db.get_value("User", log["for_user"], "user_image")
            log["for_user_image"] = for_user_image or ""  # fallback image
        else:
            log["for_user_image"] = ""

    return logs


@frappe.whitelist()
def mark_notification_as_read(notification_id):
    if not notification_id:
        frappe.throw("Notification ID is required")

    notification = frappe.get_doc("Notification Log", notification_id)

    if cint(notification.read) == 1:
        frappe.throw("This notification is already read")
    else:
        notification.db_set("read", 1, update_modified=False)
        frappe.db.commit()

    return {"status": "success", "message": "Notification marked as read"}


@frappe.whitelist()
def get_user_activity(user=None, limit=20):
    if not user:
        user = frappe.session.user

    activity_logs = frappe.get_all(
        "Activity Log",
        filters={"owner": user},
        fields=["*"],
        order_by="creation desc",
        limit_page_length=limit,
    )

    return activity_logs
