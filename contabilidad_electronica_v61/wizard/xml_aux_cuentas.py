# -*- encoding: utf-8 -*-
import xml.etree.ElementTree as ET
from osv import osv

def xml_aux_cuentas(data):
    namespace_uri = "www.sat.gob.mx/esquemas/ContabilidadE/1_1/AuxiliarCtas"
    schemaLocation = "www.sat.gob.mx/esquemas/ContabilidadE/1_1/AuxiliarCtas http://www.sat.gob.mx/esquemas/ContabilidadE/1_1/AuxiliarCtas/AuxiliarCtas_1_1.xsd"
    version = "1.1"
    if data.get('version') == '1_3':
            namespace_uri = "http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/AuxiliarCtas"
            schemaLocation = "http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/AuxiliarCtas http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/AuxiliarCtas/AuxiliarCtas_1_3.xsd"
            version = "1.3"

    namespace_prefix = "AuxiliarCtas"
    ET.register_namespace(namespace_prefix, namespace_uri)
    ns = namespace_prefix + ":"
    root = ET.Element(ns+"AuxiliarCtas", {
        'xsi:schemaLocation': schemaLocation,
        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'xmlns:' + namespace_prefix: namespace_uri,
        'Version': version,
        'RFC': "%s"%data["rfc"],
        'Mes': "%s"%data["mes"],
        'Anio': "%s"%data["ano"],
        'TipoSolicitud': "%s"%data["tipo_solicitud"],
        'noCertificado': "%s"%data["noCertificado"]
    })
    if data.get('num_orden',False):
        root.attrib["NumOrden"] = "%s"%data['num_orden']
    if data.get('num_tramite', False):
        root.attrib["NumTramite"] = "%s"%data['num_tramite']
    for cuenta in data["cuentas"]:
        attribs = {
            "NumCta": "%s"%cuenta["codigo"],
            "DesCta": "%s"%cuenta["descripcion"],
            "SaldoIni": "%.2f"%cuenta["inicial"],
            "SaldoFin": "%.2f"%cuenta["final"]
        }
        nodo_cuenta = ET.SubElement(root, ns+"Cuenta", attribs)
        for transaccion in cuenta["transacciones"]:
            nodo_transaccion = ET.SubElement(nodo_cuenta, ns+"DetalleAux", {
                "NumUnIdenPol": "%s"%transaccion["num"],
                "Fecha": "%s"%transaccion["fecha"],
                "Concepto": "%s"%transaccion["concepto"],
                "Debe": "%s"%transaccion["debe"],
                "Haber": "%s"%transaccion["haber"]
            })

    return root

def cadena_original(xml):

    def normalizar_espacios(valor):
        return " ".join(valor.split())

    def requerido(valor):
        return "|" + normalizar_espacios(valor)

    def opcional(valor):
        return "|" + normalizar_espacios(valor) if valor else ""

    root = ET.fromstring(xml)
    atributos = [
        ('Version', requerido),
        ('RFC', requerido),
        ('Mes', requerido),
        ('Anio', requerido),
        ('TipoSolicitud', requerido),
        ('NumOrden', opcional),
        ('NumTramite', opcional),
    ]
    atributos_cuentas = [
        ('NumCta', requerido),
        ('DesCta', requerido),
        ('SaldoIni', requerido),
        ('SaldoFin', requerido)
    ]
    atributos_transaccions = [
        ('Fecha', requerido),
        ("NumUnIdenPol", requerido),
        ("Debe", requerido),
        ("Haber", requerido)
    ]

    cadena = ["|"]

    def procesar(nodo, atributos, cadena):
        for a,f in atributos:
            valor = nodo.attrib.get(a, False)
            if f == requerido and valor == False:
                raise osv.except_osv("Error", u"Atributo requerido '%s' ausente en el nodo: %s"%(a,nodo.attrib))
            cadena[0] += f(valor)

    procesar(root, atributos, cadena)
    for nodo_cta in root:
        procesar(nodo_cta, atributos_cuentas, cadena)
        for nodo_pol in nodo_cta:
            procesar(nodo_pol, atributos_transaccions, cadena)

    return cadena[0] + "||"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: