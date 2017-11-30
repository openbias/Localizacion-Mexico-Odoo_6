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
    'name' : 'Subir y Validar XML de las Facturas de Proveedor',
    'version' : '1.0',
    'author' : 'Zenpar',
    'website' : 'http://www.zeval.com.mx',
    'category' : '',
    'depends' : ['purchase', 'account'],
    'description': """
Wizard para subir el xml y pdf de las facturas de proveedor. Se valida en hacienda y
se comparan las partidas de la OC con los nodos del xml. Si todo está bien, se adjuntan los archivos
a la factura.

También se puede validar contra una remisión de entrada en vez de contra la OC

También valida que el tipo de cambio, en caso de que la moneda del XML y la moneda de la OC no sean la
misma, no sea mayor que el dado de alta para esa fecha.
NOTA: Para que esta validación funcione, no importa si la moneda base es el dolar o el peso. Sin embargo aunque 
la moneda base sea el dólar, se asumirá que todos los tipos de cambio de las demás monedas están con relación al peso.
    """,
    'init_xml':[
        # 'res.groups.csv',
        # 'ir.rule.csv',
        # 'ir.model.access.csv'
    ],
    'data': [
        'wizard/subir_view.xml',
        # 'wizard/subir_simple_view.xml',
        'wizard/crear_fact_view.xml',
        'wizard/subir_fac_view.xml',
        'views/purchase_view.xml',
        'views/res_users_view.xml',
        'views/config_view.xml',
        'views/invoice_view.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'images': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

