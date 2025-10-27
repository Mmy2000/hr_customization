import frappe

import firebase_admin
from firebase_admin import credentials, messaging

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


def initialize_firebase():
    if not firebase_admin._apps:
        service_account_path = frappe.get_site_path(
            frappe.conf.get("firebase_service_account")
        )
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)


@frappe.whitelist(allow_guest=False)
def send_push_notification(
    user=None, title="Notification", body="You have a new message"
):
    initialize_firebase()

    if not user:
        user = frappe.session.user

    doc_name = frappe.db.exists("FCM Token", {"user": user})
    if not doc_name:
        frappe.throw("No FCM token found for this user.")

    token = frappe.get_value("FCM Token", doc_name, "fcm_token")

    # Construct notification message
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body), token=token
    )
    # Send notification
    response = messaging.send(message)
    return {"message": "Notification sent successfully", "response": response}


def trigger_notification_fcm(doc, method):
    """
    Automatically triggered when a Notification Log is created.
    Sends push notification to the user.
    """

    if not doc.for_user:
        return  # Ensure there's a target user

    title = doc.subject or "New Notification"
    body = doc.email_content or doc.type or "You have a new notification."

    # Reuse your existing method (session.user isn't needed since we pass target user)
    try:
        send_push_notification(user=doc.for_user, title=title, body=body)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "FCM Push Send Error")


# def trigger_notification_fcm(doc, method):
#     """
#     Triggered after insert of Notification Log (or any doctype).
#     Enqueues FCM notification to be sent asynchronously.
#     """
#     if not doc.for_user:
#         return

#     title = doc.subject or "New Notification"
#     body = doc.email_content or doc.type or "You have a new notification."

#     # Enqueue sending, runs in background
#     frappe.enqueue(
#         "hr_customization.api.fcm_token.send_push_notification",
#         queue="default",  # Or 'short' if quick tasks, or 'long' if heavy
#         user=doc.for_user,
#         title=title,
#         body=body,
#         now=False,  # Ensures it runs asynchronously
#     )
