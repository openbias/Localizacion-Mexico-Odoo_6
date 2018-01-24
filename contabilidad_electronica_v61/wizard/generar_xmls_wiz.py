# -*- encoding: utf-8 -*-
from osv import osv, fields
from tools.translate import _
from xml_catalogo import xml_catalogo, cadena_original as cadena_catalogo
from xml_balanza import xml_balanza, cadena_original as cadena_balanza
from xml_polizas import xml_polizas, cadena_original as cadena_polizas
from xml_aux_folios import xml_aux_folios, cadena_original as cadena_aux_folios
from xml_aux_cuentas import xml_aux_cuentas, cadena_original as cadena_aux_cuentas
import xml.etree.ElementTree as ET
import time
import base64
import os
import inspect
import codecs
import re

class wizard_poliza_line(osv.osv_memory):
    _name = 'cont_elect_wizard_poliza_line'
    
    _columns = {
        'move_id': fields.many2one('account.move', string=u"Polizas"),
        'tipo_poliza': fields.selection([
            ('1', 'Ingresos'),
            ('2', 'Egresos'),
            ('3', 'Diario')
        ], string=u"Tipo póliza"),
        'partner_id': fields.many2one('res.partner', string="Empresa"),
        'journal_id': fields.many2one('account.journal', string="Diario"),
        'date': fields.date("Fecha"),
        'parent_id': fields.many2one('cont_elect_wizard_generar_xmls', invisible=True)
    }
wizard_poliza_line()


class wizard_balanza_line(osv.osv_memory):
    _name = 'cont_elect_wizard_balanza_line'
    _rec_name = 'account_id'

    _columns = {
        'name': fields.char("Name", size=64),
        'account_id': fields.many2one('account.account', string="Cuenta"),
        'codigo': fields.char(u"Codigo", size=64),
        'saldo_inicial':fields.float('Saldo inicial'),
        'debe': fields.float("Debe"),
        'haber': fields.float("Haber"),
        'saldo_final':fields.float("Saldo final"),
        'parent_id': fields.many2one('cont_elect_wizard_generar_xmls', string="Parent", invisible=True)
    }

    _defaults = {
        'name': ' '
    }

wizard_balanza_line()


class wizard_generar_xmls(osv.osv_memory):
    _name = 'cont_elect_wizard_generar_xmls'
    _rec_name = 'company_id'

    def onchange_chart_id(self, cr, uid, ids, chart_account_id=False, context=None):
        res = {}
        if chart_account_id:
            period_obj = self.pool.get("account.period")
            list_fields = period_obj.fields_get(cr, uid, context=None)
            company_id = self.pool.get('account.account').browse(cr, uid, chart_account_id, context=context).company_id.id
            now = time.strftime('%Y-%m-%d')
            domain = [['company_id', '=', company_id]]
            res['value'] = {'company_id': company_id}
            if list_fields.get('company_id'):
                res['domain'] = {'mes': domain}
        return res


    _columns = {
        'tipo_solicitud': fields.selection([
          ('AF', 'Acto de fiscalización'),
          ('FC', 'Fiscalización Compulsa'),
          ('DE', 'Devolución'),
          ('CO', 'Compensación')
        ], string=u"Tipo de solicitud de la póliza"),
        'num_orden': fields.char(u"Numero de orden", size=64),
        'num_tramite': fields.char(u"Número de trámite", size=64),
        'tipo_envio': fields.selection([
            ('N', 'Normal'),
            ('C','Complementaria')
        ], string=u"Tipo de envio de la balanza", required=True),
        'fecha_mod_bal': fields.date(u"Ultima modificación"),
        'solo_con_codigo': fields.boolean(u"Solo cuentas con código agrupador"),
        'limite_nivel': fields.integer(u"Limite nivel"),
        'chart_account_id': fields.many2one("account.account", string="Plan contable", domain=[('parent_id','=',False)], required=True),
        'company_id': fields.many2one("res.company", string=u"Compañía", required=True),
        'mes': fields.many2one("account.period", string=u"Periodo (Mes y año)", required=True),
        'xml': fields.binary("Archivo xml"),
        'fname': fields.char("Filename", size=128),
        'csv': fields.binary("Archivo csv"),
        'fname_csv': fields.char("Filename CSV", size=128),
        'show_balanza': fields.boolean(u'Mostrar previsualizacion balanza'),
        'show_polizas': fields.boolean(u'Mostrar previsualizacion pólizas'),
        'balanza_lines': fields.one2many('cont_elect_wizard_balanza_line', 'parent_id', string=u'Previsualización Balanza'),
        'polizas_lines': fields.one2many('cont_elect_wizard_poliza_line', 'parent_id', string=u"Previsualización Polizas"),
        'message': fields.text("Mensaje Validacion")
    }
    
    _defaults = {
        'solo_con_codigo': True,
        'tipo_envio': 'N',
    }

    def validar_contabilidad_electronica(self, cr, uid, ids, context=None):
        address_obj= self.pool.get('res.partner.address')
        url="https://ceportalvalidacionprod.clouda.sat.gob.mx/"
        return {
            'type': 'ir.actions.act_url',
            'url':url,
        }

    def _get_cadena_original(self, xml_func):
        return {
            xml_catalogo: cadena_catalogo,
            xml_balanza: cadena_balanza,
            xml_polizas: cadena_polizas,
            xml_aux_folios: cadena_aux_folios,
            xml_aux_cuentas: cadena_aux_cuentas,

        }[xml_func]

    def _sellar_xml(self, cr, uid, root, xml_func, cer, context=None):
        if not context:
            context = {}
        invoice_obj = self.pool.get("account.invoice")
        tmpfiles = invoice_obj.get_temp_file_trans()

        openssl = invoice_obj.get_openssl()

        current_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        fname_xslt = current_path + '/' + context.get('xml_xslt')
        fname_xsd = current_path + '/' + context.get('xml_xsd')
        fname_cer_pem = tmpfiles.decode_and_save(cer.cer_pem)
        fname_key_pem = tmpfiles.decode_and_save(cer.key_pem)
        xml = '<?xml version="1.0" encoding="utf-8"?>' + ET.tostring(root)
        fname_xml_sinsello = tmpfiles.save(xml, 'xml_cesinsello')
        with open(fname_xml_sinsello, "w") as f:
            f.write(xml)
        fname_cadena = tmpfiles.create("cadenaori")
        os.system("xsltproc --output %s %s %s" % (fname_cadena, fname_xslt, fname_xml_sinsello))
        if context['version'] == '3.3':
            sello = openssl.sign_and_encode(fname_cadena, fname_key_pem, func="sha256")
        else:
            sello = openssl.sign_and_encode(fname_cadena, fname_key_pem)
        certificado = ''.join(open(fname_cer_pem).readlines()[1:-1])
        certificado = certificado.replace('\n', '')
        cadena = open(fname_cadena, 'rb').read()
        root.attrib.update({
            "Sello": "%s"%sello,
            "Certificado": "%s"%certificado
        })
        # Valida XML
        cfd = '<?xml version="1.0" encoding="utf-8"?>' + ET.tostring(root)
        fname_xml_sello = tmpfiles.save(cfd, 'xml_cesello')
        with open(fname_xml_sello, "w") as f:
            f.write(cfd)
        command = "xmllint --noout --schema %s %s 2>&1"%(fname_xsd, fname_xml_sello)
        out = os.popen(command).read().strip()
        message = ''
        if out and not out.endswith("validates"):
            message = u"Comprobante invalido %s\n"% out.decode("utf-8")
        tmpfiles.clean()
        return root, message


    def _save_xml(self, cr, uid, ids, data, xml_func, fname, context=None):
        if not context:
            context = {}
        for this in self.browse(cr, uid, ids):
            cer = self.pool.get("account.invoice")._get_certificate(cr, uid, [], this.company_id)
            data['noCertificado'] = cer.serial
            xml_root = xml_func(data)

            root, message = self._sellar_xml(cr, uid, xml_root, xml_func, cer, context=context)
            xml_sellado = '<?xml version="1.0" encoding="utf-8"?>' + ET.tostring(root, encoding="utf-8")
            xml_base64 = base64.encodestring(xml_sellado)
            self.write(cr, uid, [this.id], {'xml': xml_base64, 'fname': fname, 'message': message})
        return

    def _quote_and_escape(self, value):
        if type(value) != str and type(value) != unicode:
            value = str(value)
        value.replace('"', r'\"')
        return '"%s"'%(value)
        
    def _save_csv(self, cr, uid, ids, data, header, fname, context=None):
        rows = []
        for record in data:
            row = []
            for col in header:
                row.append(record.get(col, 'N/A'))
            rows.append(row)
        csv = ",".join([self._quote_and_escape(x) for x in header]) + "\n"
        for row in rows:
            csv += ",".join([self._quote_and_escape(x) for x in row]) + "\n"
        csv_base64 = base64.encodestring(csv.encode("utf-8"))
        self.write(cr, uid, ids, {'csv': csv_base64, 'fname_csv': fname})
        return 

    def _return_action(self, cr, uid, id, context=None):
        if not context:
            context = {}
        this = self.browse(cr, uid, id, context=context)
        form_next_name = context.get('form_next_name')
        return {
           'res_id': id,
           'view_type': 'form',
           'view_id' : False,
           'view_mode': 'form',
           'res_model': 'cont_elect_wizard_generar_xmls',
           'type': 'ir.actions.act_window',
           'target': 'new',
           'context': context
        }
    
    def _get_accounts(self, cr, uid, fiscalyear_id, period_id, company_id, context=None):
        return self.pool.get("account.account").search(cr, uid, [('company_id', '=', company_id)])

    def validate_rfc(self, rfc):
        vat = re.sub('[-,._  \t\n\r\f\v]','', rfc)
        return vat

    def action_xml_catalogo(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        vce = this.company_id.conta_elect_version or '1_3'
        data = {
            'mes': this.mes.name.split("/")[0],
            'ano': this.mes.fiscalyear_id.name,
            'rfc': self.validate_rfc(this.company_id.partner_id.vat),
            'cuentas': [],
            'version': vce
        }
        account_obj = self.pool.get("account.account")
        account_ids = self._get_accounts(cr, uid, this.mes.fiscalyear_id.id, this.mes.id, this.company_id.id)
        for account in account_obj.browse(cr, uid, account_ids):
            cuenta = {
                'codigo': account.code,
                'codigo_agrupador': account.codigo_agrupador and account.codigo_agrupador.name or False,
                'descripcion': account.name,
                'nivel': account.level + 1,
                'naturaleza': account.naturaleza and account.naturaleza.code or False
            }
            if account.parent_id:
                cuenta.update({'padre': account.parent_id.code})
            if (this.limite_nivel >= account.level + 1) and (not this.solo_con_codigo or account.codigo_agrupador):
                data['cuentas'].append(cuenta)

        fname = this.company_id.partner_id.vat + this.mes.fiscalyear_id.name + this.mes.name.split("/")[0] + "CT.xml"
        ctx = {
            'balanza': True,
            'version': vce,
            'xml_file': 'xml_catalogo.xml',
            'xml_xsd': 'SAT/CatalogoCuentas_%s.xsd'%(vce),
            'xml_xslt': 'SAT/CatalogoCuentas_%s.xslt'%(vce),
            'fname': fname+'.xml',
        }
        context.update(ctx)
        self._save_xml(cr, uid, [this.id], data, xml_catalogo, fname, context=context)
        csv_header = ["nivel", "padre", "naturaleza", "descripcion", "codigo", "codigo_agrupador"]
        self._save_csv(cr, uid, [this.id], data["cuentas"], csv_header, fname.replace(".xml", ".csv"))
        return self._return_action(cr, uid, this.id, context=context)


    def _balanza(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        this = self.browse(cr, uid, ids[0], context=context)
        account_obj = self.pool.get("account.account")
        ctx = context.copy()
        ctx.update({
            'company_id': this.company_id.id,
            'fiscalyear': this.mes.fiscalyear_id.id,
            'all_fiscalyear': True,
            'periods': [this.mes.id],
            'chart_account_id': this.chart_account_id.id
        })
        account_ids = self._get_accounts(cr, uid, this.mes.fiscalyear_id.id, this.mes.id, this.company_id.id)
        account_data = {}
        for account in account_obj.browse(cr, uid, account_ids, context=ctx):
            account_data[account.id] = {
                'balance': account.balance, #Esto es el debe menos el haber
                'credit': account.credit,
                'debit': account.debit,
                'code': account.code,
                'id': account.id
            }
        ctx['initial_bal'] = True
        for account in account_obj.read(cr, uid, account_ids, ["balance"], context=ctx):
            account_data[account["id"]]['initial_balance'] = account["balance"]
        lines = []
        for id, acc_data in account_data.iteritems():
            vals = {
                'saldo_inicial': acc_data['initial_balance'],
                'saldo_final': acc_data['initial_balance'] + acc_data['balance'],
                'debe': acc_data['debit'],
                'haber': acc_data['credit'],
                'account_id': acc_data['id'],
                'codigo': acc_data['code']
            }
            acc_brw = account_obj.browse(cr, uid, acc_data['id'])
            if (this.limite_nivel >= acc_brw.level + 1) and (not this.solo_con_codigo or acc_brw.codigo_agrupador):
                lines.append((0,0,vals))
        line_obj = self.pool.get("cont_elect_wizard_balanza_line")
        line_obj.unlink(cr, uid, line_obj.search(cr, uid, [('parent_id','=',this.id)]))
        self.write(cr, uid, [this.id], {'balanza_lines': lines})

    def action_previsualizar_balanza(self, cr, uid, ids, context=None):
        context = {}

        self._balanza(cr, uid, ids, context=context)
        balanza_ids = [ l.id for l in self.browse(cr, uid, ids[0]).balanza_lines ]
        self.write(cr, uid, ids, {'show_balanza': True, 'show_polizas': False, 'xml':False})
        
        context['show_balanza'] = True
        context['active_ids'] = balanza_ids
        context['ids'] = balanza_ids

        models_data = self.pool.get('ir.model.data')
        tree_view = models_data.get_object_reference(cr, uid, 'contabilidad_electronica_v61', 'wizard_generar_xmls_balanza_view_tree')
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'tree',
                'view_mode': 'tree',
                'view_id': False,
                'res_model': 'cont_elect_wizard_balanza_line',
                'domain': [('id','in',balanza_ids)],
                'name': _('Assignment Employees'),
                'views': [(tree_view and tree_view[1] or False, 'tree')],
                }

    def action_xml_balanza(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        vce = this.company_id.conta_elect_version or '1_3'
        rfc = self.validate_rfc(this.company_id.partner_id.vat)
        data = {
            'mes': this.mes.name.split("/")[0],
            'ano': this.mes.fiscalyear_id.name,
            'rfc': rfc,
            'cuentas': [],
            'tipo_envio': this.tipo_envio,
            'fecha_mod_bal': this.fecha_mod_bal,
            'version': vce
        }
        balanza_lines = this.balanza_lines
        if not this.balanza_lines:
            self._balanza(cr, uid, ids, context=context)
            balanza_lines = self.browse(cr, uid, ids[0]).balanza_lines
        for line in balanza_lines:
            cuenta = {
                'inicial': line.saldo_inicial,
                'final': line.saldo_final,
                'debe': line.debe,
                'haber': line.haber,
                'codigo': line.account_id.code,
                'descripcion': line.account_id.name
            }
            data["cuentas"].append(cuenta)
        data["cuentas"].sort(key=lambda x: x["codigo"])
        
        fname = this.company_id.partner_id.vat + this.mes.fiscalyear_id.name + this.mes.name.split("/")[0] + "B%s.xml"%this.tipo_envio
        ctx = {
            'version': vce,
            'xml_file': 'xml_balanza.xml',
            'xml_xsd': 'SAT/BalanzaComprobacion_%s.xsd'%(vce),
            'xml_xslt': 'SAT/BalanzaComprobacion_%s.xslt'%(vce),
            'fname': fname+'.xml'
        }
        context.update(ctx)
        self._save_xml(cr, uid, [this.id], data, xml_balanza, fname, context=context)
        csv_header = ['codigo', 'descripcion', 'inicial', 'debe', 'haber', 'final']
        self._save_csv(cr, uid, [this.id], data["cuentas"], csv_header, fname.replace(".xml",".csv"))
        return self._return_action(cr, uid, this.id, context=context)



    def _polizas(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        if not this.tipo_solicitud:
            raise osv.except_osv("Error", "Favor de indicar el tipo de solicitud")
        move_obj = self.pool.get("account.move")
        move_ids = move_obj.search(cr, uid, ['&', ('period_id','=',this.mes.id), ('company_id', '=', this.company_id.id)])
        lines = []
        for move in move_obj.browse(cr, uid, move_ids):
            lines.append((0,0,{
              'move_id': move.id,
              'partner_id': move.partner_id.id,
              'journal_id': move.journal_id.id,
              'tipo_poliza': move.tipo_poliza,
              'date': move.date
            }))
        line_obj = self.pool.get("cont_elect_wizard_poliza_line")
        line_obj.unlink(cr, uid, line_obj.search(cr, uid, [('parent_id','=',this.id)]))
        self.write(cr, uid, [this.id], {'polizas_lines': lines})


    def action_previsualizar_polizas(self, cr, uid, ids, context=None):
        context = {}
        self._polizas(cr, uid, ids, context=context)
        poliza_ids = [ l.id for l in self.browse(cr, uid, ids[0]).polizas_lines ]
        self.write(cr, uid, ids, {'show_balanza': False, 'show_polizas': True, 'xml':False})
        context['show_polizas'] = True
        context['active_ids'] = poliza_ids
        context['ids'] = poliza_ids
        models_data = self.pool.get('ir.model.data')
        tree_view = models_data.get_object_reference(cr, uid, 'contabilidad_electronica_v61', 'wizard_generar_xmls_polizas_view_tree')
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'tree',
                'view_mode': 'tree',
                'view_id': False,
                'res_model': 'cont_elect_wizard_poliza_line',
                'domain': [('id','in',poliza_ids)],
                'name': _('Assignment Employees'),
                'views': [(tree_view and tree_view[1] or False, 'tree')],
                }


    def _get_tipo_cambio(self, cr, uid, currency_id, fecha):
        cr.execute("SELECT rate FROM res_currency_rate WHERE currency_id = %s AND name <= '%s' ORDER BY name DESC LIMIT 1"%(currency_id.id, fecha))
        if cr.rowcount:
            rate = cr.fetchone()[0]
        else:
            raise osv.except_osv("Error", u"No hay tipo de cambio definido para %s para la fecha %s"%(currency_id.name, fecha))
        return rate


    def action_xml_polizas(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        vce = this.company_id.conta_elect_version or '1_3'
        rfc = self.validate_rfc(this.company_id.partner_id.vat)
        data = {
            'mes': this.mes.name.split("/")[0],
            'ano': this.mes.fiscalyear_id.name,
            'rfc': rfc,
            'tipo_solicitud': this.tipo_solicitud,
            'polizas': [],
            'version': vce
        }
        if this.num_orden: data['num_orden'] = this.num_orden
        if this.num_tramite: data['num_tramite'] = this.num_tramite
        polizas_lines = this.polizas_lines
        if not this.polizas_lines:
            self._polizas(cr, uid, ids, context=context)
            polizas_lines = self.browse(cr, uid, ids[0]).polizas_lines
        for line in polizas_lines:
            poliza = {
                "num": "%s-%s"%(line.move_id.tipo_poliza, line.move_id.name),
                "fecha": line.move_id.date,
                "concepto": line.move_id.ref,
                "transacciones": []
            }
            for move_line in line.move_id.line_id:
                transaccion = {
                    "num_cta": move_line.account_id.code,
                    "des_cta": move_line.account_id.name,
                    "concepto": move_line.name,
                    "debe": move_line.debit,
                    "haber": move_line.credit,
                    'cheques': [],
                    'transferencias': [],
                    'otros_metodos': [],
                    'comprobantes': [],
                    'comprobantes_cfd_cbb': [],
                    'comprobantes_ext': []
                }
                #-----------------------------------------------------------
                for cheque in move_line.cheques:
                    vals = {
                        "num": cheque.num,
                        "banco": cheque.cta_ori.bank.code_sat,
                        "cta_ori": cheque.cta_ori.acc_number,
                        "fecha": cheque.fecha,
                        "monto": cheque.monto,
                        "benef": cheque.benef.name,
                        "rfc": self.validate_rfc(cheque.benef.vat) 
                    }
                    if cheque.cta_ori.bank.extranjero:
                        vals["banco_ext"] = cheque.cta_ori.bank.name
                    if cheque.moneda:
                        vals.update({
                            "moneda": cheque.moneda.name,
                            "tip_camb": cheque.tipo_cambio
                        })
                    transaccion["cheques"].append(vals)
                #-----------------------------------------------------------
                for trans in move_line.transferencias:
                    vals = {
                        "cta_ori": trans.cta_ori.acc_number,
                        "banco_ori": trans.cta_ori.bank.code_sat,
                        "monto": trans.monto,
                        "cta_dest": trans.cta_dest.acc_number,
                        "banco_dest": trans.cta_dest.bank.code_sat,
                        "fecha": trans.fecha,
                        "benef": trans.cta_dest.partner_id.name,
                        "rfc": self.validate_rfc(trans.cta_ori.partner_id.vat if trans.move_line_id.move_id.tipo_poliza == '1' else trans.cta_dest.partner_id.vat)
                    }
                    if trans.cta_ori.bank.extranjero:
                        vals["banco_ori_ext"] = trans.cta_ori.bank.name
                    if trans.cta_dest.bank.extranjero:
                        vals["banco_dest_ext"] = trans.cta_dest.bank.name
                    if trans.moneda:
                        vals.update({
                            "moneda": trans.moneda.name,
                            "tip_camb": trans.tipo_cambio
                        })
                    transaccion["transferencias"].append(vals)
                #-----------------------------------------------------------                    
                for met in move_line.otros_metodos:
                    vals = {
                        "met_pago": met.metodo.code,
                        "fecha": met.fecha,
                        "benef": met.benef.name,
                        "rfc": self.validate_rfc(met.benef.vat),
                        "monto": met.monto
                    }
                    if met.moneda:
                        vals.update({
                            "moneda": met.moneda.name,
                            "tip_camb": met.tipo_cambio
                        })
                    transaccion["otros_metodos"].append(vals)
                #-----------------------------------------------------------                    
                for comp in move_line.comprobantes:
                    vals = {
                        "uuid": comp.uuid,
                        "monto": comp.monto,
                        "rfc": self.validate_rfc(comp.rfc)
                    }
                    if comp.moneda:
                        vals.update({
                            "moneda": comp.moneda.name,
                            "tip_camb": comp.tipo_cambio
                        })
                    transaccion["comprobantes"].append(vals)
                #-----------------------------------------------------------                    
                for comp in move_line.comprobantes_cfd_cbb:
                    vals = {
                        "folio": comp.uuid,
                        "monto": comp.monto,
                        "rfc": self.validate_rfc(comp.rfc)
                    }
                    if comp.serie:
                        vals["serie"] = this.serie
                    if comp.moneda:
                        vals.update({
                            "moneda": comp.moneda.name,
                            "tip_camb": comp.tipo_cambio
                        })
                    transaccion["comprobantes"].append(vals)
                #-----------------------------------------------------------                    
                for comp in move_line.comprobantes_ext:
                    vals = {
                        "num": comp.num,
                        "monto": comp.monto,
                    }
                    if comp.tax_id: vals["tax_id"] = comp.tax_id
                    if comp.moneda:
                        vals.update({
                            "moneda": comp.moneda.name,
                            "tip_camb": comp.tipo_cambio
                        })
                    transaccion["comprobantes"].append(vals)
                poliza["transacciones"].append(transaccion)
            data["polizas"].append(poliza)

        # fname = this.company_id.partner_id.vat + this.mes.fiscalyear_id.name + this.mes.name.split("/")[0] + "PL.xml"
        # self._save_xml(cr, uid, this.id, data, xml_polizas, fname, context=context)
        # self.write(cr, uid, this.id, {'csv': False})
        # return self._return_action(cr, uid, this.id, context=context)
        fname = this.company_id.partner_id.vat + this.mes.fiscalyear_id.name + this.mes.name.split("/")[0] + "PL.xml"
        ctx = {
            'fname': fname+'.xml',
            'version': vce,
            'xml_file': 'xml_polizas.xml',
            'xml_xsd': 'SAT/PolizasPeriodo_%s.xsd'%(vce),
            'xml_xslt': 'SAT/PolizasPeriodo_%s.xslt'%(vce),
        }
        context.update(ctx)
        self._save_xml(cr, uid, [this.id], data, xml_polizas, fname, context=context)
        return self._return_action(cr, uid, this.id, context=context)

    def action_xml_aux_folios(self, cr, uid, ids, context=None):
        curr_obj = self.pool.get("res.currency")
        model_data = self.pool.get("ir.model.data")
        code_cheque = model_data.get_object(cr, uid, "contabilidad_electronica_v61", "metodo_pago_2").code
        code_transferencia = model_data.get_object(cr, uid, "contabilidad_electronica_v61", "metodo_pago_3").code
        this = self.browse(cr, uid, ids[0])
        vce = this.company_id.conta_elect_version or '1_3'
        data = {
            'mes': this.mes.name.split("/")[0],
            'ano': this.mes.fiscalyear_id.name,
            'rfc': self.validate_rfc(this.company_id.partner_id.vat),
            'tipo_solicitud': this.tipo_solicitud,
            'detalles': [],
            'version': vce
        }
        if this.num_orden: data['num_orden'] = this.num_orden
        if this.num_tramite: data['num_tramite'] = this.num_tramite
        polizas_lines = this.polizas_lines
        if not this.polizas_lines:
            self._polizas(cr, uid, ids, context=context)
            polizas_lines = self.browse(cr, uid, ids[0]).polizas_lines
        for line in polizas_lines:
            poliza = {
                "num": "%s-%s"%(line.move_id.tipo_poliza, line.move_id.name),
                "fecha": line.move_id.date,
                "concepto": line.move_id.ref or line.move_id.name,
                "comprobantes": [],
                "comprobantes_cfd_cbb": [],
                "comprobantes_ext": []
            }
            uuids = []
            for move_line in line.move_id.line_id:
                metodo_pago = False
                if move_line.transferencias:
                    metodo_pago = code_transferencia
                elif move_line.cheques:
                    metodo_pago = code_cheque
                elif move_line.otros_metodos:
                    metodo_pago = move_line.otros_metodos[0].metodo.code
                for comp in move_line.comprobantes:
                    if comp.uuid in uuids:
                        continue
                    uuids.append(comp.uuid)
                    vals = {
                        "uuid": comp.uuid,
                        "monto": comp.monto,
                        "rfc": self.validate_rfc(comp.rfc)
                    }
                    if comp.moneda:
                        vals.update({
                            "moneda": comp.moneda.name,
                            "tip_camb": comp.tipo_cambio
                        })
                    if metodo_pago:
                        vals.update({"MetPagoAux": metodo_pago})
                    poliza["comprobantes"].append(vals)
                #-----------------------------------------------------------                    
                for comp in move_line.comprobantes_cfd_cbb:
                    vals = {
                        "folio": comp.uuid,
                        "monto": comp.monto,
                        "rfc": self.validate_rfc(comp.rfc)
                    }
                    if comp.serie:
                        vals["serie"] = comp.serie
                    if comp.moneda:
                        vals.update({
                            "moneda": comp.moneda.name,
                            "tip_camb": comp.tipo_cambio
                        })
                    if metodo_pago:
                        vals.update({"MetPagoAux": metodo_pago})
                    poliza["comprobantes_cfd_cbb"].append(vals)
                #-----------------------------------------------------------                    
                for comp in move_line.comprobantes_ext:
                    vals = {
                        "num": comp.num,
                        "monto": comp.monto,
                    }
                    if comp.tax_id: vals["tax_id"] = comp.tax_id
                    if comp.moneda:
                        vals.update({
                            "moneda": comp.moneda.name,
                            "tip_camb": comp.tipo_cambio
                        })
                    if metodo_pago:
                        vals.update({"MetPagoAux": metodo_pago})
                    poliza["comprobantes_ext"].append(vals)
            if len(poliza["comprobantes"]) > 0:
                data["detalles"].append(poliza)
        fname = this.company_id.partner_id.vat + this.mes.fiscalyear_id.name + this.mes.name.split("/")[0] + "XF.xml"
        ctx = {
            'version': vce,
            'xml_file': 'xml_aux_folios.xml',
            'xml_xsd': 'SAT/AuxiliarFolios_%s.xsd'%(vce),
            'xml_xslt': 'SAT/AuxiliarFolios_%s.xslt'%(vce),
            'fname': fname+'.xml'
        }
        context.update(ctx)
        self._save_xml(cr, uid, [this.id], data, xml_aux_folios, fname, context=context)
        self.write(cr, uid, [this.id], {'csv': False})
        return self._return_action(cr, uid, this.id, context=context)


    def action_xml_aux_cuentas(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        vce = this.company_id.conta_elect_version or '1_3'
        if not this.tipo_solicitud:
            raise osv.except_osv("Error", "Favor de indicar el tipo de solicitud")

        data = {
            'mes': this.mes.name.split("/")[0],
            'ano': this.mes.fiscalyear_id.name,
            'rfc': self.validate_rfc(this.company_id.partner_id.vat),
            'tipo_solicitud': this.tipo_solicitud,
            'cuentas': [],
            'version': vce
        }        
        if this.num_orden: data['num_orden'] = this.num_orden
        if this.num_tramite: data['num_tramite'] = this.num_tramite
        self._balanza(cr, uid, ids, context=context)
        balanza_lines = self.browse(cr, uid, ids[0]).balanza_lines
        move_line_obj = self.pool.get("account.move.line")
        for line in balanza_lines:
            cuenta = {
                'inicial': line.saldo_inicial,
                'final': line.saldo_final,
                'codigo': line.account_id.code,
                'descripcion': line.account_id.name,
                'transacciones': []
            }
            transacciones_ids = move_line_obj.search(cr, uid, [('company_id','=',this.company_id.id),
                ('account_id','=',line.account_id.id),('period_id','=',this.mes.id)])
            for t in move_line_obj.browse(cr, uid, transacciones_ids):
                cuenta["transacciones"].append({
                    'fecha': t.date, 
                    'num': "%s-%s"%(t.move_id.tipo_poliza, t.move_id.name),
                    'debe': t.debit,
                    'haber': t.credit,
                    'concepto': t.name
                })
            if len(cuenta["transacciones"]) > 0:
                data["cuentas"].append(cuenta)
        data["cuentas"].sort(key=lambda x: x["codigo"])
        fname = this.company_id.partner_id.vat + this.mes.fiscalyear_id.name + this.mes.name.split("/")[0] + "XC.xml"
        ctx = {
            'version': vce,
            'xml_file': 'xml_aux_folios.xml',
            'xml_xsd': 'SAT/AuxiliarCtas_%s.xsd'%(vce),
            'xml_xslt': 'SAT/AuxiliarCtas_%s.xslt'%(vce),
            'fname': fname+'.xml'
        }
        context.update(ctx)
        self._save_xml(cr, uid, [this.id], data, xml_aux_cuentas, fname, context=context)
        self.write(cr, uid, [this.id], {'csv': False})
        #csv_header = ['codigo', 'descripcion', 'inicial', 'debe', 'haber', 'final']
        #self._save_csv(cr, uid, this.id, data["cuentas"], csv_header, fname.replace(".xml",".csv"))
        return self._return_action(cr, uid, this.id, context=context)

wizard_generar_xmls()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: