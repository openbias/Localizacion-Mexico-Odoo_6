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

import pickle

from osv import osv, fields
from osv.orm import except_orm
from tools.safe_eval import safe_eval as eval


class ir_values(osv.osv):
    _inherit = 'ir.values'

    def get_default(self, cr, uid, model, field_name, for_all_users=True, company_id=False, condition=False):
        """ Return the default value defined for model, field_name, users, company and condition.
            Return ``None`` if no such default exists.
        """
        search_criteria = [
            ('key', '=', 'default'),
            ('key2', '=', condition and condition[:200]),
            ('model', '=', model),
            ('name', '=', field_name),
            ('user_id', '=', False if for_all_users else uid),
            ('company_id','=', company_id)
            ]
        defaults = self.browse(cr, uid, self.search(cr, uid, search_criteria))
        return pickle.loads(defaults[0].value.encode('utf-8')) if defaults else None

ir_values()

class account_account(osv.osv):
    _inherit = 'account.account'

    _columns = {
        'codigo_agrupador': fields.many2one("contabilidad_electronica_codigo_agrupador", string=u"Codigo agrupador SAT"),
        'naturaleza': fields.many2one("contabilidad_electronica_naturaleza", string="Naturaleza")
    }

account_account()


class account_move_line(osv.osv):
    _inherit = "account.move.line"
    
    _columns = {
        'comprobantes': fields.one2many("contabilidad_electronica.comprobante", "move_line_id", string="Comprobantes", ondelete="cascade"),
        'comprobantes_cfd_cbb': fields.one2many("contabilidad_electronica.comprobante.otro", "move_line_id", string="Comprobantes (CFD o CBB)", ondelete="cascade"),
        'comprobantes_ext': fields.one2many("contabilidad_electronica.comprobante.ext", "move_line_id", string="Comprobantes extranjeros", ondelete="cascade"),
        'cheques': fields.one2many("contabilidad_electronica.cheque", "move_line_id", string="Cheques", ondelete="cascade"),
        'transferencias': fields.one2many("contabilidad_electronica.transferencia", "move_line_id", string="Transferencias", ondelete="cascade"),
        'otros_metodos': fields.one2many("contabilidad_electronica.otro.metodo.pago", "move_line_id", string=u"Otros métodos de pago", ondelete="cascade"),
    }

    # Funcion para actualizar los nodos de la contabilidad electronica de los pagos
    #
    # Del anexo 24: "Se considera que se debe indentificar el soporte documental
    # tanto en la provisión como en el pago y/o cobro de cada una de las cuentas
    # y subcuentas que se vean afectadas"        
    def create_move_comprobantes_pagos(self, cr, uid, ids, context=None):
        move_obj = self.pool.get("account.move")
        move_line_obj = self.pool.get("account.move.line")
        comp_obj = self.pool.get("contabilidad_electronica.comprobante")
        for move_line in self.browse(cr, uid, ids):
            invoice = False
            if move_line.reconcile_id:
                for line in move_line.reconcile_id.line_id:
                    if line.invoice:
                        invoice = line.invoice
                        break
            elif move_line.reconcile_partial_id:
                for line in move_line.reconcile_partial_id.line_partial_ids:
                    if line.invoice:
                        invoice = line.invoice
                        break
            if not invoice:
                continue
            if invoice.uuid and invoice.partner_id.vat:
                uuid = invoice.uuid
                # uuid = uuid[0:8]+'-'+uuid[8:12]+'-'+uuid[12:16]+'-'+uuid[16:20]+'-'+uuid[20:32]
                vals = {
                    'uuid': uuid,
                    'rfc': invoice.partner_id.vat,
                    'monto': invoice.amount_total,
                    'move_line_id': move_line.id
                }
                if invoice.currency_id.name not in ('MN', 'MXN'):
                    vals.update({
                        'moneda': invoice.currency_id.id,
                        'tipo_cambio': invoice.tipo_cambio
                    })
                if not comp_obj.search(cr, uid, [('uuid','=',uuid),('move_line_id','=',move_line.id)]):
                    comp_obj.create(cr, uid, vals)
        return True


account_move_line()


class account_move(osv.osv):
    _inherit = "account.move"
    
    def _get_tipo_poliza(self, cr, uid, ids, fields, args, context=None):
        res = {}
        tipo = '3'
        for move in self.browse(cr, uid, ids):
            if move.journal_id.type == 'bank':
                if move.journal_id.default_debit_account_id.id != move.journal_id.default_credit_account_id.id:
                    raise osv.except_osv("Warning", 
                      u"La cuenta deudora por defecto y la cuenta acreedora por defecto no son la misma en el diario %s"%move.journal_id.name)
                if len(move.line_id) == 2:
                    if move.line_id[0].account_id.user_type.code == 'bank' and move.line_id[0].account_id.user_type.code == 'bank':
                        tipo = '3'
                        break
                for line in move.line_id:
                    if line.account_id.id == move.journal_id.default_debit_account_id.id:
                        if line.debit != 0 and line.credit == 0:
                            tipo = '1'
                            break
                        elif line.debit == 0 and line.credit != 0:
                            tipo = '2'
                            break
            else:
                tipo = '3'
            res[move.id] = tipo
        return res
            
    _columns = {
        'tipo_poliza': fields.function(_get_tipo_poliza, type="selection", selection=[
            ('1', 'Ingresos'),
            ('2', 'Egresos'),
            ('3', 'Diario'),
        ], string=u"Tipo póliza", method=True, store=True)
    }
    
    _defaults = {
        'tipo_poliza': '3'
    }


account_move()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: