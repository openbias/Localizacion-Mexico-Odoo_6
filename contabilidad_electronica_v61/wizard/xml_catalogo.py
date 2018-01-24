# -*- encoding: utf-8 -*-
import xml.etree.ElementTree as ET
from osv import osv

def xml_catalogo(data):
    namespace_uri = "www.sat.gob.mx/esquemas/ContabilidadE/1_1/CatalogoCuentas"
    schemaLocation = "www.sat.gob.mx/esquemas/ContabilidadE/1_1/CatalogoCuentas http://www.sat.gob.mx/esquemas/ContabilidadE/1_1/CatalogoCuentas/CatalogoCuentas_1_1.xsd"
    version = "1.1"
    if data.get('version') == '1_3':
            namespace_uri = "http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/CatalogoCuentas"
            schemaLocation = "http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/CatalogoCuentas http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/CatalogoCuentas/CatalogoCuentas_1_3.xsd"
            version = "1.3"

    namespace_prefix = "catalogocuentas"
    ET.register_namespace(namespace_prefix, namespace_uri)
    ns = namespace_prefix + ":"
    root = ET.Element(ns+"Catalogo", {
        'xsi:schemaLocation': schemaLocation,
        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'xmlns:' + namespace_prefix: namespace_uri,
        'Version': version,
        'RFC': "%s"%data["rfc"],
        'Mes': "%s"%data["mes"],
        'Anio': "%s"%data["ano"],
        'noCertificado': "%s"%data["noCertificado"]
    })
    for cuenta in data["cuentas"]:
        attribs = {
            "CodAgrup": "%s"%cuenta["codigo_agrupador"],
            "NumCta": "%s"%cuenta["codigo"],
            "Desc": "%s"%cuenta["descripcion"],
            "Nivel": "%s"%cuenta["nivel"],
            "Natur": "%s"%cuenta["naturaleza"]
        }
        if "padre" in cuenta and cuenta["padre"]:
            attribs.update({"SubCtaDe": "%s"%cuenta["padre"]})
        ET.SubElement(root, ns+"Ctas", attribs)

    return root

def cadena_original(xml):

    def normalizar_espacios(valor):
        return " ".join(valor.split())

    def requerido(valor):
        return "|" + normalizar_espacios(valor)
        
    def opcional(valor):
        return "|" + normalizar_espacios(valor) if valor else ""
        
    root = ET.fromstring(xml)    
    atributos_catalogo = [
        ('Version', requerido),
        ('RFC', requerido),
        ('Mes', requerido),
        ('Anio', requerido)
    ]
    atributos_cuentas = [
        ('CodAgrup', requerido),
        ('NumCta', requerido),
        ('Desc', requerido),
        ('SubCtaDe', opcional),
        ('Nivel', requerido),
        ('Natur', requerido)
    ]
    
    cadena = ["|"]
    
    def procesar(nodo, atributos, cadena):
        for a,f in atributos:
            valor = nodo.attrib.get(a, False)
            if f == requerido and valor == False:
                raise osv.except_osv("Error", u"Atributo requerido '%s' ausente en el nodo: %s"%(a,nodo.attrib))
            cadena[0] += f(valor)
            
    procesar(root, atributos_catalogo, cadena)
    for nodo in root:
        procesar(nodo, atributos_cuentas, cadena)
            
    return cadena[0] + "||"
    
if __name__ == '__main__':
    import sys
    xml = open(sys.argv[1]).read()
    print cadena_original(xml)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: