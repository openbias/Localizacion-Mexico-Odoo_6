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
import os
import netsvc

import base64
import re
import os
import xml.etree.ElementTree as ET
from lxml import etree
from datetime import datetime
from validar_xml import validate_xml_schema

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    _columns = {
        'creada_de_xml': fields.boolean("Creada a partir de CFDI"),
        'hora_factura': fields.char('Hora', size=16),
        'supplier_invoice_number': fields.char('Supplier Invoice Number', size=64, help="The reference of this invoice as provided by the supplier.", readonly=True, states={'draft':[('readonly',False)]}),
    }

    _defaults = {
        'creada_de_xml': lambda *a: False,
    }

    def test_open(self, cr, uid, ids, *args):
        for invoice in self.browse(cr, uid, ids):
            if invoice.type.startswith("in"):
                if not invoice.creada_de_xml:
                    raise osv.except_osv("Error", u"No se puede Aprobar la Factura \n No se ha subido el xml")
        return super(account_invoice, self).test_open(cr, uid, ids, *args)

    def subir(self, cr, uid, ids, context=None):
        if context is None: context = {}
        context["active_ids"] = ids
        context["active_id"] = ids[0]
        context["active_model"] = "account.invoice"
        this = self.browse(cr, uid, ids[0])
        model_data_obj = self.pool.get('ir.model.data')
        view_rec = model_data_obj.get_object_reference(cr, uid, 'validar_factura', 'validar_factura_subir_factura')
        view_id = view_rec and view_rec[1] or False
        return {
            'view_type': 'form',
            'view_id' : [view_id],
            'view_mode': 'form',
            'res_model': 'validar_factura.subir.factura',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }

    def _get_xml_datas(self, xml_sellado):
        res = {
            'importe_total': 0.0,
            'version': '1.0',
            'tipo_comprobante': 'ingreso',
            'certificado_sat': '',
            'certificado_emisor': '',
            'fecha_emision': '',
            'fecha_certificacion': '',
            'uuid': '',
            'rfc_emisor': '',
            'nombre_emisor': '',
            'rfc_receptor': '',
            'nombre_receptor': '',
            'folio': '',
            'certificado': ''
        }
        try:
            root = ET.fromstring(xml_sellado)
        except:
            pass
        res['importe_total'] = float(root.attrib.get("total", False))
        res['version'] = root.attrib.get('version')
        res['tipo_comprobante'] = root.attrib.get('tipoDeComprobante')
        res['certificado_emisor'] = root.attrib.get('noCertificado')
        res['fecha_emision'] = root.attrib.get('fecha')
        res['folio'] = root.attrib.get('folio')
        res['certificado'] = root.attrib.get('certificado')
        for child in root:
            if child.tag.endswith("Emisor"):
                res['nombre_emisor'] = unicode(child.attrib["nombre"]).encode('utf-8')
                res['rfc_emisor'] = child.attrib["rfc"]
            elif child.tag.endswith("Receptor"):
                res['nombre_receptor'] = unicode(child.attrib["nombre"]).encode('utf-8')
                res['rfc_receptor'] = child.attrib["rfc"]
            elif child.tag.endswith("Complemento"):
                for child2 in child:
                    if child2.tag.endswith("TimbreFiscalDigital"):
                        res['uuid'] = child2.attrib["UUID"]
                        res['certificado_sat'] = child2.attrib["noCertificadoSAT"]
                        res['fecha_certificacion'] = child2.attrib["FechaTimbrado"]
        return res

    def _reporte_validacion_xml(self, xml_sellado, context):
        xml_datas = self._get_xml_datas(xml_sellado)
        validar_xml = """
            ==|== Reporte de validación ==|==
            ** Versión: {version}
            ** Tipo Comprobante: {tipo_comprobante}
            ** Certificado SAT: {certificado_sat}
            ** Certificado Emisor: {certificado_emisor}
            ** Fecha Emisión: {fecha_emision}
            ** Fecha Certificación: {fecha_certificacion}
            ** UUID: {uuid}
            ** Importe Total: {importe_total}
            ** RFC Emisor: {rfc_emisor}
            ** Nombre Emisor: {nombre_emisor}
            ** RFC Receptor: {rfc_receptor}
            ** Nombre Receptor: {nombre_receptor} 
        """.format(**xml_datas)
        return validar_xml

    def _validar_xml(self, xml_sellado, context):
        path = os.path.abspath(os.path.dirname(__file__))
        path_xsd = path + "/%s"%(context.get('xml_xsd'))
        path_xml_datas = context.get('xml_file')
        validar_xml = ""
        try:
            text_xml = open("/tmp/xml_contabilidad.xml", "w")
            text_xml.write(xml_sellado)
            text_xml.close()
            validate = validate_xml_schema(path_xsd, '/tmp/xml_contabilidad.xml')
            validar_xml = validate.validate_xml()
            validar_xml = validate.return_validate()
        except:
            pass
        return validar_xml


account_invoice()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

