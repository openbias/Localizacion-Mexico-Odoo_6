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
from tools.translate  import _

class account_bank_statement_line(osv.osv):
    _inherit = 'account.bank.statement.line'

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        res = super(account_bank_statement_line, self).onchange_partner_id(cr, uid, ids, partner_id, context=context)
        res.setdefault("domain", {})["cuenta_destino"] = [('partner_id', '=', partner_id)]
        return res

    _columns = {
        'cuenta_destino': fields.many2one("res.partner.bank", string="Cuenta destino"),
        'cuenta_origen': fields.many2one("res.partner.bank", string="Cuenta origen"),
        'type': fields.selection([
            ('supplier','Supplier'),
            ('customer','Customer'),
            ('general','General'),
            ('traspaso', 'Traspaso')
            ], 'Type', required=True), 
    }


account_bank_statement_line()


class account_bank_statement(osv.osv):
    _inherit = 'account.bank.statement'

    def create_move_from_st_line(self, cr, uid, st_line_id, company_currency_id, st_line_number, context=None):
        user_company_id = self.pool.get("res.users").browse(cr, uid, uid).company_id
        move_id = super(account_bank_statement, self).create_move_from_st_line(cr, uid, st_line_id, company_currency_id, st_line_number, context=context)
        st_line_obj = self.pool.get("account.bank.statement.line")
        invoice_obj = self.pool.get("account.invoice")
        move_line_obj = self.pool.get("account.move.line")
        move_obj = self.pool.get("account.move")
        bank_obj = self.pool.get("res.partner.bank")
        st_line = st_line_obj.browse(cr, uid, st_line_id)
        move = move_obj.browse(cr, uid, move_id)
        res = bank_obj.search(cr, uid, [('journal_id','=',st_line.statement_id.journal_id.id)])
        cuenta_origen = cuenta_destino = False
        if res:
            cuenta_extracto = bank_obj.browse(cr, uid, res[0])
        else:
            cuenta_extracto = None
        if st_line.type == 'traspaso':
            if st_line.cuenta_destino and st_line.cuenta_origen:
                cuenta_origen = st_line.cuenta_origen
                cuenta_destino = st_line.cuenta_destino
            else:
                raise osv.except_osv("Error", "Favor de llenar cuenta origen y destino")
            for move_line in move.line_id:
                if cuenta_origen and cuenta_destino:
                    vals = {
                        'cta_ori': cuenta_origen.id,
                        'monto': st_line.amount,
                        'cta_dest': cuenta_destino.id,
                        'fecha': st_line.date,
                        'move_line_id': move_line and move_line.id or False
                    }
                    self.pool.get("contabilidad_electronica.transferencia").create(cr, uid, vals)
        return move_id


account_bank_statement()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: