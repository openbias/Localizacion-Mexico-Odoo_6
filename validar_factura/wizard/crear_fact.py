# -*- encoding: utf-8 -*-

from osv import osv, fields
import base64
import re
import xml.etree.ElementTree as ET
from datetime import datetime

import requests
from requests import Request, Session
import json

import logging
logging.basicConfig(level=logging.INFO)

class validar_factura_crear_fac(osv.osv_memory):
    _name = "validar_factura.crear.fac"
    _description = "Validar Factura Subir XML"

    _columns = {
        'codigo': fields.char(u"Código", size=128 ),
        'estado': fields.char(u"Estado", size=64),
        'ok': fields.boolean("Ok"),
        'xml': fields.binary(u'Archivo xml', required=True),
        'pdf': fields.binary(u'Archivo pdf', required=True),
        'moneda': fields.many2one("res.currency", string="Moneda"),
        'pdf_valida': fields.binary(u'Archivo pdf validación (opcional)'),
        'product_id': fields.many2one("product.product", string=u"Producto que aparecerá en la factura"),
        'reporte_validation_xml': fields.text(string="Validar XML"),
        'message_validation_xml': fields.text(string="Validar XML"),
        'company_id': fields.many2one('res.company', 'Company', required=True, change_default=True, readonly=True),
    }

    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'validar_factura.crear.fac', context=c),
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

    def action_subir(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid,ids[0])
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
            'ok': result.get('xml_valido'),
            'codigo': result.get('cod_estatus'),
            'estado': result.get('estado'),
        })
        model_data_obj = self.pool.get('ir.model.data')
        view_rec = model_data_obj.get_object_reference(cr, uid, 'validar_factura', 'crear_fac_wizard_form')
        view_id = view_rec and view_rec[1] or False
        return {
           'res_id': this.id,
           'view_type': 'form',
           'view_id' : [view_id],
           'view_mode': 'form',
           'res_model': 'validar_factura.crear.fac',
           'type': 'ir.actions.act_window',
           'target': 'new',
           'context': context
        }
        
    def action_procesar(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid,ids[0])
        xml = base64.decodestring(this.xml)
        data = self.get_invoice_data(cr, uid, xml, this, context=context)
        invoice_obj = self.pool.get("account.invoice")
        model_data_obj = self.pool.get('ir.model.data')
       
        if invoice_obj.search(cr, uid, [('uuid','=',data["uuid"])]):
            raise osv.except_osv("Error", "Ya se tiene en el sistema una factura con el UUID %s"%data["uuid"])
        res_id = invoice_obj.create(cr, uid, data, context=context)
        att_obj = self.pool.get("ir.attachment")
        xml_att_values = {
          'name': data["uuid"] + ".xml",
          'datas': this.xml,
          'datas_fname': data["uuid"] + ".xml",
          'description': data["uuid"],
          'res_model': "account.invoice",
          'res_id': res_id,
        }
        pdf_att_values = {
            'name': data["uuid"] + ".pdf",
            'datas': this.pdf,
            'datas_fname': data["uuid"] + ".pdf",
            'description': data["uuid"],
            'res_model': "account.invoice",
            'res_id': res_id,
        }
        a1=att_obj.create(cr, uid, xml_att_values, context=context)
        a2=att_obj.create(cr, uid, pdf_att_values, context=context)
        if this.pdf_valida:
            evi_att_values = {
                'name': "Validacion " + data["uuid"] + ".pdf",
                'datas': this.pdf_valida,
                'datas_fname': "Validacion " + data["uuid"] + ".pdf",
                'description': data["uuid"],
                'res_model': "account.invoice",
                'res_id': res_id
            }
            att_obj.create(cr, uid, evi_att_values, context=context)
        invoice_obj.button_compute(cr, uid, [res_id], context=context)


        action_model,action_id = model_data_obj.get_object_reference(cr, uid, 'account', "action_invoice_tree2")
        if action_model:
            action_pool = self.pool.get(action_model)
            action = action_pool.read(cr, uid, action_id, context=context)
            action['domain'] = "[('id','in', ["+','.join(map(str,[res_id]))+"])]"
        return action
            
    def get_invoice_data(self, cr, uid, xml, wizard, context=None):
        if context is None: context = {}
        
        datas = json.loads(context.get("xml_datas", "{}"))
        ns = "{http://www.sat.gob.mx/cfd/3}"
        ns1 = "{http://www.sat.gob.mx/TimbreFiscalDigital}"
        d = datas.get("%sComprobante"%ns)
        emisor = d.get("%sEmisor"%ns)
        receptor = d.get("%sReceptor"%ns)
        timbre = d.get("%sComplemento"%ns) and d["%sComplemento"%ns].get("%sTimbreFiscalDigital"%ns1)
        uuid = timbre.get("@UUID") or ""

        Partner = self.pool.get("res.partner")
        Users = self.pool.get('res.users')
        Journal = self.pool.get("account.journal")
        Product = self.pool.get("product.product")
        Uom = self.pool.get("product.uom")
        Fpos= self.pool.get('account.fiscal.position')
        IrValues = self.pool.get("ir.values")

        uid_company_id = Users.browse(cr, uid, uid).company_id.id
        journal_ids = Journal.search(cr, uid, [('type', '=', 'purchase'), ('company_id', '=', uid_company_id)], limit=1)
        data = {
            'type': 'in_invoice',
            'journal_id': journal_ids and journal_ids[0] or False
        }

        fecha = d.get("@Fecha") or d.get("@fecha") or False
        serie = d.get("@Serie") or d.get("@serie") or False
        folio = d.get("@Folio") or d.get("@folio") or False
        descuento = d.get("@Descuento") or d.get("@descuento") or False

        data["date_invoice"] = fecha.split("T")[0]
        data["hora_factura"] = fecha.split("T")[1]
        fpos = False
        supplier_invoice_number = str(folio)
        if serie:
            supplier_invoice_number = "%s-%s"%(supplier_invoice_number, serie)
        data["supplier_invoice_number"] = supplier_invoice_number
        data["check_total"] = d.get("@Total") or d.get("@total")

        #Emisor
        emisor_rfc = emisor.get('@Rfc') or emisor.get('@rfc') or False
        partner_ids = Partner.search(cr, uid, [('vat', '=',  emisor_rfc )])
        p_brw = Partner.browse(cr, uid, partner_ids[0])
        address_contact_id, address_invoice_id = Partner.address_get(cr, uid, [p_brw.id], ['contact', 'invoice']).values()
        data["partner_id"] = p_brw.id
        data["address_invoice_id"] = address_invoice_id or None
        data["address_contact_id"] = address_contact_id or None
        data["account_id"] = p_brw.property_account_payable.id

        #Conceptos
        if d.get("%sConceptos"%ns):
            conceptos = d["%sConceptos"%ns].get("%sConcepto"%ns)
            if type(conceptos) is dict:
                conceptos = [conceptos]

        try:
            p = Product.browse(cr, uid, wizard.product_id.id, context=context)
            for con in conceptos:
                unidad = con.get("@Unidad") or con.get("@unidad") or ""
                taxes = [(4,tax.id) for tax in p.supplier_taxes_id]

                line_vals = {}
                line_vals["product_id"] = wizard.product_id.id
                line_vals['invoice_line_tax_id'] = taxes
                line_vals["account_id"] = p.property_account_expense and p.property_account_expense.id or p.categ_id.property_account_expense_categ.id
                line_vals["name"] = con.get("@Descripcion") or con.get("@descripcion") or ""
                line_vals["quantity"] = con.get("@Cantidad") or con.get("@cantidad") or 0.0
                line_vals["price_unit"] = con.get("@ValorUnitario") or con.get("@valorUnitario") or 0.0
                uom_id = Uom.search(cr, uid, [("name", 'ilike', unidad)])
                if not uom_id:
                    uom_id = Uom.search(cr, uid, [("name", 'ilike', "pieza")])
                if uom_id:
                    line_vals["uos_id"] = uom_id[0]
                data.setdefault("invoice_line", []).append((0,0,line_vals))
            data["currency_id"] = wizard.moneda.id
        except:
            pass

        if descuento:
            supplier_taxes_id = IrValues.get_default(cr, uid, 'product.product', 'supplier_taxes_id', company_id=uid_company_id)
            purchase_tax_id = isinstance(supplier_taxes_id, list) and supplier_taxes_id[0] or supplier_taxes_id
            account_id = p.property_account_expense and p.property_account_expense.id or p.categ_id.property_account_expense_categ.id
            disc_line_vals = {
                'name': 'Descuento',
                'quantity': 1,
                'price_unit': -float(descuento),
                'account_id': account_id, 
                'invoice_line_tax_id': [(4, purchase_tax_id)]
            }
            data.setdefault("invoice_line", []).append((0,0,disc_line_vals))
        data["uuid"] = uuid
        data["creada_de_xml"] = True
        data['certificate'] = d.get("@Certificado") or d.get("@certificado") or False
        data['subtotal'] = d.get("@SubTotal") or d.get("@subTotal") or False
        data['descuento'] = descuento

        return data

validar_factura_crear_fac()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
