# -*- encoding: utf-8 -*-

from osv import fields, osv

#import text
class ResPartnerAddress(osv.osv):
    _inherit = "res.partner.address"
    _name = "res.partner.address"
    _columns = {
        'noInterior': fields.char('No. interior', size=64),
        'noExterior': fields.char('No. exterior', size=64),
    }

ResPartnerAddress()


class ResPartner(osv.osv):
    _description='Partner'
    _name = "res.partner"
    _inherit = "res.partner"
    _order = "name"

    _columns = {
        'xml_cfdi_sinacento': fields.boolean('XML CFDI sin acentos'),
        'identidad_fiscal': fields.char('Registro de Identidad Fiscal', size=40, help='Es requerido cuando se incluya el complemento de comercio exterior'),
        'regimen_id': fields.many2one('cfd_mx.regimen', "Regimen Fiscal"),
        'formapago_id': fields.many2one("cfd_mx.formapago", "Forma de Pago"),
        'metodopago_id': fields.many2one('cfd_mx.metodopago', u'Metodo de Pago'),
        'usocfdi_id': fields.many2one('cfd_mx.usocfdi', "Uso de Comprobante CFDI"),
        'es_extranjero': fields.boolean('Es Extranjero?'),
        'es_personafisica': fields.boolean("Es Persona Fisica?"),
        'curp': fields.char("CURP", size=20, help="Llenar en caso de que el empleador sea una persona física")
    }

ResPartner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: