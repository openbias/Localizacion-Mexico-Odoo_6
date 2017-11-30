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

from osv import fields, osv

import suds
import xml.etree.ElementTree as ET
import base64
import urllib2
import os
from soap_hacienda import ConsultaCFDI
import re
from datetime import datetime



class validar_factura_subir_line(osv.osv_memory):
    """
    Line 
    """
    _name = "validar_factura.subir.line"
    _description = "Validar Factura Line"
    _columns = {
        'clave': fields.char("Clave", size=64),
        'cantidad': fields.float("Cantidad factura"),
        'importe': fields.float("Importe factura"),
        'udm': fields.char("UdM factura", size=64),
        'cantidad_OC': fields.float("Cantidad sistema"),
        'importe_OC': fields.float("Importe sistema"),
        'udm_OC': fields.char("UdM sistema", size=64),
        'wizard_id': fields.many2one("validar_factura.subir"),
        'ok': fields.boolean("Ok")
    }

validar_factura_subir_line()


class validar_factura_subir_xml(osv.osv_memory):
    """
    Line 
    """
    _name = "validar_factura.subir"
    _description = "Validar Factura Subir XML"
    _columns = {
        'validar_productos_remision': fields.boolean(u"Validar partidas de la remision?"),
        'remision': fields.many2one("stock.picking", string=u"Remision"),
        'partner_id': fields.many2one("res.partner"),
        'order_id': fields.many2one("purchase.order"),
        'xml': fields.binary("XML", required=True),
        'pdf': fields.binary("PDF", required=True),
        'pdf_evidencia': fields.binary(u"PDF Validación", required=True),
        'codigo': fields.char("Codigo Estatus", size=64),
        'estado': fields.char("Estado", size=64),
        'continue': fields.boolean("Continuar"),
        'lines': fields.one2many("validar_factura.subir.line", "wizard_id", string="Partidas"),
        'show_lines': fields.boolean("Show lines"),
        'total': fields.float("Total"),
        'total_OC': fields.float("Total Sistema"),
        'n': fields.integer("Partidas en factura"),
        'n_OC': fields.integer("Partidas"),
        'tc': fields.float("Tipo de cambio reportado o calculado"),
        'tc_open': fields.float("Tipo de cambio del sistema"),
        'mensajes_error': fields.text("Mensajes de error"),
        'everything_ok': fields.boolean("Factura valida"),
        'validar_oc': fields.boolean("Validar la orden de compra"),
        'validar_tc': fields.boolean("Validar el tipo de cambio"),
        'validar_remision': fields.boolean("Validar remision"),
        'uuid': fields.char("UUID", size=64),
        'moneda': fields.many2one("res.currency", "Moneda"),
        'moneda_po': fields.many2one("res.currency", "Moneda OC"),
        'moneda_diferente': fields.boolean("Moneda diferente"),
        'descuento': fields.float("Descuento"),
        'reporte_validation_xml': fields.text(string="Validar XML"),
        'message_validation_xml': fields.text(string="Validar XML")
    }

    _defaults = {
        'continue': False,
        'show_lines': False,
        'validar_oc': True,
        'validar_tc': False,
        'validar_remision': False,
        'validar_productos_remision': True
    }


    def default_get(self, cr, uid, fields, context=None):
        res = super(validar_factura_subir_xml, self).default_get(cr, uid, fields, context=context)
        order_obj = self.pool.get("purchase.order")
        if order_obj.browse(cr, uid, context.get("active_id")).factura_subida:
            raise osv.except_osv("Error", u"Ya se subió la factura de esta orden de compra")
        return res

    def _validar_en_hacienda(self, cr, uid, xml, context=None):
        try:
            root = ET.fromstring(xml)
        except:
            raise osv.except_osv("Error", "El archivo XML parece estar mal formado")
        total = emisor = receptor = uuid = False
        total = float(root.attrib.get("total", False))
        for child in root:
            if child.tag.endswith("Emisor"):
                emisor = child.attrib["rfc"]
            elif child.tag.endswith("Receptor"):
                receptor = child.attrib["rfc"]
                receptor_nombre = child.attrib["nombre"]
            elif child.tag.endswith("Complemento"):
                for child2 in child:
                    if child2.tag.endswith("TimbreFiscalDigital"):
                        uuid = child2.attrib["UUID"]

        if not all([total, emisor, receptor, uuid]):
            raise osv.except_osv("Error", "El archivo XML no parece ser un CFDI")

        user_obj = self.pool.get('res.users').browse(cr, uid, uid)
        if user_obj.company_id.partner_id.vat != receptor:
            raise osv.except_osv("Error", u"El RFC de la compañía (receptor) %s no coincide con %s "%(user_obj.company_id.partner_id.vat, receptor) )

        if context and 'active_id' in context and "active_model" in context:
            obj = self.pool.get(context["active_model"])
            obj_brw = obj.browse(cr, uid, context.get("active_id"))
            if obj_brw.partner_id.vat != emisor:
                raise osv.except_osv("Error", u"Los RFCs de la factura y el documento no coinciden")
            if obj_brw.company_id.partner_id.vat != receptor:
                raise osv.except_osv("Error", u"El RFC de la compañía (receptor) no coincide")
        integer, decimal = str(total).split('.')
        padded_total = integer.rjust(10, '0') + '.' + decimal.ljust(6, '0')
        data = '?re=%s&rr=%s&tt=%s&id=%s'%(emisor, receptor, padded_total, uuid)
        
        #Esto manda el soap directamente con pycurl (ver soap_hacienda.py)
        #----------------
        resp = ConsultaCFDI(data)
        m = re.search("CodigoEstatus>(.*?)</a:CodigoEstatus><a:Estado>(.*?)</a:Estado>", resp)
        if not m:
            raise osv.except_osv("Error", "Hubo un error al consultar hacienda")
        return uuid, m.group(1), m.group(2)

validar_factura_subir_xml()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
