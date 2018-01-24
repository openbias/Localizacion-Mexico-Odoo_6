# -*- encoding: utf-8 -*-

from osv import fields, osv

class ResBank(osv.osv):
    _inherit = 'res.bank'

    _columns = {
        'description': fields.char("Nombre o razon social", size=64)
    }

class ResCompany(osv.osv):
    _inherit = 'res.company'

    _columns = {
        'cfd_mx_host': fields.char("URL Stamp", size=256),
        'cfd_mx_port': fields.char("Port Stamp", size=256),
        'cfd_mx_db': fields.char("DB Stamp", size=256),
        'cfd_mx_test': fields.boolean('Timbrar Prueba'),
        'cfd_mx_pac': fields.selection([('finkok', 'Finkok')], "PAC"),
        'cfd_mx_version': fields.selection([('3.3', 'CFDI 3.3'),], 'Versión'),
        'cfd_mx_journal_ids': fields.many2many('account.journal', 'res_company_journal_cfdi', 'company_id', 'journal_id', 'Diarios'),

    }

    _defaults = {
        'cfd_mx_test': True,
        'cfd_mx_pac': 'finkok',
        'cfd_mx_version': '3.3',

    }



ResBank()
ResCompany()