# -*- encoding: utf-8 -*-
import xml.etree.ElementTree as ET
from osv import osv

def xml_balanza(data):
    namespace_uri = "www.sat.gob.mx/esquemas/ContabilidadE/1_1/BalanzaComprobacion"
    schemaLocation = "www.sat.gob.mx/esquemas/ContabilidadE/1_1/BalanzaComprobacion http://www.sat.gob.mx/esquemas/ContabilidadE/1_1/BalanzaComprobacion/BalanzaComprobacion_1_1.xsd"
    version = "1.1"
    if data.get('version') == '1_3':
            namespace_uri = "http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/BalanzaComprobacion"
            schemaLocation = "http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/BalanzaComprobacion http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/BalanzaComprobacion/BalanzaComprobacion_1_3.xsd"
            version = "1.3"

    namespace_prefix = "BCE"
    ET.register_namespace(namespace_prefix, namespace_uri)
    ns = namespace_prefix + ":"
    root = ET.Element(ns+"Balanza", {
        'xsi:schemaLocation': schemaLocation,
        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'xmlns:' + namespace_prefix: namespace_uri,
        'Version': version,
        'RFC': "%s"%data["rfc"],
        'Mes': "%s"%data["mes"],
        'Anio': "%s"%data["ano"],
        'TipoEnvio': "%s"%data["tipo_envio"],
        'noCertificado': "%s"%data["noCertificado"]
    })
    if data.get("fecha_mod_bal", False):
        root.attrib['FechaModBal'] = "%s"%data["fecha_mod_bal"]
    for cuenta in data["cuentas"]:
        attribs = {
            "NumCta": "%s"%cuenta["codigo"],
            "SaldoIni": "%.2f"%cuenta["inicial"],
            "Debe": "%.2f"%cuenta["debe"],
            "Haber": "%.2f"%cuenta["haber"],
            "SaldoFin": "%.2f"%cuenta["final"]
        }
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
    atributos_balanza = [
        ('Version', requerido),
        ('RFC', requerido),
        ('Mes', requerido),
        ('Anio', requerido),
        ('TipoEnvio', requerido),
        ('FechaModBal', opcional)
    ]
    atributos_cuentas = [
        ('NumCta', requerido),
        ('SaldoIni', requerido),
        ('Debe', opcional),
        ('Haber', requerido),
        ('SaldoFin', requerido)
    ]

    cadena = ["|"]

    def procesar(nodo, atributos, cadena):
        for a,f in atributos:
            valor = nodo.attrib.get(a, False)
            if f == requerido and valor == False:
                raise osv.except_osv("Error", u"Atributo requerido '%s' ausente en el nodo: %s"%(a,nodo.attrib))
            cadena[0] += f(valor)

    procesar(root, atributos_balanza, cadena)
    for nodo in root:
        procesar(nodo, atributos_cuentas, cadena)

    return cadena[0] + "||"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: