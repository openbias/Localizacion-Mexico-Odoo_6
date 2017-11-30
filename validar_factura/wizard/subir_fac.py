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
import xml.etree.ElementTree as ET
import base64
import os
import netsvc

import requests
from requests import Request, Session
import json

import logging
logging.basicConfig(level=logging.INFO)


class validar_factura_subir_factura_line(osv.osv_memory):
    """
    Line 
    """
    _name = "validar_factura.subir.factura.line"
    _description = "Validar Factura Line"
    _columns = {
        'clave': fields.char("Clave", size=64),
        'cantidad': fields.float("Cantidad factura"),
        'importe': fields.float("Importe factura"),
        'udm': fields.char("UdM factura", size=64),
        'cantidad_fac': fields.float("Cantidad Factura"),
        'importe_fac': fields.float("Importe Factura"),
        'udm_fac': fields.char("UdM Factura", size=64),
        'wizard_id': fields.many2one("validar_factura.subir.factura"),
        'ok': fields.boolean("Ok")
    }

validar_factura_subir_factura_line()



class validar_factura_subir_factura(osv.osv_memory):
    """
    Validar XML Factura
    """
    _name = "validar_factura.subir.factura"
    _description = "Validar Factura Subir XML"
    _columns = {
        'xml': fields.binary("XML"),
        'pdf': fields.binary("PDF"),
        'pdf_evidencia': fields.binary(u"PDF Validación"),
        'codigo': fields.char("Codigo Estatus", size=64),
        'estado': fields.char("Estado", size=64),
        'continue': fields.boolean("Continuar"),
        'uuid': fields.char("UUID", size=64),
        'validar_partidas': fields.boolean("Validar Partidas"),
        'total_xml': fields.float("Total XML"),
        'total_fac': fields.float("Total Factura"),
        'all_ok': fields.boolean("Todo bien"),
        'lines': fields.one2many("validar_factura.subir.factura.line", "wizard_id", string="Partidas"),
        'mensajes': fields.text("Mensajes"),
        'show_lines': fields.boolean("Show lines"),
        'reporte_validation_xml': fields.text(string="Validar XML"),
        'message_validation_xml': fields.text(string="Validar XML"),
        'company_id': fields.many2one('res.company', 'Company', required=True, change_default=True, readonly=True),
    }

    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'validar_factura.crear.fac', context=c),
        'continue': False,
        'validar_partidas': True,
        'show_lines': False,
    }


    def action_server(self, url, host, db, params):
        s = Session()
        s.get('%s/web?db=%s'%(host, db))
        headers = {
            'Content-Type':'application/json',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0',
            'Referer' : url
        }
        data = {
            "jsonrpc": "2.0",
            "method": "call",
            "id":0,
            "params": params
        }
        res = s.post(url, data=json.dumps(data), headers=headers)
        res_datas = res.json()
        if res_datas.get('error'):
            return res_datas['error']
        if res_datas.get('result') and res_datas['result'].get('error'):
            return res_datas['result']['error']
        return res_datas

    def action_upload(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])

        cia = this.company_id
        host = cia.cfd_mx_host
        url = '%s/validate/'%(host)
        db = cia.cfd_mx_db
        cfdi_datas = {
            'db': db,
            'xml': this.xml,
            'vat': cia.partner_id.vat,
            'test': cia.cfd_mx_test,
            'cfd': {
                'test': cia.cfd_mx_test,
                'pac': cia.cfd_mx_pac,
                'version': cia.cfd_mx_version
            }
        }
        datas = json.dumps(cfdi_datas, sort_keys=True, indent=4, separators=(',', ': '))
        params = {"context": {},  "post":  datas}
        res =  self.action_server(url, host, db, params)
        if res.get('message'):
            message = res['message']
            message = message.replace("(u'", "").replace("', '')", "")
            raise osv.except_osv('Error !', message)
        result = res.get('result')

        #Valida RFC
        Invoice = self.pool.get("account.invoice")
        Partner = self.pool.get("res.partner")
        datas = json.loads(result.get("xml_datas", "{}"))
        ns = "{http://www.sat.gob.mx/cfd/3}"
        ns1 = "{http://www.sat.gob.mx/TimbreFiscalDigital}"
        d = datas.get("%sComprobante"%ns)
        emisor = d.get("%sEmisor"%ns)
        receptor = d.get("%sReceptor"%ns)
        timbre = d.get("%sComplemento"%ns) and d["%sComplemento"%ns].get("%sTimbreFiscalDigital"%ns1)
        uuid = timbre.get("@UUID") or ""
        
        emisor_rfc = emisor.get('@Rfc') or emisor.get('@rfc') or False
        partner_id = Partner.search(cr, uid, [('vat', '=',  emisor_rfc )])
        if not partner_id:
            raise osv.except_osv("Error", u"No se encontró en el sistema un proveedor con el RFC %s"%vat)

        receptor_rfc = receptor.get('@Rfc') or receptor.get('@rfc') or False
        partner_id = Partner.search(cr, uid, [('vat', '=',  receptor_rfc )])
        if not partner_id:
            raise osv.except_osv("Error", u"El RFC no corresponde a la Empresa %s"%receptor_rfc)

        invoice_id = Invoice.search(cr, uid, ['|', ('uuid', '=',  uuid), ('uuid', '=', uuid.replace("-",""))])
        if invoice_id:
            raise osv.except_osv("Error", u"UUID Duplicado en Factura ID: %s"% invoice_id[0] )

        context["xml_datas"] = result.get("xml_datas")
        self.write(cr, uid, [this.id], {
            'continue': True,
            'ok': result.get('xml_valido'),
            'codigo': result.get('cod_estatus'),
            'codigo': result.get('cod_estatus'),
            'estado': result.get('estado'),
            'uuid': uuid,
        })

        model_data_obj = self.pool.get('ir.model.data')
        view_rec = model_data_obj.get_object_reference(cr, uid, 'validar_factura', 'validar_factura_subir_factura')
        view_id = view_rec and view_rec[1] or False
        return {
           'res_id': this.id,
           'view_type': 'form',
           'view_id' : [view_id],
           'view_mode': 'form',
           'res_model': 'validar_factura.subir.factura',
           'type': 'ir.actions.act_window',
           'target': 'new',
           'context': context
        }

    def get_xml_data(self, cr, uid, xml):
        partner_obj = self.pool.get("res.partner")
        product_obj = self.pool.get("product.product")
        uid_company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        journal_ids = self.pool.get("account.journal").search(cr, uid, [('type', '=', 'purchase'), ('company_id', '=', uid_company_id)], limit=1)
        data = {
            'type': 'in_invoice',
            'journal_id': journal_ids and journal_ids[0] or False
        }

        root = ET.fromstring(xml)
        data["date_invoice"] = root.attrib["fecha"].split("T")[0]
        data["hora_factura"] = root.attrib["fecha"].split("T")[1]

        supplier_invoice_number = ""
        if root.attrib.get("serie", False):
            supplier_invoice_number = root.attrib["serie"]
        if root.attrib.get("folio", False):
            supplier_invoice_number += " - " + root.attrib["folio"]
        data["supplier_invoice_number"] = supplier_invoice_number

        data["check_total"] = root.attrib["total"]
        for node in root:
            if node.tag.endswith("Emisor"):
                vat = node.attrib["rfc"]
                partner_id = partner_obj.search(cr, uid, [('vat', '=', vat)])
                if not partner_id:
                    raise osv.except_osv("Error", u"No se encontró en el sistema un proveedor con el RFC %s"%vat)
                partner = partner_obj.browse(cr, uid, partner_id[0])
                data["partner_id"] = partner.id
                data["account_id"] = partner.property_account_payable.id
            elif node.tag.endswith("Complemento"):
                for nodecomp in node:
                    if nodecomp.tag.endswith("TimbreFiscalDigital"):
                        data["uuid"] = nodecomp.attrib["UUID"]
        return data


    def action_validar(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        xml = base64.decodestring(this.xml)
        if this.validar_partidas:
            partidas_xml = {}
            partidas_fac = {}
            lines = []
            root = ET.fromstring(xml)
            total_xml = float(root.attrib["total"])
            invoice_id = context["active_id"]
            invoice = self.pool.get("account.invoice").browse(cr, uid, invoice_id)
            for line_fac in invoice.invoice_line:
                if line_fac.price_subtotal < 0:
                    continue
                if line_fac.product_id and line_fac.product_id.default_code:
                    numid = line_fac.product_id.default_code
                    partidas_fac.setdefault(numid, [0,0,""])
                    partidas_fac[numid][0] += line_fac.quantity
                    partidas_fac[numid][1] += line_fac.price_subtotal
                    partidas_fac[numid][2] = line_fac.uos_id and line_fac.uos_id.name or ""
            sin_clave = False
            for node in root:
                if node.tag.endswith("Conceptos"):
                    conceptos = node
            for c in conceptos:
                numid = c.attrib.get("noIdentificacion", False)
                if not numid:
                    sin_clave = True
                    continue
                partidas_xml.setdefault(numid, [0,0,""])
                partidas_xml[numid][0] += float(c.attrib["cantidad"])
                partidas_xml[numid][1] += float(c.attrib["importe"])
                partidas_xml[numid][2] = c.attrib["unidad"]
            for numid in partidas_xml:
                partida_fac = partidas_fac.get(numid, [0,0,""])
                line = {
                    'clave': numid,
                    'cantidad': partidas_xml[numid][0],
                    'importe': partidas_xml[numid][1],
                    'udm': partidas_xml[numid][2]
                }
                line.update({
                    'cantidad_fac': partida_fac[0],
                    'importe_fac': partida_fac[1],
                    'udm_fac': partida_fac[2],
                })
                line["ok"] = all([
                    line["cantidad"] == line["cantidad_fac"],
                    round(line["importe"],2) == round(line["importe_fac"],2),
                    line["udm"].lower() == line["udm_fac"].lower()
                ])
                lines.append((0,0,line))
            mensajes = ''
            lines_ok = all([line[2]["ok"] for line in lines])
            total_fac = invoice.amount_total
            if not lines_ok:
                mensajes += u"No coinciden los datos de las partidas\n"
            if total_xml != total_fac:
                mensajes += u"No coinciden los totales\n"
            if sin_clave:
                mensajes += u"Una o más partidas no contienen el atributo 'noIdentificacion'\n"
            self.write(cr, uid, this.id, {
                'lines': lines ,
                'total_xml': total_xml,
                'total_fac': total_fac,
                'mensajes': mensajes,
                'all_ok': mensajes == '',
                'show_lines': True
            })
        else:
            self.write(cr, uid, [this.id], {'all_ok': True})

        model_data_obj = self.pool.get('ir.model.data')
        view_rec = model_data_obj.get_object_reference(cr, uid, 'validar_factura', 'validar_factura_subir_factura')
        view_id = view_rec and view_rec[1] or False
        return {
           'res_id': this.id,
           'view_type': 'form',
           'view_id' : [view_id],
           'view_mode': 'form',
           'res_model': 'validar_factura.subir.factura',
           'type': 'ir.actions.act_window',
           'target': 'new',
           'context': context
        }


    def action_accept(self, cr, uid, ids, context=None):
        if context is None: context = {}

        this = self.browse(cr, uid, ids[0])
        xml = base64.decodestring(this.xml)
        uid_company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        invoice_obj = self.pool.get("account.invoice")
        
        # xml_datas = invoice_obj._get_xml_datas(xml)
        xml_datas = self.pool.get("validar_factura.crear.fac").get_invoice_data(cr, uid, xml, this, context=context)
        invoice_id = context["active_id"]
        invoice_obj.write(cr, uid, invoice_id, {
            'uuid': this.uuid,
            'creada_de_xml': True,
            'certificate': xml_datas.get('certificado'),
            'supplier_invoice_number': xml_datas.get('folio')
        })
        att_obj = self.pool.get("ir.attachment")
        xml_att_values = {
          'name': this.uuid + ".xml",
          'datas': this.xml,
          'datas_fname': this.uuid + ".xml",
          'description': this.uuid,
          'res_model': "account.invoice",
          'res_id': invoice_id,
          'type': 'binary'
        }
        pdf_att_values = {
            'name': this.uuid + ".pdf",
            'datas': this.pdf,
            'datas_fname': this.uuid + ".pdf",
            'description': this.uuid,
            'res_model': "account.invoice",
            'res_id': invoice_id,
            'type': 'binary'
        }
        evi_att_values = {
            'name': "Validacion " + this.uuid + ".pdf",
            'datas': this.pdf_evidencia,
            'datas_fname': "Validacion " + this.uuid + ".pdf",
            'description': this.uuid,
            'res_model': "account.invoice",
            'res_id': invoice_id,
            'type': 'binary'
        }
        att_obj.create(cr, uid, xml_att_values, context=context)
        att_obj.create(cr, uid, pdf_att_values, context=context)
        if this.pdf_evidencia:
            att_obj.create(cr, uid, evi_att_values, context=context)
        
        #Agregar descuento si el xml tiene descuento
        descuento = xml_datas.get("descuento")
        subtotal = xml_datas.get("subtotal")

        if descuento:
            subtotal = float(subtotal)
            descuento = float(descuento)
            inv = invoice_obj.browse(cr, uid, invoice_id)
            if abs(subtotal - descuento - inv.amount_untaxed ) <= (inv.currency_id.rounding/2.0):
                descuento = 0.0

            inv_line_obj = self.pool.get("account.invoice.line")
            ir_values = self.pool.get("ir.values")
            supplier_taxes_id = ir_values.get_default(cr, uid, 'product.product', 'supplier_taxes_id', company_id=uid_company_id)
            purchase_tax_id = isinstance(supplier_taxes_id, list) and supplier_taxes_id[0] or supplier_taxes_id
            disc_line_vals = {
                'name': 'Descuento',
                'quantity': 1,
                'price_unit': -(descuento),
                'account_id': inv_line_obj._default_account_id(cr, uid),
                'invoice_id': invoice_id,
                'invoice_line_tax_id': [(4,purchase_tax_id)]
            }
            inv_line_obj.create(cr, uid, disc_line_vals)
            invoice_obj.button_compute(cr, uid, [invoice_id], context=context)
        return { 'type': 'ir.actions.client', 'tag': 'reload' }


validar_factura_subir_factura()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: