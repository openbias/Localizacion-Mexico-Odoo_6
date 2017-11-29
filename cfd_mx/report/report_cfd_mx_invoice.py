 #-*- coding: utf-8 -*-

import time
from report import report_sxw
from osv import osv

class report_cfd_mx_invoice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_cfd_mx_invoice, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })
        
report_sxw.report_sxw('report.cfd_mx.invoice',
                       'account.invoice', 
                       'addons/cfd_mx/report/report_cfd_mx_invoice.mako',
                       parser=report_cfd_mx_invoice)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: