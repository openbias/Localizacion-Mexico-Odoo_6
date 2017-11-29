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

class contabilidad_electronica_naturaleza(osv.osv):
    _name = "contabilidad_electronica_naturaleza"
    _description = "Naturaleza cuenta (catalogo anexo 24)"

    _columns = {
        'name': fields.char("Naturaleza", size=64, required=True),
        'code': fields.char(u"Codigo", size=64, required=True)
    }

contabilidad_electronica_naturaleza()


class contabilidad_electronica_codigo_agrupador(osv.osv):
    _name = "contabilidad_electronica_codigo_agrupador"
    _description = "Codigo agrupador (catalogo anexo 24)"
    _rec_name = 'description'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []
        res = []
        for rec in self.browse(cr, uid, ids):
            name = "[%s] %s"%(rec.name, rec.description)
            res.append((rec.id, name))
        return res

    
    _columns= {
        'name': fields.char(u"Codigo", size=64, required=True),
        'description': fields.text(u'Descripción'),
        'nivel': fields.integer("Nivel")
    }

contabilidad_electronica_codigo_agrupador()

class banco(osv.osv):
    _inherit = "res.bank"
    
    _columns = {
        'code_sat': fields.char(u"Código SAT", size=128, required=True),
        'razon_social': fields.text(u"Razón social"),
        'extranjero': fields.boolean("Banco extranjero")
    }

banco()

class metodo_de_pago(osv.osv):
    _name = "contabilidad.electronica.metodo.pago"
    _description = "Metodo de pago (catalogo anexo 24)"
    
    _columns = {
        'name': fields.char("Concepto", size=128, required=True),
        'code': fields.char("Clave", size=128, required=True)
    }

metodo_de_pago()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: