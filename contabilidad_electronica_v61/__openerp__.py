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

{
    'name': 'Contabilidad Electronica SAT',
    'version': '1.2',
    'category': 'Contabilidad Electronica',
    "sequence": 14,
    'complexity': "easy",
    'description': """
Contabilidad Electronica.
======================================================

    """,
    'author': 'OpenBias',
    'website': 'http://www.bias.com.mx',
    'images': [],
    'depends': ['account', 'validar_factura'],
    'init_xml': [
        'security/ir.model.access.csv',
        'data/contabilidad_electronica_naturaleza.csv',
        'data/contabilidad_electronica_codigo_agrupador.csv',
        'data/contabilidad.electronica.metodo.pago.csv',
        'data/res.bank.csv'
    ],
    'update_xml': [
        'views/catalogos_view.xml',
        'views/account_view.xml',
        'views/certificate_view.xml',
        'views/account_bank_statement_view.xml',
        'views/account_voucher_view.xml',
        'wizard/llenar_uuid_view.xml',
        'wizard/generar_xmls_wiz_view.xml',


    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: