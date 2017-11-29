# -*- encoding: utf-8 -*-

from osv import fields, osv


class AccountJournal(osv.osv):
    _inherit = 'account.journal'

    _columns = {
        'serie': fields.char('Serie', size=32),
        'codigo_postal_id': fields.many2one('res.country.state.cp', "C.P. Catálogo SAT")
    }


class AccountTax(osv.osv):
    _inherit = 'account.tax'

    _columns = {
        'tax_group_id': fields.many2one('account.tax.group', "Grupo SAT"),
        'cfdi_tipofactor': fields.selection([
                ('Tasa', 'Tasa'),
                ('Cuota', 'Cuota'),
                ('Exento', 'Exento')],
            "CFDI Tipo Factor")
    }

    _defaults = {
        "cfdi_tipofactor": "Tasa"
    }

class AccountTaxGroup(osv.osv):
    _name = 'account.tax.group'

    _columns = {
        'sequence': fields.integer('Sequence', required=True),
        'name': fields.char('Description', size=64, select=True),
        'cfdi_traslado': fields.boolean("Traslado ?"),
        'cfdi_retencion': fields.boolean("Retencion ?"),
        'cfdi_impuestos': fields.selection([
                ('001', 'ISR'),
                ('002', 'IVA'),
                ('003', 'IEPS')],
            "CFDI Catalogo de Impuestos")
    }

    _defaults = {
        "cfdi_impuestos": "002",
        'sequence': 5,
    }

class ResCurrency(osv.osv):
    _inherit = 'res.currency'

    _columns = {
        'nombre_largo': fields.char("Nombre largo", size=256, 
        help="Ejemplo: dólares americanos, francos suizos")
    }


AccountJournal()
AccountTax()
AccountTaxGroup()
ResCurrency()