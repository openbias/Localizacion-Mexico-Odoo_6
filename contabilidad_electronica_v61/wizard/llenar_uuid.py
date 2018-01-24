#-*- coding: utf-8 -*-
from osv import osv, fields

class llenar_uuid(osv.osv_memory):
    _name = "contabilidad_electronica.wizard.llenar.uuid"
    
    def action_llenar_uuid(self, cr, uid, ids, context=None):
        #Facturas
        invoice_obj = self.pool.get("account.invoice")
        all_invoices = invoice_obj.search(cr, uid, [('state','!=','draft'), ('uuid', '!=', False), ('move_id', '!=', False), ('date_invoice', '>=', '2015-05-01')])
        print len(all_invoices)
        try:
            invoice_obj.create_move_comprobantes(cr, uid, all_invoices)
        except Exception, msg:
            raise osv.except_osv(('Error in XML'), ("Error message: %s" %(msg, )))
        #Pagos
        voucher_obj = self.pool.get("account.voucher")
        all_vouchers = voucher_obj.search(cr, uid, [])
        n = 1 
        N = len(all_vouchers)
        for voucher in voucher_obj.browse(cr, uid, all_vouchers):
            n += 1
            move_ids = [x.id for x in voucher.move_ids]
            self.pool.get("account.move.line").create_move_comprobantes_pagos(cr, uid, move_ids)            
        return True

llenar_uuid()        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: