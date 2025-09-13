# your_app/api.py
import frappe
from frappe.utils.pdf import get_pdf


@frappe.whitelist()
def get_doc_pdf(doctype, docname, format="Standard"):
    """
    Generic API to generate PDF for any DocType
    :param doctype: DocType name (e.g. "Sales Invoice", "Salary Slip")
    :param docname: Document name (e.g. "SINV-0001", "SAL-PSL-0001")
    :param format: Print Format name (default = "Standard")
    """
    try:
        # Ensure the DocType exists
        if not frappe.db.exists(doctype, docname):
            return {"error": f"{doctype} {docname} not found"}

        # Get HTML using print format
        html_data = frappe.get_print(doctype, docname, print_format=format)

        # Convert to PDF
        pdf_file = get_pdf(html_data)

        # Return as downloadable file
        frappe.local.response.filename = f"{docname}.pdf"
        frappe.local.response.filecontent = pdf_file
        frappe.local.response.type = "download"
        return
    except Exception as e:
        frappe.local.response["http_status_code"] = 500
        return {"error": str(e)}


@frappe.whitelist()
def get_print_formats(doctype):
    """
    API to list available Print Formats for a given DocType (only mobile ones).
    :param doctype: DocType name (e.g. "Sales Invoice", "Salary Slip")
    :return: List of print formats with details
    """
    try:
        # Check if the DocType exists
        if not frappe.db.exists("DocType", doctype):
            return {"error": f"DocType {doctype} not found"}

        # Get all print formats marked for mobile for this doctype
        mobile_formats = frappe.get_all(
            "print format for mobile",
            filters={"doctype_name": doctype, "for_mobile": 1},
            fields=["print_format"],
        )

        # Extract only names
        format_names = [f["print_format"] for f in mobile_formats]

        # Fetch details from Print Format table
        formats = []
        if format_names:
            formats = frappe.get_all(
                "Print Format",
                filters={"name": ["in", format_names]},
                fields=["name", "custom_format", "disabled", "module"],
            )

        # Always add Standard as default
        formats.insert(
            0, {"name": "Standard", "custom_format": 0, "disabled": 0, "module": "Core"}
        )

        return {"doctype": doctype, "print_formats": formats}

    except Exception as e:
        frappe.local.response["http_status_code"] = 500
        return {"error": str(e)}
