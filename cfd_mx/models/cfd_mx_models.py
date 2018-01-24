# -*- encoding: utf-8 -*-

import openerp
from osv import fields, osv

import json, os, inspect
import logging
logging.basicConfig(level=logging.INFO)

class AltaCatalogosCFDI(osv.osv_memory):
    _name = 'cfd_mx.alta.catalogos.wizard'
    _description = 'Alta Catalogos CFDI'


    def action_alta_catalogos(self, cr, uid, ids, context=None):
        logging.info(' Inicia Alta Catalogos')
        models = [
            'cfd_mx.unidadesmedida',
            'cfd_mx.prodserv',
            'res.country.state.municipio',
            'res.country.state.ciudad',
            'res.country.state.cp'
        ]
        for model in models:
            model_name = model.replace('.', '_')
            logging.info(' Model: -- %s'%model_name )
            model_obj = self.pool.get(model)
            fname = '/../data/json/%s.json' % model
            current_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))        
            path =  current_path+fname
            jdatas = json.load(open(path))
            for indx, data in enumerate(jdatas):
                header = data.keys()
                body = data.values()
                try:
                    result, rows, warning_msg, dummy = model_obj.import_data(cr, uid, header, [body], mode='update', current_module='cfd_mx', noupdate=True, context=context)
                    logging.info(' Model: -- %s, Res: %s - %s'%(model_name, indx, result) )
                    if result < 0:
                        logging.info(' Model: -- %s, Res: %s - %s'%(model_name, indx, warning_msg) )
                    cr.commit()
                except:
                    pass
        return {}


AltaCatalogosCFDI()


class ResBank(osv.osv):
    _inherit = "res.bank"
    
    _columns = {
        'code_sat': fields.char("Codigo SAT", size=10, required=False),
        'razon_social': fields.char("Razon social", size=24),
        'extranjero': fields.boolean("Banco extranjero")
    }

class ResCountry(osv.osv):
    _inherit = "res.country" 

    _columns = {
        'code_alpha3': fields.char("Codigo (alpha3)", size=64)
    }

class CodigoPostal(osv.osv):
    _name = "res.country.state.cp"

    _columns = {
        'name': fields.char("Codigo Postal", size=128),
        'state_id': fields.many2one('res.country.state', string='Estado'),
        'ciudad_id': fields.many2one('res.country.state.ciudad', string='Localidad'),
        'municipio_id': fields.many2one('res.country.state.municipio', string='Municipio')
    }

class Ciudad(osv.osv):
    _name = 'res.country.state.ciudad'
    
    _columns = {
        'state_id': fields.many2one('res.country.state', string='Estado', required=True),
        'name': fields.char(string='Name', size=256, required=True),
        'clave_sat': fields.char("Clave SAT", size=10),
    }

class Municipio(osv.osv):
    _name = 'res.country.state.municipio'
    
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'state_id': fields.many2one('res.country.state', string='Estado', required=True),
        'clave_sat': fields.char("Clave SAT", size=10),
    }

class Colonia(osv.osv):
    _name = 'res.country.state.municipio.colonia'
    
    _columns = {
        'municipio_id': fields.many2one('res.country.state.municipio', 'Municipio', required=True),
        'name': fields.char('Name', size=256, required=True),
        'cp': fields.char('Código Postal', size=10),
    }


ResBank()
ResCountry()
CodigoPostal()
Ciudad()
Municipio()
Colonia()

# 
# Catalogos CFDI
#

class TipoRelacion(osv.osv):
    _name = "cfd_mx.tiporelacion"

    _columns = {
        'name': fields.char('Descripcion', size=128),
        'clave': fields.char('Clave', help='Clave del Catálogo del SAT', size=8),
    }

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        return [(r['id'], ("[%s] %s" % (r['clave'], r['name']) )) for r in self.read(cr, uid, ids, ['clave', 'name'], context, load='_classic_write')]

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, user, [('clave','=', name)] + args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)


class UsoCfdi(osv.osv):
    _name = "cfd_mx.usocfdi"

    _columns = {
        'name': fields.char('Descripcion', size=128),
        'clave': fields.char('Clave', help='Clave del Catálogo del SAT', size=8),
    }

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        return [(r['id'], ("[%s] %s" % (r['clave'], r['name']) )) for r in self.read(cr, uid, ids, ['clave', 'name'], context, load='_classic_write')]

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, user, [('clave','=', name)] + args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)

class ClaveProdServ(osv.osv):
    _name = "cfd_mx.prodserv"

    _columns = {
        'name': fields.char('Descripcion', size=128),
        'clave': fields.char('Clave', help='Clave del Catálogo del SAT', size=8),
        'incluir_iva': fields.char(string='Incluir IVA trasladado', size=64),
        'incluir_ieps': fields.char(string='Incluir IVA trasladado', size=64),
        'complemento': fields.char("Complemento Incluir", size=64),
        'from_date': fields.date(string='Fecha Inicial'),
        'to_date': fields.date(string='Fecha Inicial'),
        'similares': fields.char("Palabras Similares", size=64),
    }

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        return [(r['id'], ("[%s] %s" % (r['clave'], r['name']) )) for r in self.read(cr, uid, ids, ['clave', 'name'], context, load='_classic_write')]

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, user, [('clave','=', name)] + args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)

class UnidadesMedida(osv.osv):
    _name = "cfd_mx.unidadesmedida"

    _columns = {
        'name': fields.char('Descripcion', size=128),
        'clave': fields.char('Clave', help='Clave del Catálogo del SAT', size=8),
        'from_date': fields.date("Fecha Inicial"),
        'to_date': fields.date("Fecha Final"),
        'descripcion': fields.char("Descripcion", required=False, size=254),
        'nota': fields.char("Nota", size=254),
        'simbolo': fields.char("Simbolo", size=254)
    }

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        return [(r['id'], ("[%s] %s" % (r['clave'], r['name']) )) for r in self.read(cr, uid, ids, ['clave', 'name'], context, load='_classic_write')]

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, user, [('clave','=', name)] + args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)


class FormaPago(osv.osv):
    _name = "cfd_mx.formapago"

    _columns = {
        'name': fields.char('Descripcion', size=128),
        'clave': fields.char('Clave', help='Clave del Catálogo del SAT', size=8),
        'banco': fields.boolean('Banco', help="Activar este checkbox para que pregunte número de cuenta"),
        'no_operacion': fields.boolean('Num. Operacion'),
        'rfc_ordenante': fields.boolean('RFC Ordenante'),
        'cuenta_ordenante': fields.boolean('Cuenta Ordenante'),
        'patron_ordenante': fields.char('Descripcion', size=64),
        'rfc_beneficiario': fields.boolean('RFC Beneficiario'),
        'cuenta_beneficiario': fields.boolean('Cuenta Beneficiario'),
        'patron_beneficiario': fields.char('Patron Beneficiario', size=64),
        'tipo_cadena': fields.boolean('Tipo Cadena'),
    }

    _defaults = {
        'no_operacion': False,
        'rfc_ordenante': False,
        'cuenta_ordenante': False,
    }

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        return [(r['id'], ("[%s] %s" % (r['clave'], r['name']) )) for r in self.read(cr, uid, ids, ['clave', 'name'], context, load='_classic_write')]

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, user, [('clave','=', name)] + args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)


class MetodoPago(osv.osv):
    _name = "cfd_mx.metodopago"

    _columns = {
        'name': fields.char('Descripcion', size=128),
        'clave': fields.char('Clave', help='Clave del Catálogo del SAT', size=8),
    }

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        return [(r['id'], ("[%s] %s" % (r['clave'], r['name']) )) for r in self.read(cr, uid, ids, ['clave', 'name'], context, load='_classic_write')]

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, user, [('clave','=', name)] + args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)

class Regimen(osv.osv):
    _name = "cfd_mx.regimen"

    _columns = {
        'name': fields.char('Descripcion', size=128),
        'clave': fields.char('Clave', help='Clave del Catálogo del SAT', size=8),
        'persona_fisica': fields.boolean('Persona Fisica'),
        'persona_moral': fields.boolean('Persona Moral'),
    }

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        return [(r['id'], ("[%s] %s" % (r['clave'], r['name']) )) for r in self.read(cr, uid, ids, ['clave', 'name'], context, load='_classic_write')]

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, user, [('clave','=', name)] + args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)


class Aduana(osv.osv):
    _name = "cfd_mx.aduana"

    _columns = {
        'name': fields.char('Descripcion', size=128),
        'clave': fields.char('Clave', help='Clave del Catálogo del SAT', size=8),
        'date_from': fields.date('Fecha Inicio'),
        'date_to': fields.date('Fecha Final'),
    }

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        return [(r['id'], ("[%s] %s" % (r['clave'], r['name']) )) for r in self.read(cr, uid, ids, ['clave', 'name'], context, load='_classic_write')]

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, user, [('clave','=', name)] + args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)

class Addendas(osv.osv):
    _name = "cfd_mx.conf_addenda"




TipoRelacion()
UsoCfdi()
ClaveProdServ()
UnidadesMedida()
FormaPago()
FormaPago()
Regimen()
Aduana()
Addendas()