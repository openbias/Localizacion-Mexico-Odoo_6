# -*- encoding: utf-8 -*-

from osv import fields, osv

#Productos
class ProductProduct(osv.osv):
    _inherit = 'product.product'

    _columns = {
        'cuenta_predial': fields.char("Cuenta Predial", size=64, help="Numero de Cuenta Predial"),
        'clave_prodser_id': fields.many2one("cfd_mx.prodserv", 'Clave SAT')
    }

class ProductUOM(osv.osv):
    _inherit = 'product.uom'

    _columns = {
        'clave_unidadesmedida_id': fields.many2one("cfd_mx.unidadesmedida", 'Clave SAT')
    }



ProductProduct()
ProductUOM()