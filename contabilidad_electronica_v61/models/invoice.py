# -*- encoding: utf-8 -*-
############################################################################
#    Module for OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Zenpar - http://www.zeval.com.mx/
#    All Rights Reserved.
############################################################################
#    Coded by: miguel.miguel@bias.com.mx
#    Manager: Eduardo Bayardo eduardo.bayardo@bias.com.mx
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
import decimal_precision as dp
from files import TempFileTransaction
import openssl
from datetime import date, datetime

class ResCompany(osv.osv):
    _inherit = 'res.company'

    _columns = {
        'conta_elect_version': fields.selection([
                ('1_1', 'Conta. Elect. 1.1'), 
                ('1_3', 'Conta. Elect. 1.3')],
            string='Conta. Elect. Versión', required=True)
    }

    _defaults = {
        'conta_elect_version': '1_1'
    }


class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def __compute_tipo_cambio(self, cr, uid, ids, field_names, arg=None, context=None,
                  query='', query_params=()):

        res = {}
        for inv_brw in self.browse(cr, uid, ids):
            tipo_cambio = 1.0
            if inv_brw.currency_id.name in ('MXN', 'MN'):
                tipo_cambio = 1.0
            else:
                WHERE = [('name', '=', 'MN' )]
                context = {'date':inv_brw.date_invoice or False}
                cur_obj = self.pool.get('res.currency')
                cur_id = cur_obj.search(cr, uid, WHERE, context=context)
                if cur_id:
                    tipo_cambio = cur_obj.browse(cr, uid, cur_id[0], context=context).rate
            res[inv_brw.id] = tipo_cambio
        return res

    _columns = {
        'tipo_cambio': fields.function(__compute_tipo_cambio, digits_compute=dp.get_precision('Account'), method=True, string='Tipo de Cambio'),
    }

    def get_temp_file_trans(self):
        return TempFileTransaction()
        
    def get_openssl(self):
        return openssl

    def _get_certificate(self, cr, uid, id, company_id):
        certificate_obj = self.pool.get("contabilidad.electronica.certificate")
        certificate_id = certificate_obj.search(cr, uid, ['&', 
            ('company_id','=', company_id.id), 
            ('end_date', '>', date.today().strftime("%Y-%m-%d"))
        ])
        if not certificate_id:
            raise osv.except_osv("Error", "No tiene certificados vigentes")
        certificate = certificate_obj.browse(cr, uid, certificate_id)[0]
        if not certificate.cer_pem or not certificate.key_pem:
            raise osv.except_osv("Error", "No esta el certificado y la llave en formato PEM")
        return certificate

    def create_move_comprobantes(self, cr, uid, ids, context=None):
        move_line_obj = self.pool.get("account.move.line")
        comp_obj = self.pool.get("contabilidad_electronica.comprobante")
        for inv_brw in self.browse(cr, uid, ids):
            if inv_brw.move_id and inv_brw.uuid and inv_brw.partner_id.vat:
                uuid = inv_brw.uuid
                for move_line in inv_brw.move_id.line_id:
                    vals = {
                        'monto': inv_brw.amount_total,
                        'uuid': uuid,
                        'rfc': inv_brw.partner_id.vat,
                        'move_line_id': move_line.id
                    }
                    if (inv_brw.currency_id.name != "MXN") or (inv_brw.currency_id.name != "MN"):
                        vals.update({
                            'moneda': inv_brw.currency_id.id,
                            'tipo_cambio': inv_brw.tipo_cambio
                        })
                    comp_ids = comp_obj.search(cr, uid, ['&',('uuid','=',uuid),('move_line_id','=',move_line.id)])
                    if len(comp_ids) > 0:
                        comp_obj.create(cr, uid, comp_ids, vals)
                    else:
                        comp_obj.create(cr, uid, vals)
        return True

account_invoice()


class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'

    def _default_account_id(self, cr, uid, context=None):
        # XXX this gets the default account for the user's company,
        # it should get the default account for the invoice's company
        # however, the invoice's company does not reach this point
        if context is None:
            context = {}
        if context.get('type') in ('out_invoice','out_refund'):
            prop = self.pool.get('ir.property').get(cr, uid, 'property_account_income_categ', 'product.category', context=context)
        else:
            prop = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category', context=context)
        return prop and prop.id or False

account_invoice_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: