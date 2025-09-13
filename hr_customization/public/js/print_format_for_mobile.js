
frappe.ui.form.on('print format for mobile', {
    refresh: function(frm) {
        frm.set_query('print_format', function() {
            if (frm.doc.doctype_name) {
                return {
                    filters: {
                        'doc_type': frm.doc.doctype_name
                    }
                }
            } else {
                return {};
            }
        });
    },

    doctype_name: function(frm) {
        frm.set_value('print_format', null);
    }
});
