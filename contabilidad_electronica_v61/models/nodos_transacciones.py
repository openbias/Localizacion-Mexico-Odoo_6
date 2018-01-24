# -*- encoding: utf-8 -*-
############################################################################
#    Module for OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Zenpar - http://www.zeval.com.mx/
#    All Rights Reserved.
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
#############################################################################

from osv import osv, fields

class comprobante(osv.osv):
    _name = 'contabilidad_electronica.comprobante'
    _description = "Nodo comprobante nacional (anexo 24)"
    _rec_name = 'move_line_id'

    _columns = {
        'uuid': fields.char("UUID CFDI", size=36, required=True),
        'monto': fields.float("Monto", required=True),
        'rfc': fields.char("RFC", size=13, required=True),
        'moneda': fields.many2one("res.currency", string="Moneda"),
        'tipo_cambio': fields.float("Tipo de cambio"),
        'move_line_id': fields.many2one("account.move.line", required=True, string=u"Transacción", ondelete="cascade"),
        'move_line_name': fields.related("move_line_id", "name", type="char", size=254, string=u"Transacción")
    }

comprobante()

class comprobante_otro(osv.osv):
    _name = 'contabilidad_electronica.comprobante.otro'
    _description = "Nodo comprobante nacional CFD o CBB (anexo 24)"
    _rec_name = 'move_line_id'
    
    _columns = {
        'serie': fields.char("Serie", size=64),
        'folio': fields.char("Folio", size=64, required=True),
        'rfc':fields.char("RFC", size=13, required=True),
        'monto': fields.float("Monto", required=True),
        'moneda': fields.many2one("res.currency", string="Moneda"),
        'tipo_cambio': fields.float("Tipo de cambio"),
        'move_line_id': fields.many2one("account.move.line", required=True, string=u"Transacción", ondelete="cascade"),
        'move_line_name': fields.related("move_line_id", "name", type="char", size=64, string=u"Transacción")
    }

comprobante_otro()

class comprobante_extranjero(osv.osv):
    _name = 'contabilidad_electronica.comprobante.ext'
    _description = "Nodo comprobante extranjero (anexo 24)"
    _rec_name = 'move_line_id'
    
    _columns = {
        'num': fields.char(u"Numero del comprobante", size=64, required=True),
        'tax_id': fields.char(u"Identificador contribuyente", size=64),
        'monto': fields.float("Monto", required=True),
        'moneda': fields.many2one("res.currency", string="Moneda"),
        'tipo_cambio': fields.float("Tipo de cambio"),
        'move_line_id': fields.many2one("account.move.line", required=True, string=u"Transacción", ondelete="cascade"),
        'move_line_name': fields.related("move_line_id", "name", type="char", size=64, string=u"Transacción")
    }
comprobante_extranjero()


class transferencia(osv.osv):
    _name = 'contabilidad_electronica.transferencia'
    _description = "Nodo transferencia bancaria (anexo 24)"
    _rec_name = 'move_line_id'
    
    _columns = {
        'cta_ori': fields.many2one("res.partner.bank", string="Cuenta origen", required=True),
        'monto': fields.float("Monto", required=True),
        "cta_dest": fields.many2one("res.partner.bank", string="Cuenta destino", required=True),
        'fecha': fields.date("Fecha", required=True),
        'moneda': fields.many2one("res.currency", string="Moneda"),
        'tipo_cambio': fields.float("Tipo de cambio"),
        'move_line_id': fields.many2one("account.move.line", required=True, string=u"Transaccion", ondelete="cascade"),
        'move_line_name': fields.related("move_line_id", "name", type="char", size=64, string=u"Transacción")
    }

transferencia()

class cheque(osv.osv):
    _name = "contabilidad_electronica.cheque"
    _description = "Nodo cheque (anexo 24)"
    _rec_name = 'move_line_id'
    
    _columns = {
        'num': fields.char(u"Numero del cheque", size=64, required=True),
        'cta_ori': fields.many2one("res.partner.bank", string="Cuenta origen", required=True),
        'fecha': fields.date("Fecha", required=True),
        'monto': fields.float("Monto", required=True),
        "benef": fields.many2one("res.partner", string="Beneficiario", required=True),
        'moneda': fields.many2one("res.currency", string="Moneda"),
        'tipo_cambio': fields.float("Tipo de cambio"),
        'move_line_id': fields.many2one("account.move.line", required=True, string=u"Transacción", ondelete="cascade"),
        'move_line_name': fields.related("move_line_id", "name", type="char", size=64, string=u"Transacción")
    }

cheque()

class otro_metodo_pago(osv.osv):
    _name = "contabilidad_electronica.otro.metodo.pago"
    _description = "Nodo otro metodo de pago (anexo 24)"
    _rec_name = "metodo"
    _rec_name = 'move_line_id'

    _columns = {
        'metodo': fields.many2one("contabilidad.electronica.metodo.pago", string=u"Método de pago", required=True),
        'monto': fields.float("Monto", required=True),
        'fecha': fields.date("Fecha", required=True),
        'benef': fields.many2one("res.partner", string="Beneficiario", required=True),
        'moneda': fields.many2one("res.currency", string="Moneda"),
        'tipo_cambio': fields.float("Tipo de cambio"),
        'move_line_id': fields.many2one("account.move.line", required=True, string=u"Transacción", ondelete="cascade"),
        'move_line_name': fields.related("move_line_id", "name", type="char", size=64, string=u"Transacción")
    }


otro_metodo_pago()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: