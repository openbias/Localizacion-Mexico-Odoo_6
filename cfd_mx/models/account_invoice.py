# -*- encoding: utf-8 -*-

import decimal_precision as dp

from osv import fields, osv
import time
from mx.DateTime import *
from datetime import date, datetime, timedelta
from pytz import timezone, utc
import base64

import pytz

import requests
from requests import Request, Session
import json

import logging
logging.basicConfig(level=logging.INFO)


def getLocalTime(timezone):
    nn = now()
    if nn.localtime() == nn.gmtime():
        tt = time.localtime()
        mytz = pytz.timezone(timezone)
        mydelta = mytz.utcoffset(datetime(tt.tm_year, tt.tm_mon, tt.tm_mday, tt.tm_hour, tt.tm_min))
        return nn.localtime() + mydelta
    else:
        return nn


class AccountInvoiceRefund(osv.osv_memory):
    _inherit = "account.invoice.refund"
    _description = "Invoice Refund"

    _columns = { 
        'tiporelacion_id': fields.many2one('cfd_mx.tiporelacion', string=u'Tipo de Relacion')
    }

    def compute_refund(self, cr, uid, ids, mode='refund', context=None):
        if context is None:
            context = {}
        inv_obj = self.pool.get('account.invoice')
        for form in self.browse(cr, uid, ids, context=context):
            print "form", form
            for inv in inv_obj.browse(cr, uid, context.get('active_ids'), context=context):
                inv.write({'tiporelacion_refund_id': form.tiporelacion_id.id})
        res = super(AccountInvoiceRefund, self).compute_refund(cr, uid, ids, mode='refund', context=context)
        return res


class AccountInvoiceLine(osv.osv):
    _inherit = 'account.invoice.line'


    def _compute_price_sat(self, cr, uid, ids, name, args, context=None):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids, context=context):
            price_subtotal_sat = line.price_unit
            discount =  ((line.discount or 0.0) / 100.0) * price_subtotal_sat
            price = (price_subtotal_sat - discount)
            taxes = {}
            if line.invoice_line_tax_id:
                taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, address_id=line.invoice_id.address_invoice_id, partner=line.invoice_id.partner_id)
            res[line.id] = {
                'price_subtotal_sat': (line.price_unit * line.quantity),
                'price_tax_sat': taxes.get('total_included', 0.00) - taxes.get('total', 0.00),
                'price_discount_sat': discount * line.quantity
            }
        return res

    _columns = {
        'price_subtotal_sat': fields.function(_compute_price_sat, 
            string='Amount (SAT)', type='float', 
            digits_compute= dp.get_precision('Account'), multi='all'),
        'price_tax_sat': fields.function(_compute_price_sat, 
            string='Tax (SAT)', type='float', 
            digits_compute= dp.get_precision('Account'), multi='all'),
        'price_discount_sat': fields.function(_compute_price_sat, 
            string='Discount (SAT)', type='float', 
            digits_compute= dp.get_precision('Account'), multi='all'),
        'numero_pedimento_sat': fields.char(string='Numero de Pedimento', size=64, help='Informacion Aduanera. Numero de Pedimento')
    }


class AccountInvoice(osv.osv):
    _inherit = 'account.invoice'

    def _escfdi(self, cr, uid, ids, name, args, context=None):
        res = {}
        for inv in self.browse(cr, uid, ids, context=context):
            res[inv.id] = True if inv.journal_id.e_invoice else False
        return res

    def _timbrada(self, cr, uid, ids, name, args, context=None):
        res = {}
        for inv in self.browse(cr, uid, ids, context=context):
            res[inv.id] = True if inv.uuid else False
        return res

    def _compute_price_sat(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'price_subtotal_sat': 0.0,
                'price_tax_sat': 0.0,
                'price_discount_sat': 0.0
            }
            for line in invoice.invoice_line:
                res[invoice.id]['price_subtotal_sat'] += line.price_subtotal_sat
                res[invoice.id]['price_tax_sat'] += line.price_tax_sat
                if line.discount:
                    res[invoice.id]['descuento'] += line.price_discount_sat
        return res

    _columns = {

        'price_subtotal_sat': fields.function(_compute_price_sat, 
            string='Amount (SAT)', type='float', 
            digits_compute= dp.get_precision('Account'), multi='all'),
        'price_tax_sat': fields.function(_compute_price_sat, 
            string='Tax (SAT)', type='float', 
            digits_compute= dp.get_precision('Account'), multi='all'),
        'price_discount_sat': fields.function(_compute_price_sat, 
            string='Discount (SAT)', type='float', 
            digits_compute= dp.get_precision('Account'), multi='all'),

        'es_cfdi': fields.function(_escfdi, string='Es CFDI', type='boolean',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, None, 50), # Check if we can remove ?
            }
        ),
        'timbrada': fields.function(_timbrada, string='Timbrado', type='boolean',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['uuid'], 50), # Check if we can remove ?
            }
        ),
        'serie': fields.char(string='Serie', size=8),
        'test': fields.boolean('Timbrado Prueba'),
        'date_invoice_cfdi': fields.char('Invoice Date', size=36),
        'tipo_comprobante': fields.selection([
                ('I', 'Ingreso'),
                ('E', 'Egreso'),
                ('T', U'Traslado'),
                ('N', U'Nómina'),
                ('P', 'Pago')
            ], 'Tipo de Comprobante', help=u'Catálogo de tipos de comprobante.'),
        'tiporelacion_id': fields.many2one('cfd_mx.tiporelacion', 'Tipo de Relacion'),
        'tiporelacion_refund_id': fields.many2one('cfd_mx.tiporelacion', 'T de Relacion'),
        'uuid_relacionado_id': fields.many2one('account.invoice', 'UUID Relacionado',  
                domain=[('type', 'in', ('out_invoice', 'out_refund') ), ('timbrada', '=', True), ('uuid', '!=', None)]),
        'formapago_id': fields.many2one('cfd_mx.formapago', 'Forma de Pago'),
        'metodopago_id': fields.many2one('cfd_mx.metodopago', 'Metodo de Pago'),
        'usocfdi_id': fields.many2one('cfd_mx.usocfdi', 'Uso de Comprobante CFDI'),
        'uuid': fields.char('Timbre fiscal', size=36),
        'bar_code': fields.binary('Bar Code'),
        'fecha_timbrado': fields.char('Fecha de Timbrado', size=32),
        'mandada_cancelar': fields.boolean('Mandada Cancelar'),
        'mensaje_pac': fields.text('Ultimo mensaje del PAC'),

        'certificate': fields.text('Certificate'),
        'certificado_sat': fields.text('Certificado SAT'),
        'cadena' :fields.text('Cadena'),
        'sello_sat': fields.text('Sello SAT'),
        'pay_account': fields.char('NumCtaPago', size=64),
    }

    _defaults = {
        'timbrada': False,
        'es_cfdi': False,
        'test': False,
        'date_invoice_cfdi': None,
        'uuid': None,
        'tipo_comprobante': 'I',
        'tiporelacion_id': None,
        'uuid_relacionado_id': None,
        'certificate': None,
        'certificado_sat': None,
        'cadena': None,
        'sello_sat': None,
        'price_subtotal_sat': 0.0,
        'price_tax_sat': 0.0,
        'price_discount_sat': 0.0
    }


    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({
            'state':'draft', 
            'number':False, 
            'move_id':False, 
            'move_name':False, 
            'cancel_date':False, 
            'certified_date':False,
            'approved_year':False, 
            'approved_number':False, 
            'certificate':False, 
            'digital_signature':False, 
            'date_due':False,
            'date_invoice':False, 
            'sello_sat':False, 
            'cadena':False, 
            'cadenatimbre':False, 
            'uuid':False, 
            'bar_code':False, 
            'period_id':False,
            'timbrada': False,
            'es_cfdi': False,
            'test': False,
            'date_invoice_cfdi': None,
            'tipo_comprobante': 'I',
            'tiporelacion_id': None,
            'uuid_relacionado_id': None,
            'certificado_sat': None,
            'price_subtotal_sat': 0.0,
            'price_tax_sat': 0.0,
            'price_discount_sat': 0.0
        })
        return super(AccountInvoice, self).copy(cr, uid, id, default, context)


    def create(self, cr, uid, vals, context=None):
        inv_id = super(AccountInvoice, self).create(cr, uid, vals, context)
        Inv = self.browse(cr, uid, inv_id)
        if Inv.partner_id:
            partner_id = Inv.partner_id
            vals = {
                'formapago_id': partner_id.formapago_id and partner_id.formapago_id.id or None,
                'metodopago_id': partner_id.metodopago_id and partner_id.metodopago_id.id or None,
                'usocfdi_id': partner_id.usocfdi_id and partner_id.usocfdi_id.id or None,
            }
            self.write(cr, uid, inv_id, vals)
        return inv_id

    def onchange_partner_id(self, cr, uid, ids, type, partner_id, date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        res = super(AccountInvoice, self).onchange_partner_id(cr, uid, ids, type, partner_id,
                                        date_invoice=date_invoice,
                                        payment_term=payment_term,
                                        partner_bank_id=partner_bank_id,
                                        company_id=company_id)
        if partner_id:
            Partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
            vals = {
                'formapago_id': Partner.formapago_id and Partner.formapago_id.id or None,
                'metodopago_id': Partner.metodopago_id and Partner.metodopago_id.id or None,
                'usocfdi_id': Partner.usocfdi_id and Partner.usocfdi_id.id or None,
            }
            res['value'].update(vals)
        return res


    def refund(self, cr, uid, ids, date=None, period_id=None, description=None, journal_id=None):
        new_ids = super(AccountInvoice, self).refund(cr, uid, ids, date=date, period_id=period_id, description=description, journal_id=journal_id)
        
        for inv in self.browse(cr, uid, new_ids):
            vals = {}
            for form in self.browse(cr, uid, ids):
                vals['uuid_relacionado_id'] = form.id
                vals['pay_account'] = form.pay_account
                vals['formapago_id'] = form.formapago_id and form.formapago_id.id or None
                vals["metodopago_id"] = form.metodopago_id and form.metodopago_id.id or None
                vals["usocfdi_id"] = form.usocfdi_id and form.usocfdi_id.id or None
                vals["tiporelacion_id"] = form.tiporelacion_refund_id and form.tiporelacion_refund_id.id or None
                vals['uuid_egreso'] = form.uuid
                vals['tipo_comprobante'] = 'E'
            inv.write(vals)
        return new_ids


    # Cancel
    def action_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        Reconcile = self.pool.get('account.move.reconcile')
        Line = self.pool.get('account.move.line')
        Move = self.pool.get('account.move')
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.type in ('in_invoice','in_refund'):
                res = super(AccountInvoice, self).action_cancel(cr, uid, ids, context)
                return True
            if inv.payment_ids:
                for move_line in inv.payment_ids:
                    if move_line.reconcile_partial_id and move_line.reconcile_partial_id.line_partial_ids:
                        raise osv.except_osv(_('Error !'), _('You cannot cancel the Invoice which is Partially Paid! You need to unreconcile concerned payment entries!'))
            if inv.move_id:
                date = time.strftime('%Y-%m-%d')
                period = self._period_get(cr, uid)
                if inv.state in ['draft', 'proforma2', 'cancel']:
                    raise  osv.except_osv(_('Error !'), _('Can not cancel draft/proforma/cancel invoice.'))
                
                description = 'Fac. %s Cancelada'%(inv.number)
                move_id = Move.copy(cr, uid, inv.move_id.id, context={}, default={'date': date, 'period_id': period, 'ref': description })
                move = Move.browse(cr, uid, move_id)
                Move.write(cr, uid, [move_id], {'date': date, 'name': '%s-C'%(inv.move_id.name)})
                for l in move.line_id:
                    Line.write(cr, uid, [l.id], {
                            'debit': l.credit,
                            'credit': l.debit,
                            'amount_currency': l.amount_currency and -l.amount_currency or False,
                            'date':date
                        }, context={'multireconcile':True})
                Move.post(cr, uid, [move_id])
                movelines = inv.move_id.line_id
                to_reconcile_ids = {}
                for l in movelines :
                    if l.account_id.id == inv.account_id.id :
                        to_reconcile_ids[l.account_id.id] = [l.id]
                    if type(l.reconcile_id) != osv.orm.browse_null:
                        reconcile_obj.unlink(cr, uid, l.reconcile_id.id)

                for tmpline in move.line_id :
                    if tmpline.account_id.id == inv.account_id.id :
                        to_reconcile_ids[tmpline.account_id.id].append(tmpline.id)

                for account in to_reconcile_ids :
                    Line.reconcile(cr, uid, to_reconcile_ids[account],
                        type = 'simple',
                        writeoff_period_id=period,
                        writeoff_journal_id=inv.journal_id.id,
                        writeoff_acc_id=inv.account_id.id
                    )
                date_time = getLocalTime(self.DEFAULT_TIMEZONE).Format('%Y-%m-%d %H:%M:%S')
                self.write(cr, uid, inv.id, {'cancel_date': date_time, 'state': 'cancel'})

                self.write(cr, uid, ids, {'state': 'cancel'})
                self._log_event(cr, uid, ids, -1.0, 'Cancel Invoice')
                date_time = getLocalTime(self.DEFAULT_TIMEZONE).Format('%Y-%m-%d %H:%M:%S')
                self.write(cr, uid, ids, {'cancel_date': date_time})

            # d
            self.action_cancel_cfdi(cr, uid, inv, context=context)
        return True


    def action_cancel_cfdi(self, cr, uid, obj, context=None):
        if context is None:
            context = {}
        if not obj.uuid:
            return True
        if obj.state == 'draft':
            return True
        if obj.type.startswith("in"):
            return True
        if obj.journal_id not in obj.company_id.cfd_mx_journal_ids:
            return True

        cia = obj.company_id
        url = '%s/cancel/'%(cia.cfd_mx_host)
        cfdi_datas = {
            'db': cia.cfd_mx_db,
            'uuid': obj.uuid,
            'vat': cia.partner_id.vat,
            'test': cia.cfd_mx_test,
            'cfd': self.get_info_pac(obj, cia),
            'noCertificado': obj.certificate
        }
        datas = json.dumps(cfdi_datas, sort_keys=True, indent=4, separators=(',', ': '))
        logging.info(datas)
        params = {"context": {},  "post":  datas}
        res =  self.action_server(url, cia.cfd_mx_host, cia.cfd_mx_db, params)
        if res.get('message'):
            message = res['message']
            message = message.replace("(u'", "").replace("', '')", "")
            raise osv.except_osv('Error !', message)
        else:
            acuse = res["result"].get("Acuse")
            obj.write({
                'mandada_cancelar': True, 
                'mensaje_pac': """
                Fecha: %s \n
                Folios: %s \n
                XML Acuse: %s \n
                """%(res["result"].get("Fecha"), res["result"].get("Folios"), acuse)
            })

            attachment_obj = self.pool.get('ir.attachment')
            fname = "cancelacion_cfd_%s.xml"%(obj.number or "")
            attachment_values = {
                'name': fname,
                'datas': base64.b64encode(acuse),
                'datas_fname': fname,
                'description': 'Cancelar Comprobante Fiscal Digital',
                'res_model': obj._name,
                'res_id': obj.id,
                'type': 'binary'
            }
            attachment_obj.create(cr, uid, attachment_values)
        return True

    def action_cancel_draft(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for inv in self.browse(cr, uid, ids):
            print "inv.journal_id", inv.journal_id, inv.uuid

            if inv.journal_id in inv.company_id.cfd_mx_journal_ids and inv.uuid != False:
                raise osv.except_osv(('Warrnig !'), ('This electronic invoice can not be set to draft.'))
            else:
                super(AccountInvoice, self).action_cancel_draft( cr, uid, ids, context)
        return True


    def test_open(self, cr, uid, ids, context=None):
        self.action_date_assign(cr, uid, ids, context)
        self.action_move_create(cr, uid, ids, context)

        self.write(cr, uid, ids, {})
        for obj in self.browse(cr, uid, ids):
            if obj.journal_id in obj.company_id.cfd_mx_journal_ids  and (obj.type in ('out_invoice', 'out_refund')):
                self.action_number(cr, uid, [obj.id], context=context)

                self.action_validate_cfdi(cr, uid, obj, context=context)
                self.action_write_date_invoice_cfdi(cr, uid, obj, context=context)
                cia = obj.company_id
                cfdi_datas = {
                    'relacionados': None,
                    'comprobante': None,
                    'emisor': None,
                    'receptor': None,
                    'conceptos': None,
                    'vat': cia.partner_id.vat,
                    'cfd': self.get_info_pac(obj, cia),
                    'db': cia.cfd_mx_db
                }
                cfdi_datas['relacionados'] = self.invoice_info_relacionados(cr, uid, obj, context=context)
                cfdi_datas['comprobante'] = self.invoice_info_comprobante(cr, uid, obj, context=context)
                cfdi_datas['emisor'] = self.invoice_info_emisor(cr, uid, obj, context=context)
                cfdi_datas['receptor'] = self.invoice_info_receptor(cr, uid, obj, context=context)
                cfdi_datas['conceptos'] = self.invoice_info_conceptos(cr, uid, obj, context=context)
                cfdi_datas['impuestos'] = self.invoice_info_impuestos(cr, uid, cfdi_datas['conceptos'], context=None)

                datas = json.dumps(cfdi_datas, sort_keys=True, indent=4, separators=(',', ': '))
                logging.info(datas)
                url = '%s/stampinvoice/'%(cia.cfd_mx_host)
                params = {"context": {},  "post":  datas }
                res =  self.action_server(url, cia.cfd_mx_host, cia.cfd_mx_db, params)
                if res.get('message'):
                    message = res['message']
                    message = message.replace("(u'", "").replace("', '')", "")
                    raise osv.except_osv('Error !', message)
                else:
                    self.get_process_data(cr, uid, obj, res.get('result'))
            # print miguelmiguel
            else:
                self.action_number( cr, uid, [obj.id], context=context)
            return True




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

    def get_info_pac(self, obj, cia):
        cfdi_datas = {
            'test': cia.cfd_mx_test,
            'pac': cia.cfd_mx_pac,
            'version': cia.cfd_mx_version
        }
        return cfdi_datas

    def get_inv_number(self, cr, uid, inv):
        prefix = inv.journal_id.sequence_id.prefix or ''
        print "prefix", prefix, inv.number, inv.internal_number
        if (prefix) and (inv.number):
            number = int(inv.number[len(prefix):])
        else:
            number = int(inv.number)
        return number, prefix

    def invoice_info_relacionados(self, cr, uid, obj, context=None):
        if context is None:
            context = {}
        cfdi_relacionado = {}
        if obj.uuid_relacionado_id:
            cfdi_relacionado['TipoRelacion'] = obj.tiporelacion_id and obj.tiporelacion_id.clave or ''
            cfdi_relacionado['uuid'] = obj.uuid_relacionado_id and obj.uuid_relacionado_id.uuid or ''
        return cfdi_relacionado

    def invoice_info_comprobante(self, cr, uid, obj, context=None):
        if context is None:
            context = {}
        Currency = self.pool.get('res.currency')
        dpa = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        date_invoice = obj.date_invoice_cfdi
        if obj.currency_id.name in ['MN', 'MXN']:
            rate = 1.0
            nombre = obj.currency_id.nombre_largo or 'pesos'
        else:
            cur_id = Currency.search(cr, uid, [('name', 'in', ['MN', 'MXN'])], context={'date': obj.date_invoice or False})
            if cur_id:
                c_id = Currency.browse(cr, uid, cur_id[0], context={'date':obj.date_invoice or False})
                rate = c_id.rate
                nombre = c_id.nombre_largo or 'pesos'
        if not obj.date_invoice_cfdi:
            date_invoice = self.action_write_date_invoice_cfdi(cr, uid, obj)

        number, prefix = self.get_inv_number(cr, uid, obj)
        cfdi_comprobante = {
            'Folio': '%s'%(number),
            'Fecha': date_invoice,
            'FormaPago': obj.formapago_id and obj.formapago_id.clave or '99',
            'CondicionesDePago': obj.payment_term and obj.payment_term.name or 'CONDICIONES',
            'Moneda': obj.currency_id.name,
            'SubTotal': '%.2f'%(obj.price_subtotal_sat),
            'Total': '%.2f'%(obj.price_subtotal_sat - obj.price_discount_sat + obj.price_tax_sat),
            'TipoDeComprobante': obj.tipo_comprobante,
            'MetodoPago': obj.metodopago_id and obj.metodopago_id.clave or 'Pago en una sola exhibicion',
            'LugarExpedicion': obj.journal_id and obj.journal_id.codigo_postal_id and obj.journal_id.codigo_postal_id.name or '',
            'Descuento': '%.2f'%(0.0)
        }
        if obj.journal_id.serie:
            cfdi_comprobante['Serie'] = obj.journal_id.serie or ''
        if obj.price_discount_sat:
            cfdi_comprobante['Descuento'] = '%.2f'%(round(obj.price_discount_sat, dpa))
        if obj.currency_id.name != 'MXN':
            cfdi_comprobante['TipoCambio'] = '%s'%(round(rate, 4))
        return cfdi_comprobante

    def invoice_info_emisor(self, cr, uid, obj, context=None):
        if context is None:
            context = {}
        partner_data = obj.company_id.partner_id
        emisor_attribs = {
            'Rfc': partner_data.vat or '',
            'Nombre': partner_data.name or '',
            'RegimenFiscal': partner_data.regimen_id and partner_data.regimen_id.clave or ''
        }
        return emisor_attribs

    def invoice_info_receptor(self, cr, uid, obj, context=None):
        if context is None:
            context = {}
        partner_data = obj.partner_id
        receptor_attribs = {
            'Rfc': partner_data.vat or '',
            'Nombre': partner_data.name or '',
            'UsoCFDI': obj.usocfdi_id and obj.usocfdi_id.clave or ''
        }
        if partner_data.es_extranjero == True:
            receptor_attribs['ResidenciaFiscal'] = partner_data.country_id.code_alpha3
            if partner_data.identidad_fiscal:
                receptor_attribs['NumRegIdTrib'] = partner_data.identidad_fiscal
        return receptor_attribs

    def invoice_info_conceptos(self, cr, uid, obj, context=None):
        if context is None:
            context = {}
        tax_obj = self.pool.get('account.tax')
        dp_obj = self.pool.get('decimal.precision')
        dp_account = dp_obj.precision_get(cr, uid, 'Account')
        dp_product = dp_obj.precision_get(cr, uid, 'Product Price')
        cfdi_conceptos = []
        for line in obj.invoice_line:
            ClaveProdServ = '01010101'
            concepto_attribs = {
                'ClaveProdServ': line.product_id and line.product_id.clave_prodser_id and line.product_id.clave_prodser_id.clave or ClaveProdServ,
                'NoIdentificacion': line.product_id and line.product_id.default_code or '',
                'Descripcion': line.name.replace('[', '').replace(']', '') or '',
                'Cantidad': '%s'%(round(line.quantity, dp_account)),
                'ClaveUnidad': line.uos_id and line.uos_id.clave_unidadesmedida_id and line.uos_id.clave_unidadesmedida_id.clave or '',
                'Unidad': line.uos_id and line.uos_id.name or '',
                'ValorUnitario': '%.2f'%(round(line.price_unit, dp_product)),
                'Importe': '%.2f'%( line.price_subtotal_sat ),
                'Descuento': '%.2f'%( line.price_discount_sat ),
                'Impuestos': {
                    'Traslado': [],
                    'Retenciones': []
                }
            }
            if line.numero_pedimento_sat:
                concepto_attribs['NumeroPedimento'] = line.numero_pedimento_sat
            if line.product_id.cuenta_predial:
                concepto_attribs['CuentaPredial'] = line.product_id.cuenta_predial
            
            # Calculo de Impuestos.
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price_unit, line.quantity, product=line.product_id, address_id=line.invoice_id.address_invoice_id, partner=line.invoice_id.partner_id)['taxes']
            for tax in taxes:
                tax_id = tax_obj.browse(cr, uid, tax.get('id'), context=context)
                tax_group = tax_id.tax_group_id
                importe = tax.get('amount')
                TasaOCuota = '%.6f'%(round(abs(tax_id.amount), dp_account))

                base = tax['price_unit'] * line['quantity']
                impuestos = {
                    'Base': '%.2f'%(round( base , dp_account)),
                    'Impuesto': tax_group.cfdi_impuestos,
                    'TipoFactor': '%s'%(tax_id.cfdi_tipofactor),
                    'TasaOCuota': '%s'%(TasaOCuota),
                    'Importe': '%.2f'%(round(abs(importe), dp_account))
                }
                if tax_group.cfdi_retencion:
                    concepto_attribs['Impuestos']['Retenciones'].append(impuestos)
                elif tax_group.cfdi_traslado:
                    concepto_attribs['Impuestos']['Traslado'].append(impuestos)
            cfdi_conceptos.append(concepto_attribs)
        return cfdi_conceptos

    def invoice_info_impuestos(self, cr, uid, conceptos, context=None):
        if context is None:
            context = {}
        TotalImpuestosRetenidos = 0.00
        TotalImpuestosTrasladados = 0.00
        traslado_attribs = {}
        retenciones_attribs = {}
        for concepto in conceptos:
            for impuesto in concepto['Impuestos']:
                if impuesto == 'Retenciones':
                    for ret in concepto['Impuestos'][impuesto]:
                        ret_key = '%s_%s'%(ret['Impuesto'], ret['TasaOCuota'].replace('.', '') )
                        TotalImpuestosRetenidos += float(ret['Importe'])
                        if not ret_key in retenciones_attribs.keys():
                            retenciones_attribs[ ret_key ] = {
                                'Importe': '%s'%(0.0)
                            }
                        importe = float(retenciones_attribs[ret_key]['Importe']) + float(ret['Importe'])
                        retenciones_attribs[ ret_key ] = {
                            'Impuesto': ret['Impuesto'],
                            'TipoFactor': ret['TipoFactor'],
                            'TasaOCuota': ret['TasaOCuota'],
                            'Importe': '%.2f'%(importe)
                        }
                if impuesto == 'Traslado':
                    for tras in concepto['Impuestos'][impuesto]:
                        tras_key = '%s_%s'%(tras['Impuesto'], tras['TasaOCuota'].replace('.', '') )
                        TotalImpuestosTrasladados += float(tras['Importe'])
                        if not tras_key in traslado_attribs.keys():
                            traslado_attribs[ tras_key ] = {
                                'Importe': '%s'%(0.0)
                            }
                        importe = float(traslado_attribs[tras_key]['Importe']) + float(tras['Importe'])
                        traslado_attribs[ tras_key ] = {
                            'Impuesto': tras['Impuesto'],
                            'TipoFactor': tras['TipoFactor'],
                            'TasaOCuota': tras['TasaOCuota'],
                            'Importe': '%.2f'%(importe)
                        }
        cfdi_impuestos = {
            'TotalImpuestosRetenidos': '%.2f'%(TotalImpuestosRetenidos),
            'TotalImpuestosTrasladados': '%.2f'%(TotalImpuestosTrasladados),
            'traslado_attribs': traslado_attribs,
            'retenciones_attribs': retenciones_attribs
        }
        return cfdi_impuestos

    def get_process_data(self, cr, uid, obj, res):
        attachment_obj = self.pool.get('ir.attachment')
        fname = "cfd_" + (obj.number or obj.name) + ".xml"
        attachment_values = {
            'name': fname,
            'datas': res.get('xml'),
            'datas_fname': fname,
            'description': 'Comprobante Fiscal Digital',
            'res_model': obj._name,
            'res_id': obj.id,
            'type': 'binary'
        }
        attachment_obj.create(cr, uid, attachment_values)
        # Guarda datos:
        values = {
            'cadena': res.get('cadenaori', ''),
            'fecha_timbrado': res.get('fecha'),
            'sello_sat': res.get('satSeal'),
            'certificado_sat': res.get('noCertificadoSAT'),
            'sello': res.get('SelloCFD'),
            'certificate': res.get('NoCertificado'),
            'uuid': res.get('UUID') or res.get('uuid') or '',
            'bar_code': res.get('qr_img'),
            'mensaje_pac': res.get('Leyenda'),
            'tipo_cambio': res.get('TipoCambio'),
            'cadena_sat': res.get('cadena_sat'),
            'test': res.get('test')
        }
        obj.write(values)
        return True


    def action_validate_cfdi(self, cr, uid, obj, context=None):
        if context is None:
            context = {}
        message = ''
        if not obj.tipo_comprobante:
            message += 'No se definio Tipo Comprobante\n'
        if not obj.journal_id.codigo_postal_id:
            message += 'No se definio Lugar de Expedicion (C.P.)\n'
        if not obj.payment_term:
            message += 'No se definio Condiciones de Pago\n'
        if not obj.formapago_id:
            message += 'No se definio Forma de Pago\n'
        if not obj.metodopago_id:
            message += 'No se definio Metodo de Pago\n'
        if not obj.usocfdi_id:
            message += 'No se definio Uso CFDI\n'
        regimen_id = obj.company_id.partner_id.regimen_id
        if not regimen_id:
            message += 'No se definio Regimen Fiscal para la Empresa\n'
        if not obj.partner_id.vat:
            message += 'No se especifico el RFC para el Cliente\n'
        if not obj.company_id.partner_id.vat:
            message += 'No se especifico el RFC para la Empresa\n'
        for line in obj.invoice_line:
            if not line.uos_id.clave_unidadesmedida_id.clave:
                message += 'Favor de Configurar la Clave Unidad SAT %s \n'%(line.uos_id.name)
            for tax in line.invoice_line_tax_id:
                if not tax.tax_group_id.cfdi_impuestos:
                    message += 'El impuesto %s no tiene categoria CFD \n'%()
        if message:
            raise osv.except_osv('Error !', message)
        return True

    def action_write_date_invoice_cfdi(self, cr, uid, obj, context=None):
        if context is None:
            context = {}
        dtz = False
        User = self.pool.get('res.users').browse(cr, uid, uid)
        if not obj.date_invoice_cfdi:
            tz = 'America/Monterrey' # User.context_tz
            if not tz:
                raise osv.except_osv(_('Error !'), 'El usuario no tiene definido Zona Horaria')

            hora_factura_utc = datetime.now(timezone('UTC'))
            dtz = hora_factura_utc.astimezone(timezone(tz)).strftime('%Y-%m-%d %H:%M:%S')
            dtz = dtz.replace(' ', 'T')
            cr.execute("UPDATE account_invoice SET date_invoice_cfdi='%s' WHERE id=%s "%(dtz, obj.id) )
        print 'dtz', dtz
        return dtz

AccountInvoice()