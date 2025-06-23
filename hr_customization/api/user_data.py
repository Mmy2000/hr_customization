import frappe
from frappe import _
from frappe.utils.file_manager import save_file


@frappe.whitelist()
def get_user_details():
    try:
        user_email = frappe.session.user
        user = frappe.get_doc("User", user_email)
        return {
            "email": user.email,
            "first_name": user.first_name,
            "middle_name": user.middle_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "username": user.username,
            "language": user.language,
            "time_zone": user.time_zone,
            "image": user.user_image,
        }
    except frappe.DoesNotExistError:
        frappe.throw(_("User not found"), frappe.DoesNotExistError)



@frappe.whitelist()
def update_user_details(
    first_name=None, middle_name=None, last_name=None, language=None, time_zone=None
):
    try:
        user_email = frappe.session.user
        user = frappe.get_doc("User", user_email)

        # Handle standard fields
        if first_name:
            user.first_name = first_name
        if middle_name:
            user.middle_name = middle_name
        if last_name:
            user.last_name = last_name
        if language:
            user.language = language
        if time_zone:
            user.time_zone = time_zone

        # Handle file upload (from form-data)
        file = frappe.request.files.get("user_image")
        if file:
            saved_file = save_file(
                fname=file.filename,
                content=file.stream.read(),
                dt="User",
                dn=user.name,
                is_private=0,
            )

            user.user_image = saved_file.file_url

        user.save()
        frappe.db.commit()

        user_data = {
            "email": user.email,
            "first_name": user.first_name,
            "middle_name": user.middle_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "username": user.username,
            "language": user.language,
            "time_zone": user.time_zone,
            "user_image": user.user_image,
        }

        return {"message": "User updated successfully", "user": user_data}

    except frappe.DoesNotExistError:
        frappe.throw(_("User not found"), frappe.DoesNotExistError)

