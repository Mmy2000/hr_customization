import frappe
from frappe.utils import format_time, today, getdate
from frappe import _
import datetime
import calendar

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

    # --- build date range ---
    start_date, end_date = get_month_date_range(year, month)

    # --- get attendance records ---
    filters = {}
    if employee:
        filters["employee"] = employee
    if company:
        filters["company"] = company
    filters["attendance_date"] = ["between", [start_date, end_date]]

    attendance_records = frappe.get_all(
        "Attendance",
        filters=filters,
        fields=["attendance_date", "status"],
    )

    attendance_map = {getdate(r.attendance_date): r.status for r in attendance_records}

    # --- get holidays and weekly offs dynamically from system ---
    holidays, weekly_offs = get_holidays_and_weekly_offs(
        employee, company, start_date, end_date
    )

    # --- build complete attendance list ---
    result = []
    current_date = start_date
    while current_date <= end_date:
        day_status = attendance_map.get(current_date)

        if not day_status:
            if current_date in holidays:
                day_status = "Holiday | H"
            elif current_date in weekly_offs:
                day_status = "Weekly Off | WO"
            else:
                day_status = "Absent | A"

        result.append({"date": current_date, "status": day_status})
        current_date += datetime.timedelta(days=1)

    return {"message": "Success", "data": result}


def get_holidays_and_weekly_offs(employee, company, start_date, end_date):
    """Return separate lists of public holidays and weekly offs based on the system Holiday List."""

    # get holiday list assigned to employee or company
    holiday_list = frappe.db.get_value("Employee", employee, "holiday_list")
    if not holiday_list and company:
        holiday_list = frappe.db.get_value("Company", company, "default_holiday_list")

    if not holiday_list:
        return [], []  # no holiday list configured

    # fetch all holidays for the month
    holidays_data = frappe.get_all(
        "Holiday",
        filters={
            "parent": holiday_list,
            "holiday_date": ["between", [start_date, end_date]],
        },
        fields=["holiday_date", "weekly_off"],
    )

    holidays = []
    weekly_offs = []
    for h in holidays_data:
        date = getdate(h.holiday_date)
        if h.weekly_off:
            weekly_offs.append(date)
        else:
            holidays.append(date)

    return holidays, weekly_offs


def get_month_date_range(year, month_name):

    month_number = list(calendar.month_name).index(month_name)
    start_date = datetime.date(int(year), month_number, 1)
    last_day = calendar.monthrange(int(year), month_number)[1]
    end_date = datetime.date(int(year), month_number, last_day)
    return [start_date, end_date]
