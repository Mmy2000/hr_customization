import frappe
from frappe.auth import LoginManager
from frappe import _
import random
import requests


@frappe.whitelist(allow_guest=True)
def mobile_login(usr, pwd):
    user_doc = frappe.get_doc("User", usr)
    roles = [role.role for role in user_doc.roles]

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


@frappe.whitelist(allow_guest=True)
def generate_employee_otp(email):
    """Generate a random OTP for the given user email"""
    # Check if user exists
    user = frappe.get_value("User", {"email": email}, "name")
    if not user:
        frappe.throw(_("User not found for email: {0}").format(email))

    # Generate random 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # Check if an OTP record already exists for this user
    otp_doc = frappe.get_all("Employee OTP", filters={"user": user}, fields=["name"])
    if otp_doc:
        # Update existing OTP
        doc = frappe.get_doc("Employee OTP", otp_doc[0].name)
        doc.otp_code = otp
        doc.save(ignore_permissions=True)
    else:
        # Create new OTP record
        doc = frappe.get_doc({"doctype": "Employee OTP", "user": user, "otp_code": otp})
        doc.insert(ignore_permissions=True)

    frappe.db.commit()

    frappe.sendmail(
        recipients=email,
        subject="Your OTP Code",
        message=f"Your OTP is {otp}",
        now=True,
    )
    name = frappe.get_value("User", user, "first_name")
    phone_number = frappe.get_value(
        "User", user, "mobile_no"
    )  # Assuming 'phone' field exists
    if phone_number:
        send_whatsapp_message(phone_number,name,otp)
    else:
        frappe.log_error("User phone number not found", "WhatsApp OTP")

    return {"message": "OTP generated successfully"}


@frappe.whitelist(allow_guest=True)
def verify_employee_otp(email, otp):
    """Check if OTP is correct for the given user email"""
    user = frappe.get_value("User", {"email": email}, "name")
    if not user:
        frappe.throw(_("User not found for email: {0}").format(email))

    # Get the OTP record
    record = frappe.get_value("Employee OTP", {"user": user, "otp_code": otp}, "name")

    if record:
        # Optional: delete or clear OTP after successful verification
        frappe.delete_doc("Employee OTP", record, ignore_permissions=True)
        frappe.db.commit()
        return {"verified": True, "message": "OTP verified successfully"}
    else:
        return {"verified": False, "message": "Invalid OTP"}


WHATSAPP_API_URL = "https://graph.facebook.com/v22.0/{phone_number_id}/messages"
ACCESS_TOKEN = "EAAReaRG2IZB4BO8ryyzSbRCxYImVWEjHxIdtCSON4zfyO4KiKyiDZAkW0igZCTZA1KPidF7lEQCn8rddg5ViSaZBiX0ZCoQnrebkBGdlXZCaHZCirUxqwvKshIPhhPv6fgm6BCDKWI9bR4sDJUfm6IhRHdGqQyBTkeeX71xEMzD3kRC326xGQ1DjMLzGIUfDdzjNwwZDZD"
PHONE_NUMBER_ID = "715406844979744"


def send_whatsapp_message(phone_number, name, otp):
    url = WHATSAPP_API_URL.format(phone_number_id=PHONE_NUMBER_ID)
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": "otp",  # template name (must match exactly)
            "language": {"code": "en"},  # or use "ar" if the template is in Arabic
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": name},  # {{1}}
                        {"type": "text", "text": otp},  # {{2}}
                    ],
                }
            ],
        },
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print("WhatsApp message sent:", response.json())
        frappe.logger().info(f"WhatsApp message sent: {response.json()}")
    else:
        print("WhatsApp send failed:", response.text)
        frappe.logger().error(f"WhatsApp message failed: {response.text}")
