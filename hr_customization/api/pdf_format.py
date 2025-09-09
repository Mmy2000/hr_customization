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
    API to list all available Print Formats for a given DocType
    :param doctype: DocType name (e.g. "Sales Invoice", "Salary Slip")
    :return: List of print formats
    """
    try:
        # Check if the DocType exists
        if not frappe.db.exists("DocType", doctype):
            return {"error": f"DocType {doctype} not found"}

        # Fetch all print formats linked to this DocType
        formats = frappe.get_all(
            "Print Format",
            filters={"doc_type": doctype},
            fields=["name", "custom_format", "disabled", "module"],
        )

        # Add Standard as default (ERPNext always supports it)
        formats.insert(
            0, {"name": "Standard", "custom_format": 0, "disabled": 0, "module": "Core"}
        )

        return {"doctype": doctype, "print_formats": formats}

    except Exception as e:
        frappe.local.response["http_status_code"] = 500
        return {"error": str(e)}
