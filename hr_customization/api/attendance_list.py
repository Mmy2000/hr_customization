import frappe
from frappe.utils import format_time, today
from frappe import _


@frappe.whitelist()
def get_attendance_list():
    user = frappe.session.user
    user_lang = frappe.db.get_value("User", user, "language") or frappe.local.lang
    frappe.local.lang = user_lang

    # Get employee linked to user
    employee = frappe.get_value("Employee", {"user_id": user}, "name")
    if not employee:
        frappe.throw(_("No Employee linked with this user."))

    # Fetch all attendance records
    attendance_list = frappe.get_all(
        "Attendance",
        filters={"employee": employee},
        fields=["*"],
        order_by="attendance_date desc",
    )

    # Translate string fields in each record
    translated_attendance = []
    for record in attendance_list:
        translated_record = {}
        for k, v in record.items():
            translated_record[k] = _(v) if isinstance(v, str) else v
        translated_attendance.append(translated_record)

    return translated_attendance


@frappe.whitelist()
def get_check_in_and_out_times():

    user = frappe.session.user
    user_lang = frappe.db.get_value("User", user, "language") or frappe.local.lang
    frappe.local.lang = user_lang
    employee_id = frappe.get_value("Employee", {"user_id": user}, "name")
    # Get today's date
    today_date = today()

    # Fetch attendance records for the employee for today
    attendance_records = frappe.get_all(
        "Employee Checkin",
        filters={"employee": employee_id},
        fields=['*'],
    )

    translated_records = []
    for rec in attendance_records:
        translated = {}
        for k, v in rec.items():
            translated[k] = _(v) if isinstance(v, str) else v
        translated_records.append(translated)

    return {"attendance_records": translated_records}


@frappe.whitelist(allow_guest=False)
def get_monthly_attendance(month, year, employee=None, company=None):
    filters = {}
    if employee:
        filters["employee"] = employee
    if company:
        filters["company"] = company
    if month and year:
        filters["attendance_date"] = ["between", get_month_date_range(year, month)]

    records = frappe.get_all(
        "Attendance",
        filters=filters,
        fields=["employee", "employee_name", "attendance_date", "status", "company"],
        order_by="attendance_date asc",
    )

    return {"message": "Success", "data": records}


def get_month_date_range(year, month_name):
    import calendar
    import datetime

    month_number = list(calendar.month_name).index(month_name)
    start_date = datetime.date(int(year), month_number, 1)
    last_day = calendar.monthrange(int(year), month_number)[1]
    end_date = datetime.date(int(year), month_number, last_day)
    return [start_date, end_date]
