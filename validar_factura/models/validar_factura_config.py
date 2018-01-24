# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields

class validar_factura_config(osv.osv):
    _name = 'validar_factura.config'

    _columns = {
        'partner_id': fields.many2one("res.partner", "Empresa"),
        'validar_oc': fields.boolean("Validar Orden de Compra"),
        'validar_tc': fields.boolean("Validar Tipo de cambio"),
        'validar_remision': fields.boolean("Permitir validar contra una remisión de entrada")
    }
    
    _defaults = {
        'validar_oc': True,
        'validar_tc': False,
        'validar_remision': False
    }

validar_factura_config()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: